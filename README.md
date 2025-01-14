# ham-radio-utils

Personal tool developed and used by W1YTQ to filter and generate statistics from radio logging exports in adif format.

### View radio modes

        ./process-adif.py combined.adi modedist

![Pie chart showing radio modes](./radio_mode_dist.png)

### Report top 10 call signs in your log

```bash
 % ./process-adif.py combined.adi top10calls
Top 10 CALL entries:
shape: (10, 2)
┌────────┬───────┐
│ CALL   ┆ count │
│ ---    ┆ ---   │
│ str    ┆ u32   │
╞════════╪═══════╡
│ AB9CA  ┆ 10    │
│ WB0RLJ ┆ 8     │
│ W4SK   ┆ 7     │
│ NS1C   ┆ 6     │
│ W8NWG  ┆ 6     │
│ W5ATJ  ┆ 5     │
│ WD5EEI ┆ 5     │
│ KS4S   ┆ 5     │
│ N2QW   ┆ 5     │
│ W9VI   ┆ 5     │
└────────┴───────┘

```

### Create a new adi file selecting only the QSOs that have "SKCC" in the comments attribute

The command below creates a new adi file with an `skcc.adi` suffix that is a subset of the provided file. The new file
will only have SKCC QSO records which are identified because their 'comments' attribute contains the string 'skcc' or 'SKCC'.

```bash
% ./process-adif.py w1ytq.349397.20250114172534.adi skcc
(ham-radio-utils) cfarnham@Christophers-MacBook-Pro ham-radio-utils % ls -alt w1ytq.349397.20250114172534*
-rw-r--r--@ 1 cfarnham  staff  14741 Jan 14 17:08 w1ytq.349397.20250114172534.skcc.adi
-rw-r--r--@ 1 cfarnham  staff  14741 Jan 14 16:56 w1ytq.349397.20250114172534.adi
```

## Install

Ensure you have Python 3 installed, preferably in a virtual environment created with a tool like `pipenv`.

Then run `pip install -r requirements.txt`


## update requirements.txt

Only maintainers need to do this in cases where we want to manage dependencies.

Install pip-tools

    pip install pip-tools

Make sure that pyproject.toml has the libraries you want and then type:

    pip-compile
