from unittest.mock import patch, MagicMock

import pytest

from src.chatbot import Chatbot


@pytest.fixture
def chatbot():
    with patch("src.chatbot.RAG"), \
         patch("src.chatbot.genai.Client"):

        yield Chatbot()


@pytest.fixture
def contexto():
    return [
        {
            "fonte": "doacao_alimentos.md",
            "texto": "Alimentos dentro do prazo de validade.",
            "similaridade": 0.83
        },
        {
            "fonte": "desperdicio_alimentos.md",
            "texto": "Doação de alimentos excedentes.",
            "similaridade": 0.71
        }
    ]


def configurar_resposta(chatbot, contexto):
    chatbot.rag.buscar.return_value = contexto

    resposta = MagicMock()
    resposta.text = "Alimentos próprios para consumo podem ser doados."

    chatbot.client.models.generate_content.return_value = resposta


def test_gerar_resposta(chatbot, contexto):
    configurar_resposta(chatbot, contexto)

    resultado = chatbot.gerar_resposta(
        "Quais alimentos podem ser doados?"
    )

    assert resultado["resposta"]
    assert resultado["contexto"] == contexto


def test_retornar_fontes(chatbot, contexto):
    configurar_resposta(chatbot, contexto)

    resultado = chatbot.gerar_resposta("Como doar alimentos?")

    assert resultado["fontes"] == [
        "doacao_alimentos.md",
        "desperdicio_alimentos.md"
    ]


def test_fontes_sem_duplicacao(chatbot, contexto):
    contexto.append(contexto[0].copy())

    configurar_resposta(chatbot, contexto)

    resultado = chatbot.gerar_resposta("Como doar alimentos?")

    assert len(resultado["fontes"]) == 2


def test_pergunta_vazia(chatbot):
    with pytest.raises(ValueError):
        chatbot.gerar_resposta("")

    chatbot.rag.buscar.assert_not_called()


def test_pergunta_apenas_espacos(chatbot):
    with pytest.raises(ValueError):
        chatbot.gerar_resposta("   ")


def test_sem_contexto_relevante(chatbot):
    chatbot.rag.buscar.return_value = []

    resultado = chatbot.gerar_resposta(
        "Como instalar o Windows?"
    )

    assert "Não encontrei informações relevantes" in resultado["resposta"]
    assert resultado["fontes"] == []
    assert resultado["contexto"] == []


def test_nao_chamar_gemini_sem_contexto(chatbot):
    chatbot.rag.buscar.return_value = []

    chatbot.gerar_resposta("Quem ganhou a Copa?")

    chatbot.client.models.generate_content.assert_not_called()


def test_contexto_enviado_ao_gemini(chatbot, contexto):
    configurar_resposta(chatbot, contexto)

    pergunta = "Quais alimentos podem ser doados?"

    chatbot.gerar_resposta(pergunta)

    argumentos = (
        chatbot.client.models.generate_content.call_args.kwargs
    )

    prompt = argumentos["contents"]

    assert pergunta in prompt

    for trecho in contexto:
        assert trecho["texto"] in prompt
        assert trecho["fonte"] in prompt


def test_chamada_ao_rag(chatbot, contexto):
    configurar_resposta(chatbot, contexto)

    pergunta = "Como doar alimentos?"

    chatbot.gerar_resposta(pergunta)

    chatbot.rag.buscar.assert_called_once_with(
        pergunta,
        top_k=3
    )


def test_erro_na_api(chatbot, contexto):
    chatbot.rag.buscar.return_value = contexto

    chatbot.client.models.generate_content.side_effect = (
        RuntimeError("Erro na API")
    )

    with pytest.raises(RuntimeError):
        chatbot.gerar_resposta("Como doar alimentos?")

def test_execucao_terminal():
    import runpy

    resposta = MagicMock()
    resposta.text = "Resposta de teste."

    contexto = [
        {
            "fonte": "doacao_alimentos.md",
            "texto": "Orientações sobre doações.",
            "similaridade": 0.85
        }
    ]

    with patch("src.rag.RAG") as mock_rag, \
         patch("google.genai.Client") as mock_client, \
         patch("builtins.input", side_effect=[
             "",
             "Quais alimentos podem ser doados?",
             "Como instalar o Windows?",
             "sair"
         ]):

        mock_rag.return_value.buscar.side_effect = [
            contexto,
            []
        ]

        mock_client.return_value.models.generate_content.return_value = (
            resposta
        )

        runpy.run_module(
            "src.chatbot",
            run_name="__main__"
        )