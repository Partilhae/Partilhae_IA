from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


CAMINHO_DOCUMENTOS = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "documentos"
)

MODELO_EMBEDDING = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


def carregar_documentos():
    documentos = []

    for arquivo in sorted(CAMINHO_DOCUMENTOS.glob("*.md")):
        texto = arquivo.read_text(encoding="utf-8")

        documentos.append({
            "fonte": arquivo.name,
            "texto": texto
        })

    return documentos


def dividir_documentos(documentos):
    chunks = []

    for documento in documentos:
        secoes = documento["texto"].split("\n## ")

        for secao in secoes[1:]:
            secao = secao.strip()

            if secao.startswith(("Fonte\n", "Fontes\n")):
                continue

            if secao:
                chunks.append({
                    "fonte": documento["fonte"],
                    "texto": secao
                })

    return chunks


class RAG:
    def __init__(self):
        self.documentos = carregar_documentos()
        self.chunks = dividir_documentos(self.documentos)

        if not self.chunks:
            raise ValueError("Base de conhecimento vazia.")

        self.modelo = SentenceTransformer(MODELO_EMBEDDING)

        textos = [chunk["texto"] for chunk in self.chunks]

        self.embeddings = self.modelo.encode(
            textos,
            normalize_embeddings=True
        )

    def buscar(self, pergunta, top_k=3, min_similarity=0.35):
        if not pergunta.strip():
            raise ValueError("A pergunta não pode estar vazia.")

        if top_k < 1:
            raise ValueError("top_k deve ser maior que zero.")

        embedding_pergunta = self.modelo.encode(
            pergunta,
            normalize_embeddings=True
        )

        similaridades = np.dot(
            self.embeddings,
            embedding_pergunta
        )

        indices = np.argsort(similaridades)[::-1][:top_k]

        resultados = []

        for indice in indices:
            similaridade = float(similaridades[indice])

            if similaridade < min_similarity:
                continue

            resultados.append({
                "fonte": self.chunks[indice]["fonte"],
                "texto": self.chunks[indice]["texto"],
                "similaridade": similaridade
            })

        return resultados


if __name__ == "__main__":
    rag = RAG()

    print("Documentos carregados:", len(rag.documentos))
    print("Chunks gerados:", len(rag.chunks))

    perguntas = [
        "O que é o Partilhaê?",
        "Como funciona o Partilhaê?",
        "Como faço para doar alimentos?",
        "Como posso solicitar ajuda?",
        "Quem ganhou a Copa do Mundo de 2022?",
        "Como instalar o Windows?",
        "Qual a diferença entre ajuda específica e qualquer ajuda?",
        "Posso cancelar uma solicitação?",
        "oi, to precisando de comida pra minha familia, como q eu faço pra pedir ajuda?",
    ]

    for pergunta in perguntas:
        print("\nPergunta:", pergunta)

        resultados = rag.buscar(pergunta, top_k=3)

        if not resultados:
            print("Nenhum contexto relevante encontrado.")
            continue

        for resultado in resultados:
            print("\nFonte:", resultado["fonte"])
            print(f"Similaridade: {resultado['similaridade']:.4f}")
            print("Texto:", resultado["texto"])