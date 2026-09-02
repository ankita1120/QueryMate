"""
dashboard_builder.py

QueryMate AI Automatic Dashboard Builder
"""

import pandas as pd
import plotly.express as px

class DashboardBuilder:

    def __init__(self, df):

        self.df = df


    # -----------------------------------------
    # Generate KPI Metrics
    # -----------------------------------------

    def generate_kpis(self):

        kpis = {}

        kpis["Total Rows"] = len(self.df)

        kpis["Total Columns"] = len(
            self.df.columns
        )

        kpis["Missing Values"] = int(
            self.df.isnull()
            .sum()
            .sum()
        )

        kpis["Duplicate Rows"] = int(
            self.df.duplicated()
            .sum()
        )

        return kpis


    # -----------------------------------------
    # Numeric Columns
    # -----------------------------------------

    def numeric_columns(self):

        return list(
            self.df
            .select_dtypes(
                include="number"
            )
            .columns
        )


    # -----------------------------------------
    # Category Columns
    # -----------------------------------------

    def categorical_columns(self):

        return list(
            self.df
            .select_dtypes(
                include="object"
            )
            .columns
        )


    # -----------------------------------------
    # Create Charts
    # -----------------------------------------

    def generate_charts(self):

        charts = []


        numeric_cols = (
            self.numeric_columns()
        )


        category_cols = (
            self.categorical_columns()
        )


        # Histogram

        if numeric_cols:

            col = numeric_cols[0]

            fig = px.histogram(
                self.df,
                x=col,
                title=f"{col} Distribution"
            )

            charts.append(fig)



        # Bar Chart

        if category_cols and numeric_cols:

            category = category_cols[0]

            value = numeric_cols[0]


            summary = (
                self.df
                .groupby(category)[value]
                .sum()
                .reset_index()
                .head(10)
            )


            fig = px.bar(
                summary,
                x=category,
                y=value,
                title=f"Top {category}"
            )


            charts.append(fig)



        # Correlation Heatmap

        if len(numeric_cols) > 1:


            corr = (
                self.df[numeric_cols]
                .corr()
            )


            fig = px.imshow(
                corr,
                title="Correlation Heatmap"
            )


            charts.append(fig)


        return charts