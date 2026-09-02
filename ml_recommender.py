"""
ml_recommender.py

QueryMate AI - Machine Learning Recommendation Engine
"""

import pandas as pd


class MLRecommender:

    def __init__(self, df):

        self.df = df

    # --------------------------------
    # Detect Dataset Problem Type
    # --------------------------------

    def detect_problem_type(self):

        numeric_cols = (
            self.df
            .select_dtypes(
                include="number"
            )
            .columns
        )

        categorical_cols = (
            self.df
            .select_dtypes(
                include=["object", "category"]
            )
            .columns
        )

        date_cols = []

        for col in self.df.columns:

            col_name = col.lower()

            if (
                "date" in col_name
                or "time" in col_name
                or "year" in col_name
            ):

                date_cols.append(col)

        # Time Series
        if len(date_cols) > 0 and len(numeric_cols) > 0:

            return "Time Series Forecasting"

        # Classification
        if len(categorical_cols) > 0:

            return "Classification"

        # Regression
        if len(numeric_cols) > 0:

            return "Regression"

        # Clustering
        return "Clustering"

    # --------------------------------
    # Recommend ML Models
    # --------------------------------

    def recommend_models(self):

        problem = self.detect_problem_type()

        if problem == "Regression":

            models = [
                "Linear Regression",
                "Random Forest Regressor",
                "Gradient Boosting Regressor",
                "XGBoost Regressor"
            ]

        elif problem == "Classification":

            models = [
                "Logistic Regression",
                "Decision Tree Classifier",
                "Random Forest Classifier",
                "XGBoost Classifier"
            ]

        elif problem == "Time Series Forecasting":

            models = [
                "ARIMA",
                "Prophet",
                "LSTM",
                "XGBoost Forecasting"
            ]

        else:

            models = [
                "K-Means Clustering",
                "DBSCAN",
                "Hierarchical Clustering"
            ]

        return {
            "problem_type": problem,
            "recommended_models": models
        }

    # --------------------------------
    # Feature Suggestions
    # --------------------------------

    def suggest_features(self):

        return list(
            self.df.columns[:10]
        )

    # --------------------------------
    # Streamlit Output
    # --------------------------------

    def recommend(self):

        result = self.recommend_models()

        features = self.suggest_features()

        output = []

        output.append(
            f"📌 Problem Type: {result['problem_type']}"
        )

        output.append("")

        output.append("🤖 Recommended Models:")

        for model in result["recommended_models"]:

            output.append(f"✅ {model}")

        output.append("")

        output.append("📊 Suggested Features:")

        for feature in features:

            output.append(f"• {feature}")

        return output