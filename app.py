import os
import streamlit as st
import pandas as pd
import numpy as np
from graphrag.retriever import get_neo4j_vector, retrieve_store_nodes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from llm_response.make_response import get_llm_response
from llm_response.langgraph_app import app, GraphState
from langchain_core.runnables import RunnableConfig


st.title("혼저 옵서예!👋")
st.subheader("\"잘도 맛있수다!\"가 절로 나오는 제주도 맛집 추천 🍊")
st.write("")
st.write("여행 구성원 유형(가족, 친구 등) 및 연령대에 맞춘 제주도 맛집 추천해드려요")
st.write("")
with st.sidebar:
    st.title("🍊참신한! 제주 맛집")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

if query := st.chat_input("Say something"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)


config = RunnableConfig(recursion_limit=10, configurable={"thread_id": "movie"})
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # LangGraph
            gs = GraphState(query=query, messages=st.session_state.messages)
            result_gs = app.invoke(gs, config=config)
            placeholder = st.empty()

    if result_gs['final_answer']:
        message = {"role": "assistant", "content": result_gs['final_answer']}
        st.session_state.messages.append(message)
