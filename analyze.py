import unicodedata

import adif_io
import matplotlib.pyplot as plt
import polars as pl

if __name__ == '__main__':


  calls = {}
  with open("./w1ytq.349397.20241231142157.adi", 'r', encoding = "ISO-8859-1") as rf:
    content = ''.join(rf.readlines())
    qsos, header = adif_io.read_from_string(content)
    df = pl.DataFrame([{k:v for k,v in q.items()} for q in qsos])

    print(df.columns)
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