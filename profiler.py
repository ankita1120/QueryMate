"""
profiler.py

Automatic Dataset Profiling for QueryMate AI Data Analyst
"""

import pandas as pd


class DataProfiler:
    def __init__(self, df):
        self.df = df

    def profile(self):
        """
        Generate a complete profile report for the dataset.
        """

        # ==========================
        # Handle Empty Dataset
        # ==========================
        if self.df.empty:
            return {
                "rows": 0,
                "columns": 0,
                "shape": (0, 0),
                "memory_usage_mb": 0,
                "duplicates": 0,
                "total_missing_values": 0,
                "quality_score": 100,
                "numeric_columns": [],
                "categorical_columns": [],
                "datetime_columns": [],
                "column_details": [],
                "numeric_statistics": {},
                "categorical_statistics": {}
            }

        report = {}

        # ==========================
        # Basic Information
        # ==========================
        report["rows"] = len(self.df)
        report["columns"] = len(self.df.columns)
        report["shape"] = self.df.shape

        # ==========================
        # Memory Usage
        # ==========================
        report["memory_usage_mb"] = round(
            self.df.memory_usage(deep=True).sum() / (1024 * 1024),
            2
        )

        # ==========================
        # Duplicate Rows
        # ==========================
        report["duplicates"] = int(self.df.duplicated().sum())

        # ==========================
        # Missing Values
        # ==========================
        report["total_missing_values"] = int(
            self.df.isna().sum().sum()
        )

        # ==========================
        # Column Detection
        # ==========================
        numeric_df = self.df.select_dtypes(include="number")

        categorical_df = self.df.select_dtypes(
            include=["object", "category"]
        )

        datetime_df = self.df.select_dtypes(
            include=["datetime", "datetimetz"]
        )

        report["numeric_columns"] = list(
            numeric_df.columns
        )

        report["categorical_columns"] = list(
            categorical_df.columns
        )

        report["datetime_columns"] = list(
            datetime_df.columns
        )

        # ==========================
        # Dataset Quality Score
        # ==========================
        total_cells = report["rows"] * report["columns"]

        missing_penalty = (
            report["total_missing_values"] / total_cells
        ) * 100 if total_cells else 0

        duplicate_penalty = (
            report["duplicates"] / report["rows"]
        ) * 100 if report["rows"] else 0

        quality = max(
            0,
            100 - missing_penalty - duplicate_penalty
        )

        report["quality_score"] = round(quality, 2)

        # ==========================
        # Column Details
        # ==========================
        column_details = []

        for col in self.df.columns:

            missing = int(self.df[col].isna().sum())

            column_details.append(
                {
                    "name": col,
                    "dtype": str(self.df[col].dtype),
                    "unique_values": int(
                        self.df[col].nunique(dropna=True)
                    ),
                    "missing_values": missing,
                    "missing_percentage": round(
                        (missing / report["rows"]) * 100,
                        2
                    )
                }
            )

        report["column_details"] = column_details

        # ==========================
        # Numeric Statistics
        # ==========================
        numeric_statistics = {}

        for col in numeric_df.columns:

            numeric_statistics[col] = {
                "count": int(numeric_df[col].count()),
                "mean": round(
                    float(numeric_df[col].mean()),
                    2
                ),
                "median": round(
                    float(numeric_df[col].median()),
                    2
                ),
                "std": round(
                    float(numeric_df[col].std()),
                    2
                ),
                "min": round(
                    float(numeric_df[col].min()),
                    2
                ),
                "max": round(
                    float(numeric_df[col].max()),
                    2
                ),
                "sum": round(
                    float(numeric_df[col].sum()),
                    2
                )
            }

        report["numeric_statistics"] = numeric_statistics

        # ==========================
        # Categorical Statistics
        # ==========================
        categorical_statistics = {}

        for col in categorical_df.columns:

            mode = categorical_df[col].mode()

            value_counts = categorical_df[col].value_counts()

            categorical_statistics[col] = {
                "unique_values": int(
                    categorical_df[col].nunique()
                ),
                "most_frequent": (
                    mode.iloc[0]
                    if not mode.empty
                    else "N/A"
                ),
                "top_frequency": (
                    int(value_counts.max())
                    if not value_counts.empty
                    else 0
                )
            }

        report["categorical_statistics"] = categorical_statistics

        return report