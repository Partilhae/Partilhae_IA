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

    def buscar(self, pergunta, top_k=3):
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
            resultados.append({
                "fonte": self.chunks[indice]["fonte"],
                "texto": self.chunks[indice]["texto"],
                "similaridade": float(similaridades[indice])
            })

        return resultados


if __name__ == "__main__":
    rag = RAG()

    print("Documentos carregados:", len(rag.documentos))
    print("Chunks gerados:", len(rag.chunks))

    pergunta = "Quais alimentos podem ser doados?"

    print("\nPergunta:", pergunta)

    resultados = rag.buscar(pergunta)

    for resultado in resultados:
        print("\nFonte:", resultado["fonte"])
        print(f"Similaridade: {resultado['similaridade']:.4f}")
        print("Texto:", resultado["texto"])