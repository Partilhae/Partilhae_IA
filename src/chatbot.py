import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = os.getenv("GEMINI_MODEL")


def gerar_resposta(pergunta):
    resposta = client.models.generate_content(
        model=MODEL,
        contents=pergunta
    )

    return resposta.text


if __name__ == "__main__":
    pergunta = "Qual a importância da doação de alimentos?"

    print("Pergunta:", pergunta)
    print()
    print("Resposta:", gerar_resposta(pergunta))