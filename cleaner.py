"""
cleaner.py

QueryMate AI Data Cleaning Assistant
"""

import pandas as pd


class DataCleaner:

    def __init__(self, df):

        self.df = df.copy()


    # -----------------------------------------
    # Missing Values Report
    # -----------------------------------------

    def missing_values_report(self):

        missing = (
            self.df
            .isnull()
            .sum()
        )

        report = (
            missing[missing > 0]
            .to_dict()
        )

        return report


    # -----------------------------------------
    # Duplicate Report
    # -----------------------------------------

    def duplicate_report(self):

        return int(
            self.df
            .duplicated()
            .sum()
        )


    # -----------------------------------------
    # Remove Duplicates
    # -----------------------------------------

    def remove_duplicates(self):

        self.df = (
            self.df
            .drop_duplicates()
        )

        return self.df


    # -----------------------------------------
    # Fill Missing Values
    # -----------------------------------------

    def fill_missing_values(self):

        for column in self.df.columns:


            if self.df[column].isnull().sum() > 0:


                if pd.api.types.is_numeric_dtype(
                    self.df[column]
                ):

                    self.df[column] = (
                        self.df[column]
                        .fillna(
                            self.df[column].median()
                        )
                    )


                else:

                    self.df[column] = (
                        self.df[column]
                        .fillna(
                            self.df[column]
                            .mode()[0]
                        )
                    )


        return self.df


    # -----------------------------------------
    # Data Type Detection
    # -----------------------------------------

    def datatype_report(self):

        return (
            self.df
            .dtypes
            .astype(str)
            .to_dict()
        )


    # -----------------------------------------
    # Clean Dataset
    # -----------------------------------------

    def clean_dataset(self):

        self.remove_duplicates()

        self.fill_missing_values()

        return self.df