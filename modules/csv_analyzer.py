import pandas as pd

def analyze_csv(file_path):
    df = pd.read_csv(file_path)

    print("\n📊 Weather Dataset Analysis")
    print("=" * 40)

    print("\nFirst 5 Rows:")
    print(df.head())

    print("\nDataset Information:")
    print(df.info())

    print("\nStatistics:")
    print(df.describe())


if __name__ == "__main__":
    analyze_csv("data/daily_weather.csv")