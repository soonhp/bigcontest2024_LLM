from graphrag.get_embedding_model import get_embedding_model
from llm_response.langgraph_graph_state import GraphState
import streamlit as st
import re

from prompt.text_to_cypher_for_recomm import EXAMPLES_COMBINED, NEO4J_SCHEMA_RECOMM, TEXT_TO_CYPHER_FOR_RECOMM_TEMPLATE
from utils import get_candidate_str
import time


# 마크다운에서 HTML로 변환하는 함수
def convert_markdown_to_html(text):
    # **bold** -> <b>bold</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

def text_to_cypher_for_recomm(llm, state:GraphState):
    print(f"Text2Cypher for SEARCH".ljust(100, '-'))
    response = llm.invoke(
        TEXT_TO_CYPHER_FOR_RECOMM_TEMPLATE.format(
            NEO4J_SCHEMA_RECOMM=NEO4J_SCHEMA_RECOMM,
            EXAMPLES_COMBINED=EXAMPLES_COMBINED, 
            query=state['query']
            )
    )
    print(f"# input_tokens count : {response.usage_metadata['input_tokens']}")
    cypher = response.content.replace('```', '').replace('cypher', '').strip()
    print(f"cypher : {cypher}")
    state['t2c_for_recomm'] = cypher
    return state

def get_store_candidates(llm, graphdb_driver, store_retriever_rev_emb, state:GraphState):
    placeholder = st.empty()
    placeholder.markdown("> 리뷰 검색중...", unsafe_allow_html=True)
    # Review similarity
    intent_guide = """
    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);">
        <h5 style="font-size: 16px; margin-bottom: 10px;">🔍 질문 의도 파악 및 알맞은 리뷰를 찾는 중...</h5>
        <ul style="list-style-type: none; padding-left: 0;">
    """
    review_candidates_lst = []
    # query에 대한 리뷰 CONFIG.store_retriever_rev_emb_k개 후보에 추가
    rev_sim_result = store_retriever_rev_emb.invoke(state['query'])
    for document in rev_sim_result:
        if document.metadata['pk'] not in [d.metadata['pk'] for d in review_candidates_lst]:  # 중복방지
            review_candidates_lst.append(document)

    # intent별 CONFIG.store_retriever_rev_emb_k개씩 후보에 추가
    for intent in state['intent']:
        converted_intent = convert_markdown_to_html(intent)  # 마크다운을 HTML로 변환
        intent_guide += f"<li style='margin-bottom: 8px;'>{converted_intent}</li>"
        rev_sim_result = store_retriever_rev_emb.invoke(intent)  # invoke는 동기적으로 실행되는 메서드
        for document in rev_sim_result:
            store_name = document.metadata['storeName']
            review_text = document.page_content  # 페이지 내용에 접근할 때는 page_content
            print(f"Store Name: {store_name}")
            print(f"Review Text: {review_text}")
            print()
            if document.metadata['pk'] not in [d.metadata['pk'] for d in review_candidates_lst]:  # 중복방지
                review_candidates_lst.append(document)

    state['candidate_str'] = get_candidate_str(review_candidates_lst)

    # Text2Cypher
    placeholder.markdown(
        f"리뷰 검색 결과 {len(review_candidates_lst)}개, 데이터 베이스 검색중...",
        unsafe_allow_html=True,
    )
    state = text_to_cypher_for_recomm(llm, state)
    records, summary, keys = graphdb_driver.execute_query(state['t2c_for_recomm'])
    # pk 기준 중복 제거
    records_drop_dup = []
    for r in records:
        if r['pk'] not in [d['pk'] for d in records_drop_dup]:
            records_drop_dup.append(r)
    embedding_model = get_embedding_model()
    query_embedding = embedding_model.embed_query(state['query'])
    state['candidate_str'] += '\n'
    for r in records_drop_dup:
        r_keys = r.keys()
        one_record_str = ''
        for key in r_keys:
            one_record_str += f"{key} : {str(r[key])[:100]}\n"
            if key == 'pk':
                reviews = retrieve_top_k_reviews(r[key], query_embedding, graphdb_driver, k=2)
                if reviews:
                    reviews_lst = [f"{ri}. {review['text'][:100]}" for ri, review in enumerate(reviews, start=1)]
                    one_record_str += f"리뷰 : {', '.join(reviews_lst)}\n"
        if '리뷰' in one_record_str:
            state["candidate_str"] += one_record_str
    placeholder.markdown(
        f"> 리뷰 검색 결과 후보 : {len(review_candidates_lst)}개, 데이터 베이스 검색 결과 후보 : { len(records_drop_dup)}개",
        unsafe_allow_html=True,
    )
    intent_guide += f"""  	</ul>
<h5 style="font-size: 16px;">⏳ 질문 조건을 만족하는 {len(review_candidates_lst) + len(records)}개의 후보 중에서 최적의 추천 결과 선별 중...</h5>

</div>"""
    st.markdown(intent_guide, unsafe_allow_html=True)

    return state


def retrieve_top_k_reviews(store_pk, query_embedding, driver, k=3):
    """
    특정 STORE 노드에 연결된 리뷰 중 유사한 TOP-K 리뷰를 반환합니다.
    """
    query = """
    MATCH (s:STORE {pk: $store_pk})-[:HAS_REVIEW]->(r:Review)
    WHERE r.textEmbedding IS NOT NULL
    RETURN r.text AS text, gds.similarity.cosine(r.textEmbedding, $query_embedding) AS similarity
    ORDER BY similarity DESC
    LIMIT $k
    """
    with driver.session() as session:
        result = session.run(
            query, store_pk=store_pk, query_embedding=query_embedding, k=k
        )
        return [
            {"text": record["text"], "similarity": record["similarity"]}
            for record in result
        ]
