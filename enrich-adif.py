#! /usr/bin/env python3
"""Enrich an ADIF file with callsign data from the QRZ.com XML API.

Fills only fields that are MISSING from a record. Never overwrites a value that
is already present -- instead it reports the disagreement, so deliberate
overrides (e.g. a state taken from the paper log rather than the database)
survive enrichment and conflicts stay visible.

Usage:
    ./enrich-adif.py <file.adi> [--apply]

Without --apply it runs as a dry run and only prints what would change.

Auth: the QRZ XML service trades a username+password login for a session key.
Session keys have no guaranteed lifetime (QRZ's own spec), so this logs in
fresh at the start of every run rather than relying on a cached key. Put
credentials in .env (gitignored) as:

    qrz_username=...   # your QRZ.com callsign, not an email address
    qrz_password=...

Requires an active QRZ XML subscription; without one the API returns a reduced
field set. Protocol reference: docs/qrz-xml-interface-spec.md
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

QRZ_URL = "https://xmldata.qrz.com/xml/current/"
QRZ_NS = "{http://xmldata.qrz.com}"
AGENT = "ham-radio-utils/0.1"

# POTA's public park API. When a QSO records the other station's park
# (SIG_INFO), the park is where they actually were, so its grid beats anything
# derived from their QRZ home address -- which is why this pass is allowed to
# overwrite GRIDSQUARE where the QRZ pass never overwrites anything.
POTA_URL = "https://api.pota.app/park/%s"
PARK_CACHE_FILE = ".pota-cache.json"

# QRZ counts every lookup against the account, and the documented workflow is a
# dry run followed by --apply. Caching keeps that from costing two lookups per
# callsign.
CACHE_FILE = ".qrz-cache.json"

FIELD_RE = re.compile(r"<(\w+):(\d+)(?::[A-Za-z])?>([^<\n]*)")

# ADIF field <- QRZ JSON key
ENRICH_FIELDS = ["NAME", "QTH", "STATE", "CNTY", "COUNTRY", "GRIDSQUARE", "DXCC"]

# Fields that describe *where the operator was*. QRZ returns a home address, so
# when the logged STATE disagrees with QRZ's, the station was operating away
# from home and QRZ's location is simply the wrong place -- importing it would
# put a foreign city and grid on the QSO. Grid in particular drives distance
# and awards math, so these are suppressed rather than guessed at.
LOCATION_FIELDS = {"QTH", "CNTY", "GRIDSQUARE"}


def adif(tag, val):
    return "<%s:%d>%s" % (tag, len(val), val)


def parse_records(text):
    """Split into (header, [record_text, ...]) preserving the original text."""
    head, _, body = text.partition("<EOH>")
    parts = re.split(r"(<EOR>)", body, flags=re.IGNORECASE)
    records = []
    for i in range(0, len(parts) - 1, 2):
        records.append(parts[i] + parts[i + 1])
    trailing = parts[-1] if len(parts) % 2 else ""
    return head + "<EOH>", records, trailing


def fields_of(record):
    return {m.group(1).upper(): m.group(3) for m in FIELD_RE.finditer(record)}


def load_env(path=".env"):
    """Read simple KEY=value lines into os.environ without overriding real ones."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.replace("export ", "").strip()
            os.environ.setdefault(key, val.strip().strip('"').strip("'"))


def strip_ns(tag):
    return tag[len(QRZ_NS):] if tag.startswith(QRZ_NS) else tag


def qrz_login(username, password):
    """Trade username+password for a session key. Returns the key or exits."""
    url = QRZ_URL + "?" + urllib.parse.urlencode(
        {"username": username, "password": password, "agent": AGENT}
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        root = ET.fromstring(resp.read())

    session = {}
    for child in root:
        if strip_ns(child.tag) == "Session":
            session = {strip_ns(g.tag): (g.text or "").strip() for g in child}

    if "Key" not in session:
        sys.exit("QRZ login failed (%s). Check qrz_username/qrz_password in .env."
                  % session.get("Error", "no Key returned"))
    return session["Key"]


def qrz_fetch(call, key):
    """Look up one callsign. Returns (record_dict_or_None, error_or_None)."""
    url = QRZ_URL + "?" + urllib.parse.urlencode(
        {"s": key, "callsign": call, "agent": AGENT}
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        root = ET.fromstring(resp.read())

    session = {}
    record = None
    for child in root:
        name = strip_ns(child.tag)
        if name == "Session":
            session = {strip_ns(g.tag): (g.text or "").strip() for g in child}
        elif name == "Callsign":
            record = {strip_ns(g.tag): (g.text or "").strip() for g in child}

    # No Key in the Session node means the session is dead, not that the
    # callsign is missing. Treat that as fatal so we do not silently record a
    # whole log as "not found on QRZ".
    if "Key" not in session:
        sys.exit("QRZ session invalidated mid-run (%s)."
                 % session.get("Error", "no Key returned"))

    if record is None:
        return None, session.get("Error", "not found")
    return record, None


def qrz_lookup(calls, key, use_cache=True):
    """Return {CALL: record}. One request per callsign; results are cached."""
    cache = {}
    if use_cache and os.path.exists(CACHE_FILE):
        try:
            cache = json.load(open(CACHE_FILE))
        except (json.JSONDecodeError, OSError):
            cache = {}

    out = {}
    fetched = 0
    for call in calls:
        if use_cache and call in cache:
            if cache[call] is not None:
                out[call] = cache[call]
            continue
        record, err = qrz_fetch(call, key)
        fetched += 1
        cache[call] = record
        if record:
            out[call] = record
        if fetched > 1:
            time.sleep(0.2)  # be polite to QRZ's servers

    if use_cache:
        try:
            json.dump(cache, open(CACHE_FILE, "w"), indent=1, sort_keys=True)
        except OSError:
            pass

    print("%d looked up, %d served from cache" % (fetched, len(calls) - fetched))
    return out


def pota_fetch(ref, cache):
    """Look up a POTA park. Returns {'grid','state','name'} or None."""
    if ref in cache:
        return cache[ref]
    try:
        with urllib.request.urlopen(POTA_URL % ref, timeout=30) as resp:
            d = json.loads(resp.read())
    except Exception:
        cache[ref] = None
        return None
    if not d:  # unknown park: the API answers with JSON null
        cache[ref] = None
        return None
    # locationDesc is like "US-MO", or "US-FL,US-MS" for a park spanning states.
    loc = (d.get("locationDesc") or "").split(",")
    states = [p.split("-")[-1] for p in loc if p.strip()]
    out = {
        "grid": (d.get("grid6") or d.get("grid4") or "").strip(),
        "states": states,
        "name": (d.get("name") or "").strip(),
    }
    cache[ref] = out
    return out


def apply_pota_grids(records, use_cache=True):
    """Override GRIDSQUARE from the park a station was activating.

    Returns (new_records, notes). A park reference pins the QSO to the park, so
    its grid replaces any QRZ home grid, and the home QTH/CNTY are dropped as
    describing the wrong place.
    """
    cache = {}
    if use_cache and os.path.exists(PARK_CACHE_FILE):
        try:
            cache = json.load(open(PARK_CACHE_FILE))
        except (json.JSONDecodeError, OSError):
            cache = {}

    notes = []
    out = []
    for r in records:
        f = fields_of(r)
        ref = f.get("SIG_INFO")
        if not ref:
            out.append(r)
            continue

        # SIG_INFO lists every park the other station was activating,
        # comma-separated. They are one place, so the first park's grid stands
        # for the contact; the state must hold across all of them.
        refs = [x.strip() for x in ref.split(",") if x.strip()]
        parks = [pota_fetch(x, cache) for x in refs]
        if not all(parks) or not parks[0]["grid"]:
            notes.append((f.get("CALL", "?"), ref, "no park data", "", ""))
            out.append(r)
            continue
        park = {
            "grid": parks[0]["grid"],
            "name": parks[0]["name"],
            "states": sorted({st for p in parks for st in p["states"]}),
        }

        old = f.get("GRIDSQUARE", "")
        new = park["grid"]
        if old != new:
            notes.append((f.get("CALL", "?"), ref, park["name"], old or "(none)", new))
            # replace or insert GRIDSQUARE
            if "GRIDSQUARE" in f:
                r = re.sub(r"<GRIDSQUARE:\d+>[^<\n]*", adif("GRIDSQUARE", new), r, count=1)
            else:
                r = re.sub(r"(<SIG:)", adif("GRIDSQUARE", new) + r"\n\1", r, count=1)
            # the operator's home town/county do not describe a park activation
            for tag in ("QTH", "CNTY"):
                r = re.sub(r"<%s:\d+>[^<\n]*\n?" % tag, "", r, count=1)

        # An activation is in the park's state. Only correct this when the park
        # sits in exactly one state -- some parks span two (Gulf Islands is
        # US-FL,US-MS), and then the logged state is the better evidence.
        if len(park["states"]) == 1:
            want = park["states"][0]
            cur = f.get("STATE", "")
            if cur != want:
                notes.append((f.get("CALL", "?"), ref, "state " + park["name"][:16],
                              cur or "(none)", want))
                if "STATE" in f:
                    r = re.sub(r"<STATE:\d+>[^<\n]*", adif("STATE", want), r, count=1)
                else:
                    r = re.sub(r"(<SIG:)", adif("STATE", want) + r"\n\1", r, count=1)
        out.append(r)

    if use_cache:
        try:
            json.dump(cache, open(PARK_CACHE_FILE, "w"), indent=1, sort_keys=True)
        except OSError:
            pass
    return out, notes


def country_for(rec):
    """Prefer `land` over `country`.

    Per the XML spec, `country` is the country of the QSL *mailing address*,
    while `land` is the DXCC country of the callsign itself. They differ for DX
    operators who receive mail in another country -- e.g. HK3W (Colombia,
    DXCC 116) lists a North Miami address, so `country` says "United States".
    Using it would pair COUNTRY=UNITED STATES with DXCC=116 in the same record.
    """
    c = (rec.get("land") or rec.get("country") or "").strip()
    if c.lower() in ("united states", "usa"):
        return "UNITED STATES OF AMERICA"
    return c.upper()


def name_for(rec):
    fmt = (rec.get("name_fmt") or "").strip()
    if fmt:
        return fmt
    parts = [(rec.get("fname") or "").strip(), (rec.get("name") or "").strip()]
    return " ".join(p for p in parts if p)


def cnty_for(rec):
    county = (rec.get("county") or "").strip()
    state = (rec.get("state") or "").strip()
    if not county:
        return ""
    return "%s,%s" % (state, county) if state else county


def derived(rec):
    """QRZ record -> {ADIF field: value}, omitting blanks.

    Note QRZ sends the city in `addr2`, not a field called `city` -- see the
    spec's Callsign node fields table. (qrzclient renames it on output, which is
    why its JSON looks different from the raw API.)
    """
    out = {
        "NAME": name_for(rec),
        "QTH": (rec.get("addr2") or "").strip(),
        "STATE": (rec.get("state") or "").strip(),
        "CNTY": cnty_for(rec),
        "COUNTRY": country_for(rec),
        "GRIDSQUARE": (rec.get("grid") or "").strip(),
        "DXCC": str(rec.get("dxcc") or "").strip(),
    }
    return {k: v for k, v in out.items() if v}


def main():
    ap = argparse.ArgumentParser(__file__, description="Enrich an ADIF log from the QRZ XML API")
    ap.add_argument("path")
    ap.add_argument("--apply", action="store_true", help="write changes back to the file")
    ap.add_argument("--env", default=".env", help="file holding qrz_username/qrz_password")
    ap.add_argument("--no-cache", action="store_true", help="ignore %s" % CACHE_FILE)
    args = ap.parse_args()

    load_env(args.env)
    username = os.environ.get("qrz_username") or os.environ.get("QRZ_USERNAME")
    password = os.environ.get("qrz_password") or os.environ.get("QRZ_PASSWORD")
    if not username or not password:
        sys.exit("qrz_username/qrz_password not found in %s or the environment" % args.env)
    key = qrz_login(username, password)

    text = open(args.path, encoding="ISO-8859-1").read()
    header, records, trailing = parse_records(text)

    calls = []
    for r in records:
        c = fields_of(r).get("CALL")
        if c and c.upper() not in calls:
            calls.append(c.upper())
    if not calls:
        sys.exit("no CALL fields found in %s" % args.path)

    print("looking up %d callsigns on the QRZ XML API..." % len(calls))
    lookups = qrz_lookup(calls, key, use_cache=not args.no_cache)

    missing = [c for c in calls if c not in lookups]
    if missing:
        print("NOT FOUND on QRZ: %s" % ", ".join(missing))

    added_total = 0
    conflicts = []
    suppressed = []
    new_records = []

    for r in records:
        f = fields_of(r)
        call = (f.get("CALL") or "").upper()
        rec = lookups.get(call)
        if not rec:
            new_records.append(r)
            continue

        want = derived(rec)

        # Logged state disagreeing with QRZ means the operator was travelling;
        # QRZ's home location does not describe this QSO.
        logged_state = f.get("STATE", "").strip().upper()
        qrz_state = want.get("STATE", "").strip().upper()
        away_from_home = bool(logged_state and qrz_state and logged_state != qrz_state)
        if away_from_home:
            suppressed.append((call, logged_state, qrz_state))

        additions = []
        for tag in ENRICH_FIELDS:
            val = want.get(tag)
            if not val:
                continue
            if away_from_home and tag in LOCATION_FIELDS:
                continue
            if tag in f:
                if f[tag].strip().upper() != val.strip().upper():
                    conflicts.append((call, tag, f[tag], val))
                continue
            additions.append(adif(tag, val))

        if additions:
            added_total += len(additions)
            print("%-8s +%s" % (call, ",".join(a.split(">")[0].lstrip("<").split(":")[0]
                                               for a in additions)))
            # insert immediately before <EOR>, matching existing one-field-per-line layout
            r = re.sub(r"(<EOR>)", "\n".join(additions) + r"\n\1", r, count=1, flags=re.IGNORECASE)
        new_records.append(r)

    if suppressed:
        print("\nOPERATING AWAY FROM HOME (kept logged state; skipped QRZ location):")
        for call, logged, qrz in suppressed:
            print("  %-8s logged=%s  qrz-home=%s  -> QTH/CNTY/GRIDSQUARE not imported"
                  % (call, logged, qrz))

    if conflicts:
        print("\nCONFLICTS (kept the existing value, QRZ disagrees):")
        for call, tag, have, qrz in conflicts:
            print("  %-8s %-10s file=%-28s qrz=%s" % (call, tag, have, qrz))

    new_records, park_notes = apply_pota_grids(new_records, use_cache=not args.no_cache)
    if park_notes:
        print("\nPARK GRIDS (park reference overrides the home grid):")
        for call, ref, name, old, new in park_notes:
            print("  %-8s %-9s %-24s %s -> %s" % (call, ref, name[:24], old, new))

    print("\n%d fields would be added across %d records" % (added_total, len(records)))

    if args.apply:
        out = header + "".join(new_records) + trailing
        open(args.path, "w", encoding="ISO-8859-1", errors="replace").write(out)
        print("wrote %s" % args.path)
    else:
        print("dry run -- rerun with --apply to write")


if __name__ == "__main__":
    main()
