"""
insight_generator.py

Generate AI-powered insights for uploaded datasets.
"""

import pandas as pd


class InsightGenerator:

    def __init__(self, df: pd.DataFrame):
        self.df = df


    def generate_basic_insights(self):
        """Generate automatic dataset insights."""

        insights = []

        # Dataset overview
        rows = len(self.df)
        cols = len(self.df.columns)

        insights.append(
            f"📊 Dataset contains {rows} rows and {cols} columns."
        )


        # Missing values
        missing = self.df.isnull().sum()

        total_missing = missing.sum()

        if total_missing > 0:
            insights.append(
                f"⚠️ Dataset has {total_missing} missing values."
            )

            missing_cols = missing[missing > 0]

            for col, value in missing_cols.items():
                insights.append(
                    f" - {col}: {value} missing values"
                )

        else:
            insights.append(
                "✅ No missing values detected."
            )


        # Numeric analysis
        numeric_cols = (
            self.df
            .select_dtypes(include="number")
            .columns
        )


        for col in numeric_cols:

            mean = self.df[col].mean()
            minimum = self.df[col].min()
            maximum = self.df[col].max()

            insights.append(
                f"📈 {col}: Average={mean:.2f}, "
                f"Lowest={minimum}, Highest={maximum}"
            )


            # Trend insight
            if mean > maximum * 0.7:
                insights.append(
                    f"🔎 {col} values are generally high compared to range."
                )


        # Categorical analysis
        categorical_cols = (
            self.df
            .select_dtypes(include="object")
            .columns
        )


        for col in categorical_cols:

            unique_values = self.df[col].nunique()

            insights.append(
                f"🏷️ {col} contains {unique_values} unique categories."
            )


            if unique_values < 10:

                top_value = (
                    self.df[col]
                    .value_counts()
                    .idxmax()
                )

                insights.append(
                    f"⭐ Most common {col}: {top_value}"
                )


        return insights