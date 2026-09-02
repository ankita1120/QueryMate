"""
agent_manager.py

QueryMate AI Agent Manager

Connects Agent Router with all analysis modules.
"""


from agent_router import AgentRouter

from agent import DataAnalystAgent
from visualizer import DataVisualizer
from cleaner import DataCleaner
from ml_recommender import MLRecommender
from report_generator import ReportGenerator



class AgentManager:


    def __init__(
        self,
        df,
        api_key=None
    ):

        self.df = df

        self.api_key = api_key


        self.router = AgentRouter()


        self.data_agent = None


        if api_key:

            self.data_agent = DataAnalystAgent(
                df=df,
                api_key=api_key
            )



    def process(self, question):


        agent_type = (
            self.router
            .route(question)
        )


        # -------------------------
        # Data Analysis Agent
        # -------------------------

        if agent_type == "data":


            if self.data_agent:


                return (
                    self.data_agent
                    .ask(question)
                )


            return (
                "Gemini API key required "
                "for data analysis."
            )



        # -------------------------
        # Visualization Agent
        # -------------------------

        elif agent_type == "visualization":


            visualizer = DataVisualizer(
                self.df
            )


            charts = (
                visualizer
                .numeric_charts()
            )


            return {
                "type": "charts",
                "result": charts
            }



        # -------------------------
        # Cleaning Agent
        # -------------------------

        elif agent_type == "cleaning":


            cleaner = DataCleaner(
                self.df
            )


            return {

                "type": "cleaning",

                "missing":
                    cleaner.missing_values_report(),

                "duplicates":
                    cleaner.duplicate_report()
            }



        # -------------------------
        # ML Agent
        # -------------------------

        elif agent_type == "ml":


            recommender = MLRecommender(
                self.df
            )


            return {

                "type": "ml",

                "result":
                    recommender.recommend_models()
            }



        # -------------------------
        # Report Agent
        # -------------------------

        elif agent_type == "report":


            return {

                "type": "report",

                "message":
                "Report generation requested."

            }



        else:


            return (
                "Unable to understand request."
            )