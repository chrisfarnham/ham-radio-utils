#! /usr/bin/env python3
"""Build an ADIF log from a JSON description of a POTA activation.

Written for the paper-log-to-ADIF workflow: transcribe a log page into JSON,
then generate the .adi deterministically so every field length prefix is
correct by construction.

    ./build-adif.py session.json -o "Park-Name---US-1234,-June-18,-2026.adi"

The JSON looks like:

    {
      "date": "20260618",
      "freq": "14.041",
      "park": "US-8399",
      "my_gridsquare": "FN42kj",
      "operator": "W1YTQ",
      "qsos": [
        {"time": "1502", "call": "WA4NKL"},
        {"time": "1505", "call": "VE3CMI", "state": "ON",
         "country": "CANADA", "dxcc": "1"}
      ]
    }

Only date, freq, park and qsos are required; the rest have defaults below.
BAND is derived from FREQ. Per-QSO keys (name, qth, state, cnty, country,
gridsquare, dxcc, comment) are optional -- leave out anything the paper log
did not record and let enrich-adif.py fill it from QRZ.
"""

import argparse
import json
import sys
import time

DEFAULTS = {
    "operator": "W1YTQ",
    "my_state": "MA",
    "mode": "CW",
    "tx_pwr": "20",
    "rst_sent": "599",
    "rst_rcvd": "599",
    "country": "UNITED STATES OF AMERICA",
    "dxcc": "291",
    "programid": "HAMRS",
    "programversion": "2.51.0",
    "adif_ver": "3.1.6",
}

# (low MHz, high MHz, band) -- HF through 70cm
BAND_PLAN = [
    (1.8, 2.0, "160m"), (3.5, 4.0, "80m"), (5.3, 5.4, "60m"),
    (7.0, 7.3, "40m"), (10.1, 10.15, "30m"), (14.0, 14.35, "20m"),
    (18.068, 18.168, "17m"), (21.0, 21.45, "15m"), (24.89, 24.99, "12m"),
    (28.0, 29.7, "10m"), (50.0, 54.0, "6m"), (144.0, 148.0, "2m"),
    (222.0, 225.0, "1.25m"), (420.0, 450.0, "70cm"),
]

# Order matters: this is the field order HAMRS emits, and matching it keeps
# diffs against previously exported logs readable.
QSO_FIELD_ORDER = [
    "NAME", "QTH", "STATE", "CNTY", "COUNTRY", "GRIDSQUARE", "DXCC", "COMMENT",
]


def band_for(freq):
    try:
        mhz = float(freq)
    except ValueError:
        sys.exit("freq %r is not a number" % freq)
    for low, high, band in BAND_PLAN:
        if low <= mhz <= high:
            return band
    sys.exit("freq %s MHz does not fall in a known band" % freq)


def adif(tag, val):
    val = str(val)
    return "<%s:%d>%s" % (tag, len(val), val)


def build(session):
    cfg = dict(DEFAULTS)
    cfg.update({k: v for k, v in session.items() if k != "qsos"})

    for required in ("date", "freq", "park", "qsos"):
        if not session.get(required):
            sys.exit("session JSON is missing required key %r" % required)

    freq = str(cfg["freq"])
    band = cfg.get("band") or band_for(freq)
    park = cfg["park"]

    out = [
        adif("ADIF_VER", cfg["adif_ver"]),
        adif("CREATED_TIMESTAMP", time.strftime("%Y%m%d %H%M%S")),
        adif("PROGRAMID", cfg["programid"]),
        adif("PROGRAMVERSION", cfg["programversion"]),
        "<EOH>",
        "",
    ]

    for q in session["qsos"]:
        if not q.get("call"):
            sys.exit("a QSO entry has no call: %r" % q)
        if not q.get("time"):
            # A call with no time is an unresolved fragment, not a contact.
            sys.exit("QSO %s has no time; drop it or supply one" % q["call"])

        t = str(q["time"])
        t = t + "00" if len(t) == 4 else t

        rec = [
            adif("RST_RCVD", q.get("rst_rcvd", cfg["rst_rcvd"])),
            adif("RST_SENT", q.get("rst_sent", cfg["rst_sent"])),
            adif("CALL", q["call"].upper()),
            adif("OPERATOR", cfg["operator"]),
            adif("FREQ", q.get("freq", freq)),
            adif("BAND", band_for(q["freq"]) if q.get("freq") else band),
            adif("MY_POTA_REF", park),
            adif("MY_GRIDSQUARE", cfg["my_gridsquare"]),
            adif("MODE", q.get("mode", cfg["mode"])),
            adif("TX_PWR", q.get("tx_pwr", cfg["tx_pwr"])),
            adif("MY_STATE", cfg["my_state"]),
            adif("TIME_ON", t),
            adif("QSO_DATE", cfg["date"]),
        ]

        for tag in QSO_FIELD_ORDER:
            val = q.get(tag.lower())
            if tag == "COUNTRY" and not val:
                val = cfg["country"]
            if tag == "DXCC" and not val:
                val = cfg["dxcc"]
            if val:
                rec.append(adif(tag, val))

        # Park-to-park: the other station was also activating. On the paper log
        # this shows up as a POTA reference in the state column instead of a
        # state. SIG/SIG_INFO describe *their* park; MY_SIG/MY_SIG_INFO ours.
        # A station activating several parks at once (an N-fer) is a list, which
        # SIG_INFO carries comma-separated: "US-0161,US-3791".
        their_park = q.get("their_park")
        if isinstance(their_park, list):
            their_park = ",".join(their_park)
        if their_park:
            rec.append(adif("SIG", "POTA"))
            rec.append(adif("SIG_INFO", their_park))

        rec.append(adif("MY_SIG", "POTA"))
        rec.append(adif("MY_SIG_INFO", park))
        rec.append("<EOR>")
        out.extend(rec)
        out.append("")

    return "\n".join(out).rstrip("\n") + "\n"


def main():
    ap = argparse.ArgumentParser(__file__, description="Build an ADIF log from session JSON")
    ap.add_argument("session", help="JSON file describing the activation")
    ap.add_argument("-o", "--output", required=True, help="ADIF file to write")
    args = ap.parse_args()

    with open(args.session) as f:
        session = json.load(f)

    text = build(session)
    with open(args.output, "w", encoding="ISO-8859-1", errors="replace") as f:
        f.write(text)

    print("wrote %s (%d QSOs)" % (args.output, len(session["qsos"])))


if __name__ == "__main__":
    main()
