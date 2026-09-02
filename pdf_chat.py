class PDFChat:

    def __init__(self, pdf_file):
        self.pdf_file = pdf_file


    def ask(self, question):

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=question
        )

        return response.text
