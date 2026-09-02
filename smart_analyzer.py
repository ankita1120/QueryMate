"""
smart_analyzer.py

Fast rule-based analysis for QueryMate.
Handles common analytical questions without calling Gemini.
"""

import pandas as pd


class SmartAnalyzer:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def analyze(self, question: str):

        question = question.lower()

        numeric_cols = self.df.select_dtypes(include="number").columns.tolist()

        # -----------------------------
        # Total
        # -----------------------------
        if "total" in question:
            for col in numeric_cols:
                if col.lower() in question:
                    return self.df[col].sum()

        # -----------------------------
        # Average
        # -----------------------------
        if "average" in question or "mean" in question:
            for col in numeric_cols:
                if col.lower() in question:
                    return round(self.df[col].mean(), 2)

        # -----------------------------
        # Maximum
        # -----------------------------
        if "maximum" in question or "highest" in question or "max" in question:
            for col in numeric_cols:
                if col.lower() in question:
                    return self.df[col].max()

        # -----------------------------
        # Minimum
        # -----------------------------
        if "minimum" in question or "lowest" in question or "min" in question:
            for col in numeric_cols:
                if col.lower() in question:
                    return self.df[col].min()

        # -----------------------------
        # Median
        # -----------------------------
        if "median" in question:
            for col in numeric_cols:
                if col.lower() in question:
                    return self.df[col].median()

        # -----------------------------
        # Standard Deviation
        # -----------------------------
        if "standard deviation" in question or "std" in question:
            for col in numeric_cols:
                if col.lower() in question:
                    return round(self.df[col].std(), 2)

        # -----------------------------
        # Missing Values
        # -----------------------------
        if "missing" in question or "null" in question:
            return self.df.isnull().sum()

        # -----------------------------
        # Duplicate Rows
        # -----------------------------
        if "duplicate" in question:
            return int(self.df.duplicated().sum())

        # -----------------------------
        # Rows
        # -----------------------------
        if "rows" in question or "records" in question:
            return len(self.df)

        # -----------------------------
        # Columns
        # -----------------------------
        if "columns" in question:
            return list(self.df.columns)

        # -----------------------------
        # Shape
        # -----------------------------
        if "shape" in question:
            return self.df.shape

        # -----------------------------
        # Data Types
        # -----------------------------
        if "datatype" in question or "data type" in question or "dtype" in question:
            return self.df.dtypes

        # -----------------------------
        # Unique Values
        # -----------------------------
        if "unique" in question:
            for col in self.df.columns:
                if col.lower() in question:
                    return self.df[col].nunique()

        # -----------------------------
        # Correlation
        # -----------------------------
        if "correlation" in question:
            return self.df.corr(numeric_only=True)

        return None