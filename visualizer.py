"""
visualizer.py

Visualization module for QueryMate AI
"""

import pandas as pd
import matplotlib.pyplot as plt


class DataVisualizer:

    def __init__(self, df):
        self.df = df


    # -----------------------------
    # Histogram Charts
    # -----------------------------
    def numeric_charts(self):

        charts = []

        numeric_columns = (
            self.df
            .select_dtypes(include="number")
            .columns
        )

        for col in numeric_columns[:5]:

            fig, ax = plt.subplots(figsize=(6, 4))

            ax.hist(
                self.df[col].dropna(),
                bins=20
            )

            ax.set_title(
                f"Distribution of {col}"
            )

            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")

            fig.tight_layout()

            charts.append(fig)

        return charts


    # -----------------------------
    # Correlation Heatmap
    # -----------------------------
    def correlation_chart(self):

        numeric_df = (
            self.df
            .select_dtypes(include="number")
        )

        if len(numeric_df.columns) < 2:
            return None


        correlation = numeric_df.corr()


        fig, ax = plt.subplots(
            figsize=(7,6)
        )


        image = ax.imshow(
            correlation
        )


        ax.set_title(
            "Correlation Heatmap"
        )


        ax.set_xticks(
            range(len(correlation.columns))
        )

        ax.set_xticklabels(
            correlation.columns,
            rotation=90
        )


        ax.set_yticks(
            range(len(correlation.columns))
        )

        ax.set_yticklabels(
            correlation.columns
        )


        fig.colorbar(image)

        fig.tight_layout()


        return fig



    # -----------------------------
    # Bar Chart
    # -----------------------------
    def bar_chart(self, column):

        if column not in self.df.columns:
            return None


        fig, ax = plt.subplots(
            figsize=(6,4)
        )


        (
            self.df[column]
            .value_counts()
            .head(10)
            .plot(
                kind="bar",
                ax=ax
            )
        )


        ax.set_title(
            f"Top Values of {column}"
        )


        ax.set_ylabel(
            "Count"
        )


        fig.tight_layout()


        return fig



    # -----------------------------
    # Line Chart
    # -----------------------------
    def line_chart(self, column):

        if column not in self.df.columns:
            return None


        if not pd.api.types.is_numeric_dtype(
            self.df[column]
        ):
            return None


        fig, ax = plt.subplots(
            figsize=(6,4)
        )


        self.df[column].plot(
            ax=ax
        )


        ax.set_title(
            f"Trend of {column}"
        )


        fig.tight_layout()


        return fig



    # -----------------------------
    # Box Plot
    # -----------------------------
    def box_plot(self, column):

        if column not in self.df.columns:
            return None


        if not pd.api.types.is_numeric_dtype(
            self.df[column]
        ):
            return None


        fig, ax = plt.subplots(
            figsize=(6,4)
        )


        ax.boxplot(
            self.df[column].dropna()
        )


        ax.set_title(
            f"Box Plot of {column}"
        )


        ax.set_ylabel(
            column
        )


        fig.tight_layout()


        return fig



    # -----------------------------
    # Scatter Plot
    # -----------------------------
    def scatter_plot(
        self,
        x_col,
        y_col
    ):

        if (
            x_col not in self.df.columns
            or
            y_col not in self.df.columns
        ):
            return None


        if (
            not pd.api.types.is_numeric_dtype(self.df[x_col])
            or
            not pd.api.types.is_numeric_dtype(self.df[y_col])
        ):
            return None


        fig, ax = plt.subplots(
            figsize=(6,4)
        )


        ax.scatter(
            self.df[x_col],
            self.df[y_col]
        )


        ax.set_xlabel(
            x_col
        )

        ax.set_ylabel(
            y_col
        )


        ax.set_title(
            f"{x_col} vs {y_col}"
        )


        fig.tight_layout()


        return fig
    # -----------------------------
    # Automatic Chart Selection
    # -----------------------------
    def automatic_charts(self):

        charts = []

        numeric_columns = (
            self.df
            .select_dtypes(include="number")
            .columns
        )

        categorical_columns = (
            self.df
            .select_dtypes(include="object")
            .columns
        )


        # Numeric columns → Histogram
        for col in numeric_columns[:3]:

            fig, ax = plt.subplots(figsize=(6,4))

            ax.hist(
                self.df[col].dropna(),
                bins=20
            )

            ax.set_title(
                f"Distribution of {col}"
            )

            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")

            fig.tight_layout()

            charts.append(fig)



        # Category columns → Bar Chart
        for col in categorical_columns[:2]:

            fig, ax = plt.subplots(figsize=(6,4))

            (
                self.df[col]
                .value_counts()
                .head(10)
                .plot(
                    kind="bar",
                    ax=ax
                )
            )

            ax.set_title(
                f"Top Values of {col}"
            )

            ax.set_ylabel("Count")

            fig.tight_layout()

            charts.append(fig)



        # Two numeric columns → Scatter Plot
        if len(numeric_columns) >= 2:

            fig, ax = plt.subplots(figsize=(6,4))

            ax.scatter(
                self.df[numeric_columns[0]],
                self.df[numeric_columns[1]]
            )

            ax.set_xlabel(
                numeric_columns[0]
            )

            ax.set_ylabel(
                numeric_columns[1]
            )

            ax.set_title(
                f"{numeric_columns[0]} vs {numeric_columns[1]}"
            )

            fig.tight_layout()

            charts.append(fig)


        return charts