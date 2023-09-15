import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

file_name: str = "evaluation_results\\evaluation_on_100_tests_1694812888.csv"

def main():
    df: pd.DataFrame = pd.read_csv(file_name)

    plt.figure(figsize=(8, 6))
    sns.histplot(data=df, x="PlayerHealth", hue="BotName", bins=15, element="step", common_norm=False, kde=True)

    # Customize the plot
    plt.title("Distribution of Player Health by Bot Name")
    plt.xlabel("Player Health")
    plt.ylabel("Count")

    # Show the plot
    plt.show()

    return
    print(df[df["Bot Name"] == "random"])
    df.plot.bar(y="Player Health")
    plt.show()

if __name__ == '__main__':
    main()