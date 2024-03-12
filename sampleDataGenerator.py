import PyPDF2
import openai
import os

api_key = os.getenv("API_KEY")
openai.api_key = api_key

def pdf_extractor(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text += page.extract_text()
    return text

pdf_path1 = 'cleansample1.pdf'

extracted_text1 = pdf_extractor(pdf_path1)

prompt = "You will be provided two different texts. Conduct an analysis of them by finding similarities, differences, contradictions, etc between the two texts. Your response should be detailed, concise, and clear. The tone should be that of a clinical diagnosis. Use as few words as necessary without sacrificing quality. Also provide a concise summary of each text. Speak formally. If you find contradictions, attempt to specify the author on either side of the contradiction and offer as much insight as possible, but make it clear that you are unsure who the author is. And if you cannot identify the author, just say so. Use bulletpoints. And for each summary, list the three most important idea in addition to a paragraph with a summary. And use bullet point format for the similarities and differences. Here's the first one: " + extracted_text1

response1 = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0
)
# print(response)
print(response1['choices'][0]['message']['content'])