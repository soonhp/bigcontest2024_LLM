from graphrag.get_embedding_model import get_embedding_model
from graphrag.graph_search import retrieve_top_k_stores_by_review_graph_embedding, process_review_node
from llm_response.langgraph_graph_state import GraphState
from llm_response.utils.recomm_get_store_nodes.intent_guide import IntentGuide
from llm_response.utils.recomm_get_store_nodes.t2c import text_to_cypher_for_recomm
from llm_response.utils.recomm_get_store_nodes.top_similar_stores import retrieve_top_similar_stores_pk
from llm_response.utils.recomm_get_store_nodes.utils import convert_markdown_to_html
from llm_response.utils.recomm_get_store_nodes.cypher_result_to_str import get_cypher_result_to_str


import streamlit as st
import re

from prompt.text_to_cypher_for_recomm import EXAMPLES_COMBINED, NEO4J_SCHEMA_RECOMM, TEXT_TO_CYPHER_FOR_RECOMM_TEMPLATE
from utils import get_candidate_str
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

embedding_model = get_embedding_model()  # 초기화된 모델을 재사용


def get_store_candidates(llm, graphdb_driver, store_retriever_rev_emb, store_retriever_grp_emb, state:GraphState):
    print(f"Get Store Candidates".ljust(100, '-'))
    intent = state['intent']
    ig = IntentGuide()
    ig.add(f"<li style='margin-bottom: 8px;'>{convert_markdown_to_html(intent)}</li>")

    placeholder = st.empty()
    placeholder.markdown("> 리뷰 검색중...", unsafe_allow_html=True)
    
    # Text to Cypher
    state = text_to_cypher_for_recomm(llm, state)
    
    # Retrieve store nodes filtered by DB schema
    candidates_1st, summary, keys = graphdb_driver.execute_query(state['t2c_for_recomm'])
    placeholder.markdown(
        f"> {len(candidates_1st)}개의 후보 탐색 중...",
        unsafe_allow_html=True,
    )

    # Retrieve store nodes by review embedding search
    query_embedding = embedding_model.embed_query(intent)
    top_sim_stores = retrieve_top_similar_stores_pk(store_pk=[r['pk'] for r in candidates_1st], query_embedding=query_embedding)
    print(f"top sim scores : {top_sim_stores}")
    top_sim_pks = [ts['pk'] for ts in top_sim_stores]
    candidates_2nd = [r for r in candidates_1st if r['pk'] in top_sim_pks]
    placeholder.markdown(
        f"> {len(candidates_2nd)}개의 후보 탐색 중...",
        unsafe_allow_html=True,
    )

    cypher_result_str = get_cypher_result_to_str(candidates_2nd, query_embedding, graphdb_driver, k=2)
    state['candidate_str'] = cypher_result_str

    # Guide
    place_holder_str = ''
    placeholder.markdown(place_holder_str, unsafe_allow_html=True)
    ig.close(num_canidates=len(candidates_2nd))
    st.markdown(ig.guide, unsafe_allow_html=True)
    state["final_answer"] = ig.guide + '\n'


    # GraphEmbedding similarity
    graph_candidates_lst = []
    grp_sim_result = store_retriever_grp_emb.invoke(state['query'])
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_review_node, review, top_k_reviews=1)
            for review in grp_sim_result
        ]
        for future in as_completed(futures):
            result = future.result()
            if result:
                graph_candidates_lst.append(result)

    return state
