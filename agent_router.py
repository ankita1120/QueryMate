"""
agent_router.py

QueryMate AI Agent Router

Routes user requests to the appropriate AI module.
"""


class AgentRouter:

    def __init__(self):

        self.agents = {

            # ---------------------------------
            # Data Analysis
            # ---------------------------------
            "data": [

                "analyze",
                "analysis",
                "insight",
                "summary",

                "average",
                "mean",
                "sum",
                "total",
                "count",

                "maximum",
                "minimum",
                "max",
                "min",

                "highest",
                "lowest",

                "top",
                "bottom",

                "compare",
                "calculate",
                "find",
                "show",

                "sales",
                "revenue",
                "profit",
                "customer",
                "product"

            ],

            # ---------------------------------
            # Visualization
            # ---------------------------------
            "visualization": [

                "chart",
                "plot",
                "graph",
                "visual",
                "visualization",

                "dashboard",
                "trend",

                "histogram",
                "bar",
                "line",
                "scatter",
                "pie",
                "heatmap"

            ],

            # ---------------------------------
            # Machine Learning
            # ---------------------------------
            "ml": [

                "machine learning",
                "ml",

                "predict",
                "prediction",
                "forecast",

                "model",

                "classification",
                "classifier",

                "regression",
                "regressor",

                "cluster",
                "clustering"

            ],

            # ---------------------------------
            # Data Cleaning
            # ---------------------------------
            "cleaning": [

                "clean",
                "cleaning",

                "missing",
                "null",

                "duplicate",

                "remove",

                "fix",

                "outlier"

            ],

            # ---------------------------------
            # Report Generation
            # ---------------------------------
            "report": [

                "report",
                "pdf",

                "download",

                "export",

                "generate report",

                "analysis report"

            ]

        }

    # ---------------------------------
    # Route Question
    # ---------------------------------

    def route(self, question):

        question = question.lower().strip()

        for agent_name, keywords in self.agents.items():

            for keyword in keywords:

                if keyword in question:

                    return agent_name

        # Default Agent
        return "data"