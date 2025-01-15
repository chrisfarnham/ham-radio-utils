#! /usr/bin/env python3

import argparse
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


def report_top_10_calls(df):
    # Get the top 10 CALL entries by frequency
    call_counts = df['CALL'].value_counts().sort('count', descending=True)
    top_10_calls = call_counts.head(10)
    print("Top 10 CALL entries:")
    print(top_10_calls)


def filter_skcc(qsos):
    qsos = ((q.get('comment'), q) for q in qsos)
    qsos = (q for comment, q in qsos if comment and 'skcc' in comment.lower())
    return qsos


def main():

    # Set up argument parser
    parser = argparse.ArgumentParser(
        __file__, description="Analyze ham radio data")
    report_choices = ['columns', 'modedist', 'top10calls', 'skcc']
    parser.add_argument('report', choices=report_choices, help='Type of report to generate')
    parser.add_argument('adif', type=str, help='ADIF file to process')

    # Parse command-line arguments
    args = parser.parse_args()

    adif = Path.cwd().joinpath(args.adif)
    adif_basename_sans_suffix = Path(adif).stem

    with open(adif, 'r', encoding="ISO-8859-1") as rf:
        content = ''.join(rf.readlines())
        qsos, header = adif_io.read_from_string(content)
        qsos_list = list(qsos)
        df = pl.DataFrame([{k: v for k, v in q.items()} for q in qsos_list])
        # Execute the specified report
        if args.report == 'modedist':
            plot_mode_distribution(df)
        if args.report == 'top10calls':
            report_top_10_calls(df)
        if args.report == 'skcc':
            qsos = filter_skcc(qsos_list)
            headers = {
                "generated_by": "Source code found at https://github.com/chrisfarnham/ham-radio-utils",
                "description": "Only QSOs with SKCC in comments",
            }
            headers = adif_io.headers_from_dict(headers)
            with open(Path.cwd().joinpath(f'{adif_basename_sans_suffix}.skcc.adi'), 'w',  encoding="ISO-8859-1") as wf:
                wf.writelines(adif_io.headers_to_adif(headers))
                wf.writelines((adif_io.qso_to_adif(q) for q in qsos))

        else:
            print("")
            print(df.columns)


if __name__ == '__main__':
    main()
