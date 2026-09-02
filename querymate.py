from google import genai

client = genai.Client(api_key="AQ.Ab8RN6IMkHthTG5_Q6DGAonw_FPPo2WsZN4U2bIP7VLLytImCg"
                  #"AQ.Ab8RN6LEVbTmVyBqcW9ad5G_LIHmgBJXqyJfxX4nd5botL-oXQ"
                      )

while True:
    question = input("You: ")

    if question.lower() in ["exit", "quit"]:
        break

    response = client.models.generate_content(
        model="models/gemini-3.6-flash",
        contents=question
    )

    print("\nGemini:", response.text)