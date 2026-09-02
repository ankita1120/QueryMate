"""
file_loader.py

QueryMate AI
Smart File Loader

Supports:
- CSV
- Excel (.xlsx, .xls)
- Multiple files
"""

import pandas as pd


class FileLoader:

    def __init__(self):
        pass

    def load_file(self, uploaded_file):

        if uploaded_file is None:
            return None

        filename = uploaded_file.name.lower()

        try:

            # CSV
            if filename.endswith(".csv"):
                return pd.read_csv(uploaded_file)

            # Excel
            elif filename.endswith((".xlsx", ".xls")):
                return pd.read_excel(uploaded_file)

            else:
                raise ValueError(
                    f"Unsupported file type: {uploaded_file.name}"
                )

        except Exception as e:
            raise Exception(
                f"Failed to load {uploaded_file.name}: {e}"
            )

    def load_files(self, uploaded_files):

        datasets = {}

        if not uploaded_files:
            return datasets

        for file in uploaded_files:

            datasets[file.name] = self.load_file(file)

        return datasets