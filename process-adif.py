#! /usr/bin/env python3

import argparse
from functools import partial
from pathlib import Path

import adif_io
import matplotlib.pyplot as plt
import polars as pl
from icecream import ic


def plot_mode_distribution(df):
    mode_counts = df["MODE"].value_counts()
    print(mode_counts)
    total_mode = df["MODE"].count()
    mode_counts = mode_counts.with_columns(
        (mode_counts["count"] / total_mode * 100).round(0).alias("MODE_PERCENTAGE"))
    # Filter out entries with a percentage less than 1
    mode_counts = mode_counts.filter(mode_counts['MODE_PERCENTAGE'] >= 1)
    print(f"{total_mode} QSOs in 2025")
    print(mode_counts)

    # Extract data for the pie chart
    labels = mode_counts['MODE'].to_list()
    sizes = mode_counts['MODE_PERCENTAGE'].to_list()

    # Create a pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('W1YTQ Operating Modes in 2024')
    # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.axis('equal')
    plt.show()

def plot_qsos_per_day(df):
    # Convert the QSO_DATE column to datetime
    df = df.with_columns(pl.col("QSO_DATE").str.strptime(pl.Date, "%Y%m%d"))

    # Filter out any QSO that is not the first for that call sign
    df = df.with_columns(pl.col("QSO_DATE").rank("dense").over("CALL").alias("rank"))
    df = df.filter(pl.col("rank") == 1)

    # Group by date and count the number of QSOs per day
    qsos_per_day = df.group_by("QSO_DATE").agg(pl.count("CALL").alias("count")).sort("QSO_DATE")

    # Calculate the cumulative sum of QSOs
    qsos_per_day = qsos_per_day.with_columns(pl.col("count").cum_sum().alias("cumulative_count"))

    # Extract data for the line graph
    dates = qsos_per_day["QSO_DATE"].to_list()
    cumulative_counts = qsos_per_day["cumulative_count"].to_list()

    # Create a cumulative line graph
    plt.figure(figsize=(10, 6))
    plt.plot(dates, cumulative_counts, marker='o', linestyle='-', color='b')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Number of QSOs')
    plt.title('Cumulative QSOs per Day')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()    


def command_top_10_calls(df):
    # Get the top 10 CALL entries by frequency
    call_counts = df['CALL'].value_counts().sort('count', descending=True)
    top_10_calls = call_counts.head(10)
    print("Top 10 CALL entries:")
    print(top_10_calls)


def filter_skcc(qsos):
    qsos = ((q.get('comment'), q) for q in qsos)
    qsos = (q for comment, q in qsos if comment and 'skcc' in comment.lower())

    return qsos

def add_key_type(qso, key_type='SK'):
    # <APP_SKCCLOGGER_KEYTYPE:2>SK
    qso = {**qso, **{'APP_SKCCLOGGER_KEYTYPE': key_type}}
    return qso

def add_comment(qso, comment=''):
    comment = qso.get('comment', '') + '\n' + comment
    comment = comment.strip()
    qso = {**qso, **{'COMMENT': comment}}
    return qso

def write_adif(path: Path, headers, qsos):
    headers = adif_io.headers_from_dict(headers)
    with open(path, 'w',  encoding="ISO-8859-1") as wf:
        wf.writelines(adif_io.headers_to_adif(headers))
        wf.writelines((adif_io.qso_to_adif(q) for q in qsos))

def main():

    # Set up argument parser
    parser = argparse.ArgumentParser(
        __file__, description="Analyze ham radio data")
    command_choices = ['columns', 'modedist', 'top10calls', 'skcc', 'comment', 'perday']
    parser.add_argument('command', choices=command_choices, help='Type of command to run')
    parser.add_argument('adif', type=str, help='ADIF file to process')
    parser.add_argument('--key', type=str, default='', help="Add the SKCCLOGGER_KEYTYPE (e.g., 'SK') to the adif records")
    parser.add_argument('--comment', type=str, default='', help="Comment that you want added to the comment fields in your ADIF records")

    # Parse command-line arguments
    args = parser.parse_args()

    adif = Path.cwd().joinpath(args.adif)
    adif_basename_sans_suffix = Path(adif).stem

    with open(adif, 'r', encoding="ISO-8859-1") as rf:
        content = ''.join(rf.readlines())
        qsos, header = adif_io.read_from_string(content)
        qsos_list = list(qsos)
        df = pl.DataFrame([{k: v for k, v in q.items()} for q in qsos_list])
        # Execute the specified command
        if args.command == 'perday':
            plot_qsos_per_day(df)
        if args.command == 'modedist':
            plot_mode_distribution(df)
        if args.command == 'top10calls':
            command_top_10_calls(df)
        if args.command == 'skcc':
            qsos = filter_skcc(qsos_list)
            if args.key:
                add_key_type_func = partial(add_key_type, key_type=args.key)
                qsos = list(map(add_key_type_func, qsos))

            headers = {
                "generated_by": "Source code found at https://github.com/chrisfarnham/ham-radio-utils",
                "description": "Only QSOs with SKCC in comments",
            }
            write_adif(Path.cwd().joinpath(f'{adif_basename_sans_suffix}.skcc.adi'), headers, qsos)


        if args.command == 'comment':
            if args.comment:
                add_comment_func = partial(add_comment, comment=args.comment)
                qsos = list(map(add_comment_func, qsos))
            else:
                print("--comment switch is required when using the comment command")
                parser.print_help()
                exit(1)

            headers = {
                "generated_by": "Source code found at https://github.com/chrisfarnham/ham-radio-utils",
                "description": f"Appended comment {args.comment}  each QSO",
            }
            write_adif(Path.cwd().joinpath(f'{adif_basename_sans_suffix}.comments.adi'), headers, qsos)


        else:
            print("")
            print(df.columns)


if __name__ == '__main__':
    main()
