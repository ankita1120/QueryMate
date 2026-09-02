"""
chart_recommender.py

QueryMate AI Automatic Chart Recommendation Engine
"""

import pandas as pd
import plotly.express as px


class ChartRecommender:

    def __init__(self, df):

        self.df = df


    def recommend_charts(self):

        charts = []

        numeric_cols = (
            self.df
            .select_dtypes(include="number")
            .columns
            .tolist()
        )

        categorical_cols = (
            self.df
            .select_dtypes(include="object")
            .columns
            .tolist()
        )


        # Numeric distribution
        if numeric_cols:

            col = numeric_cols[0]

            fig = px.histogram(
                self.df,
                x=col,
                title=f"{col} Distribution"
            )

            charts.append(fig)


        # Category comparison
        if categorical_cols and numeric_cols:

            category = categorical_cols[0]
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
                title=f"{value} by {category}"
            )

            charts.append(fig)


        # Correlation
        if len(numeric_cols) > 1:

            corr = (
                self.df[numeric_cols]
                .corr()
            )


            fig = px.imshow(
                corr,
                title="Feature Correlation"
            )

            charts.append(fig)


        return charts