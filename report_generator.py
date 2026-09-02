"""
report_generator.py

Generate QueryMate AI Data Analyst reports
"""

from datetime import datetime


class ReportGenerator:

    def __init__(
        self,
        overview,
        profile,
        ml_result=None,
        insights=None
    ):

        self.overview = overview
        self.profile = profile
        self.ml_result = ml_result
        self.insights = insights


    def generate_text_report(self):

        report = []

        report.append(
            "🤖 QueryMate AI Data Analyst Report"
        )

        report.append(
            f"Generated: {datetime.now()}"
        )


        report.append(
            "\n📊 Dataset Overview"
        )


        for key, value in self.overview.items():

            report.append(
                f"{key}: {value}"
            )


        report.append(
            "\n🔍 Data Profile"
        )


        report.append(
            f"Rows: {self.profile.get('rows')}"
        )

        report.append(
            f"Columns: {self.profile.get('columns')}"
        )

        report.append(
            f"Duplicates: {self.profile.get('duplicates')}"
        )


        if self.ml_result:

            report.append(
                "\n🤖 ML Recommendations"
            )

            report.append(
                f"Problem Type: {self.ml_result.get('problem_type')}"
            )


            for model in self.ml_result.get(
                "recommended_models",
                []
            ):

                report.append(
                    f"- {model}"
                )


        if self.insights:

            report.append(
                "\n🧠 AI Insights"
            )

            report.append(
                str(self.insights)
            )


        return "\n".join(report)