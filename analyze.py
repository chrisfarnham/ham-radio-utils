import unicodedata

import adif_io
import matplotlib.pyplot as plt
import polars as pl
import argparse

def plot_mode_distribution(df):
  mode_counts = df["MODE"].value_counts()
  print(mode_counts)
  total_mode = df["MODE"].count()
  mode_counts = mode_counts.with_columns((mode_counts["count"] / total_mode * 100).alias("MODE_PERCENTAGE"))

  print(mode_counts)


  # Extract data for the pie chart
  labels = mode_counts['MODE'].to_list()
  sizes = mode_counts['MODE_PERCENTAGE'].to_list()

  # Create a pie chart
  plt.figure(figsize=(8, 6))
  plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
  plt.title('W1YTQ Operating Modes in 2024')
  plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
  plt.show()

def report_top_10_calls(df):
    # Get the top 10 CALL entries by frequency
    call_counts = df['CALL'].value_counts().sort('count', descending=True)
    top_10_calls = call_counts.head(10)
    print("Top 10 CALL entries:")
    print(top_10_calls)

def main():

  # Set up argument parser
  parser = argparse.ArgumentParser(description="Analyze ham radio data")
  report_choices = ['columns', 'modedist', 'top10calls']
  parser.add_argument('report', choices=report_choices, default='columns', nargs='?', help='Type of report to generate')

  # Parse command-line arguments
  args = parser.parse_args()

  with open("./w1ytq.349397.20241231142157.adi", 'r', encoding = "ISO-8859-1") as rf:
    content = ''.join(rf.readlines())
    qsos, header = adif_io.read_from_string(content)
    df = pl.DataFrame([{k:v for k,v in q.items()} for q in qsos])

    # Execute the specified report
    if args.report == 'mode_distribution':
        plot_mode_distribution(df)
    if args.report == 'top10calls':
      report_top_10_calls(df)
    else:
      print(df.columns)


if __name__ == '__main__':
  main()
