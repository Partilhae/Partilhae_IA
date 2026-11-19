import streamlit as st

from src.chatbot import Chatbot


st.set_page_config(
    page_title="Assistente Partilhaê",
    page_icon="🤝",
    layout="centered"
)


@st.cache_resource
def carregar_chatbot():
    return Chatbot()


st.title("🤝 Assistente Partilhaê")

st.caption(
    "Inteligência artificial a serviço da solidariedade."
)

st.info(
    "Tire suas dúvidas sobre doações, conservação de "
    "alimentos e funcionamento do Partilhaê."
)

chatbot = carregar_chatbot()


if "mensagens" not in st.session_state:
    st.session_state.mensagens = []


with st.sidebar:
    st.header("Sobre o assistente")

    st.write(
        "O assistente utiliza IA generativa e RAG para "
        "fornecer orientações baseadas em documentos."
    )

    st.caption("Modelo: Gemini 3.5 Flash-Lite")

    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.mensagens = []
        st.rerun()

    st.warning(
        "O assistente possui caráter informativo e não "
        "substitui avaliações sanitárias profissionais."
    )


for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])


pergunta = st.chat_input("Digite sua pergunta...")


if pergunta:
    st.session_state.mensagens.append({
        "role": "user",
        "content": pergunta
    })

    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando a base de conhecimento..."):
            try:
                resultado = chatbot.gerar_resposta(pergunta)

                resposta = resultado["resposta"]

                st.markdown(resposta)

                st.session_state.mensagens.append({
                    "role": "assistant",
                    "content": resposta
                })

            except Exception:
                st.error(
                    "Não foi possível gerar uma resposta. "
                    "Tente novamente em alguns instantes."
                )