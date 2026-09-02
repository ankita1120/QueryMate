"""
querymate_chatbot.py

Terminal chatbot + Streamlit compatible
"""

import os
from google import genai


class QueryMateChatbot:


    def __init__(self, api_key=None):

        self.api_key = (
            api_key
            or os.getenv("AQ.Ab8RN6LEVbTmVyBqcW9ad5G_LIHmgBJXqyJfxX4nd5botL-oXQ")
            #("AQ.Ab8RN6IMkHthTG5_Q6DGAonw_FPPo2WsZN4U2bIP7VLLytImCg")
        )

        self.client = genai.Client(
            api_key=self.api_key
        )


    def ask(self, question):

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=question
        )

        return response.text



# ---------------------------------
# Terminal mode only
# ---------------------------------

def run_terminal():

    bot = QueryMateChatbot()


    print("🤖 Welcome to QueryMate!")
    print("Type 'exit' to quit.\n")


    while True:

        question = input("You: ")


        if question.lower() == "exit":

            print("Goodbye!")

            break


        answer = bot.ask(question)


        print("\n🤖 QueryMate:")
        print(answer)
        print("-" * 60)



# Important:
# This runs only when you execute:
# python querymate_chatbot.py
#
# It will NOT run when Streamlit imports it.

if __name__ == "__main__":

    run_terminal()