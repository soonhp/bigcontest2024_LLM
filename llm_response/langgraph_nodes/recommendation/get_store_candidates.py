
from config import CONFIG
from graphrag.get_embedding_model import get_embedding_model
from llm_response.langgraph_graph_state import GraphState
from llm_response.utils.recomm_get_store_nodes.intent_guide import IntentGuide
from llm_response.utils.recomm_get_store_nodes.t2c import text_to_cypher_for_recomm
from llm_response.utils.recomm_get_store_nodes.token_check import token_check
from llm_response.utils.recomm_get_store_nodes.top_similar_stores import retrieve_top_similar_stores_pk
from llm_response.utils.recomm_get_store_nodes.utils import convert_markdown_to_html
from llm_response.utils.recomm_get_store_nodes.cypher_result_to_str import get_candidate_str, get_cypher_result_to_str

import streamlit as st
import re

from prompt.text_to_cypher_for_recomm import EXAMPLES_COMBINED, NEO4J_SCHEMA_RECOMM, TEXT_TO_CYPHER_FOR_RECOMM_TEMPLATE
from prompt.final_selecting_for_recomm import FINAL_SELECTING_FOR_RECOMM_v2

from concurrent.futures import ThreadPoolExecutor, as_completed
import time

embedding_model = get_embedding_model()  # 초기화된 모델을 재사용


def get_store_candidates(llm, graphdb_driver, store_retriever_rev_emb, store_retriever_grp_emb, state:GraphState):
    print(f"Get Store Candidates".ljust(100, '='))
    candidate_str = ''
    intent = state['intent']
    ig = IntentGuide()
    ig.add(f"<li style='margin-bottom: 8px;'>{convert_markdown_to_html(intent)}</li>")

    placeholder = st.empty()
    placeholder.markdown("> 조건을 만족하는 맛집 찾는 중...", unsafe_allow_html=True)
    
    # Text to Cypher
    state = text_to_cypher_for_recomm(llm, state)
    
    # Retrieve store nodes filtered by DB schema
    candidates_1st, summary, keys = graphdb_driver.execute_query(state['t2c_for_recomm'])
    query_embedding = embedding_model.embed_query(intent)
    if candidates_1st:
        placeholder.markdown(
            f"> {len(candidates_1st)}개의 후보 탐색 중...",
            unsafe_allow_html=True,
        )

        # Retrieve store nodes by review embedding search
        top_sim_stores = retrieve_top_similar_stores_pk(
            store_pk=[r['pk'] for r in candidates_1st], 
            query_embedding=query_embedding
            )

        # 정리
        top_sim_pks = [ts['pk'] for ts in top_sim_stores]
        candidates_2nd = [r for r in candidates_1st if r['pk'] in top_sim_pks]
        placeholder.markdown(
            f"> {len(candidates_2nd)}개의 후보 탐색 중...",
            unsafe_allow_html=True,
        )
        cypher_result_str = get_cypher_result_to_str(candidates_2nd, query_embedding, graphdb_driver, k=2)
        candidate_str += cypher_result_str
    
    lack_num = CONFIG.recomm_candidates_num - len(candidates_1st)
    # print("lack_num : ", lack_num)
    if lack_num:
        if state['subtype'] == 'purpose_and_visit_with' :
            review_retrieval = store_retriever_grp_emb.invoke(state['intent'])
            print("review_retrieval : ", review_retrieval)
        else : 
            review_retrieval = store_retriever_rev_emb.invoke(state['intent'])
            
        candidate_str += get_candidate_str(review_retrieval[:lack_num], query_embedding, graphdb_driver, use_unique_k=lack_num, state=state['subtype'], review_k=2)
        placeholder.markdown(
            f"> {len(candidates_1st) + len(review_retrieval)}개의 후보 탐색 중...",
            unsafe_allow_html=True,
        )
    

    # Token check
    state["candidate_str"] = token_check(candidate_str, state, llm, placeholder)
    place_holder_str = ''
    placeholder.markdown(place_holder_str, unsafe_allow_html=True)

    # Guide
    ig.close()
    st.markdown(ig.guide, unsafe_allow_html=True)
    state["final_answer"] = ig.guide + '\n'

    return state
