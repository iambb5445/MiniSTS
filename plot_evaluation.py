import pandas as pd
import seaborn as sns
import argparse
from matplotlib import pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('by_column')
    args = parser.parse_args()
    df: pd.DataFrame = pd.read_csv(args.filename)

    by_column = args.by_column
    test_count = len(df) / len(set(df[by_column]))
    plt.figure(figsize=(8, 6))
    sns.histplot(data=df, x="PlayerHealth", hue=by_column, bins=15, element="step", common_norm=False, kde=True)

    plt.title(f"Distribution of Player Health by {by_column} - {test_count} Samples")
    plt.xlabel("Player Health")
    plt.ylabel("Count")
    plt.show()

if __name__ == '__main__':
    main()