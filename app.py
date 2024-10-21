import os
import streamlit as st
import pandas as pd
import numpy as np
from graphrag.retriever import get_neo4j_vector, retrieve_store_nodes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from llm_response.make_response import get_llm_response
from prompt.system_prompt import SYSTEM_PROMPT
from llm_response.langgraph_app import app, GraphState
from langchain_core.runnables import RunnableConfig



st.title("\"잘도 맛있수다!\"가 절로 나오는 제주도 맛집 추천! 🍊🍊")

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

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

            # response = retrieve_store_nodes(query)
            # print(f"response : \n{response}")

            placeholder = st.empty()
            
            # 임의로 response 추가 : 나중에 데이터 적재되면 활용할 예정            
            # for r in response :
            #     r.metadata['menu'] = {"메뉴1":"20000", "메뉴2":"25000"}
            #     r.metadata['Nearby tourist attractions'] = {"성산일출봉":"10분이내 거리", "섭지코지":"20분이내 거리"}

            # ai_msg = get_llm_response(query, response)
            placeholder.markdown(result_gs['final_answer'])

    message = {"role": "assistant", "content": result_gs['final_answer']}
    st.session_state.messages.append(message)