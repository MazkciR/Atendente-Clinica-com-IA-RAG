import time

import streamlit as st

from llm import carregar_prompt, chamar_llm, montar_pergunta

st.title("Atendente virtual - Clínica Exemplo")

VERSOES = ["v1", "v2", "v3", "v4"]
versao = st.sidebar.selectbox("Versão do prompt", VERSOES, index=3)
st.sidebar.caption("v4 usa RAG: busca só os trechos da FAQ relevantes para a pergunta.")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []


def mostrar(m):
    st.write(m["texto"])
    if m.get("trechos"):
        with st.expander("Trechos da FAQ usados (RAG)"):
            for t in m["trechos"]:
                st.caption(f"[{t['codigo']}] distância {t['distancia']:.2f}")


def responder(versao, pergunta):
    """Gera a resposta; tenta de novo se a API estiver instável (503)."""
    for tentativa in range(3):
        try:
            prompt = carregar_prompt(versao, pergunta)
            return chamar_llm(prompt, montar_pergunta(versao, pergunta))
        except Exception:
            if tentativa == 2:
                return "Desculpe, o serviço está instável agora. Tente de novo em instantes."
            time.sleep(3)


for m in st.session_state.mensagens:
    with st.chat_message(m["papel"]):
        mostrar(m)

pergunta = st.chat_input("Digite sua dúvida")

if pergunta:
    st.session_state.mensagens.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    trechos = []
    if versao == "v4":
        try:
            from rag import buscar

            trechos = buscar(pergunta, k=3)
        except Exception:
            trechos = []

    with st.spinner("Pensando..."):
        resposta = responder(versao, pergunta)

    msg = {"papel": "assistant", "texto": resposta, "trechos": trechos}
    st.session_state.mensagens.append(msg)
    with st.chat_message("assistant"):
        mostrar(msg)