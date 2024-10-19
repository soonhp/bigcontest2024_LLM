import os
import streamlit as st
import pandas as pd
import numpy as np
from llm_response.make_response import get_llm_response
from llm_response.get_llm_model import get_llm_model  
from langchain.chains.retrieval import create_retrieval_chain
from graphrag.retriever import retrieve_store_nodes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from prompt.system_prompt import SYSTEM_PROMPT

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



if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            # response = get_llm_response(prompt)
            # rchain = create_retrieval_chain(retrieve_store_nodes, chain)
            # response = rchain.invoke({"input": query})
            response = retrieve_store_nodes(query)
            placeholder = st.empty()
            

            # 임의로 response 추가 : 나중에 데이터 적재되면 활용할 예정            
            for r in response :
                r.metadata['menu'] = {"메뉴1":"20000", "메뉴2":"25000"}
                r.metadata['Nearby tourist attractions'] = {"성산일출봉":"10분이내 거리", "섭지코지":"20분이내 거리"}

            ai_msg = get_llm_response(query, response)
            placeholder.markdown(ai_msg)

    message = {"role": "assistant", "content": ai_msg}
    st.session_state.messages.append(message)