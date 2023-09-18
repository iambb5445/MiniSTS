import pandas as pd
import seaborn as sns
import argparse
import numpy as np
from matplotlib import pyplot as plt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('by_column')
    args = parser.parse_args()
    df: pd.DataFrame = pd.read_csv(args.filename)

    by_col = args.by_column
    target_col = "PlayerHealth"
    test_count = len(df) / len(set(df[by_col]))
    print(df.filter(items=[target_col, by_col]).groupby(by_col).mean())
    print(df.filter(items=[target_col, by_col]).groupby(by_col).apply(lambda g: np.mean(g[target_col] * g[target_col])))
    print(df.filter(items=[target_col, by_col]).groupby(by_col).agg(np.std, ddof=1))
    plt.figure(figsize=(8, 6))
    sns.histplot(data=df, x=target_col, hue=by_col, bins=15, element="step", common_norm=False, kde=True)
    plt.title(f"Distribution of {target_col} by {by_col} - {test_count} Samples")
    plt.xlabel(target_col)
    plt.ylabel("Count")
    plt.show()

if __name__ == '__main__':
    main()