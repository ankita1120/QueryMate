"""
overview.py

Displays basic information about the uploaded dataset.
"""

import pandas as pd


class DatasetOverview:

    def __init__(self, df: pd.DataFrame):

        self.df = df


    def generate(self):

        df = self.df


        memory_mb = (
            df.memory_usage(deep=True).sum()
            / (1024 * 1024)
        )


        overview = {

            "Rows": len(df),

            "Columns": len(df.columns),

            "Missing Values": int(
                df.isnull()
                .sum()
                .sum()
            ),

            "Duplicate Rows": int(
                df.duplicated()
                .sum()
            ),

            "Memory Usage (MB)": round(
                memory_mb,
                2
            )

        }


        return overview