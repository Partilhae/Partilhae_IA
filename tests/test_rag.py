import pytest

from src.rag import RAG, carregar_documentos, dividir_documentos


@pytest.fixture(scope="module")
def rag():
    return RAG()


def test_carregar_documentos():
    documentos = carregar_documentos()

    assert len(documentos) == 5


def test_dividir_documentos():
    documentos = carregar_documentos()
    chunks = dividir_documentos(documentos)

    assert len(chunks) == 28


def test_estrutura_dos_chunks():
    chunks = dividir_documentos(carregar_documentos())

    for chunk in chunks:
        assert chunk["fonte"]
        assert chunk["texto"]


@pytest.mark.parametrize("pergunta, fonte_esperada", [
    (
        "Quais alimentos podem ser doados?",
        "doacao_alimentos.md"
    ),
    (
        "Como devo armazenar alimentos perecíveis?",
        "conservacao_alimentos.md"
    ),
    (
        "Como faço uma solicitação pelo Partilhaê?",
        "partilhae.md"
    ),
    (
        "Como posso reduzir o desperdício de alimentos?",
        "desperdicio_alimentos.md"
    ),
    (
        "Como faço para doar pelo aplicativo?",
        "partilhae.md"
    )
])
def test_recuperar_contexto_relevante(
    rag, pergunta, fonte_esperada
):
    resultados = rag.buscar(pergunta)

    assert resultados
    assert resultados[0]["fonte"] == fonte_esperada


@pytest.mark.parametrize("pergunta", [
    "Quem ganhou a Copa do Mundo de 2022?",
    "Como instalar o Windows?",
    "Quais são os melhores jogos de futebol?"
])
def test_pergunta_fora_do_escopo(rag, pergunta):
    assert rag.buscar(pergunta) == []


def test_pergunta_vazia(rag):
    with pytest.raises(ValueError):
        rag.buscar("")


def test_top_k_invalido(rag):
    with pytest.raises(ValueError):
        rag.buscar("Doação de alimentos", top_k=0)


def test_limite_de_resultados(rag):
    resultados = rag.buscar("Doação de alimentos", top_k=2)

    assert 0 < len(resultados) <= 2


def test_similaridade_minima(rag):
    resultados = rag.buscar("Quais alimentos podem ser doados?")

    assert resultados

    for resultado in resultados:
        assert resultado["similaridade"] >= 0.35


def test_ordem_dos_resultados(rag):
    resultados = rag.buscar("Quais alimentos podem ser doados?")

    similaridades = [
        resultado["similaridade"]
        for resultado in resultados
    ]

    assert similaridades == sorted(similaridades, reverse=True)

def test_base_de_conhecimento_vazia():
    from unittest.mock import patch

    with patch("src.rag.carregar_documentos", return_value=[]):
        with pytest.raises(ValueError, match="Base de conhecimento vazia"):
            RAG()


def test_ignorar_secao_vazia():
    documentos = [
        {
            "fonte": "teste.md",
            "texto": "# Teste\n## \n## Conteúdo válido"
        }
    ]

    chunks = dividir_documentos(documentos)

    assert len(chunks) == 1
    assert chunks[0]["texto"] == "Conteúdo válido"


def test_ignorar_referencias_bibliograficas():
    documentos = [
        {
            "fonte": "teste.md",
            "texto": (
                "# Teste\n"
                "## Conteúdo\nTexto válido\n"
                "## Fonte\nReferência bibliográfica"
            )
        }
    ]

    chunks = dividir_documentos(documentos)

    assert len(chunks) == 1
    assert chunks[0]["texto"] == "Conteúdo\nTexto válido"


def test_pergunta_apenas_espacos(rag):
    with pytest.raises(ValueError):
        rag.buscar("   ")

def test_execucao_terminal():
    import runpy

    runpy.run_module("src.rag", run_name="__main__")