from google import genai

class GeminiAnalyzer:

    def __init__(self, api_key):
        self.client = genai.Client(api_key="AQ.Ab8RN6LEVbTmVyBqcW9ad5G_LIHmgBJXqyJfxX4nd5botL-oXQ")

    def analyze(self, data, question):

        prompt = f"""
You are a Data Analyst.

Analyze this dataset:

{data}

User Question:

{question}

Provide:
- Clear answer
- Business insights
- Recommendations
"""

        response = self.client.models.generate_content(
            model="models/gemini-3.6-flash",   # <-- CHANGE THIS LINE
            contents=prompt
        )

        return response.text