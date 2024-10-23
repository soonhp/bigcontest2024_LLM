from llm_response.langgraph_graph_state import GraphState
import streamlit as st
import re
# 마크다운에서 HTML로 변환하는 함수
def convert_markdown_to_html(text):
    # **bold** -> <b>bold</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    return text

def get_store_candidates(graphdb_driver, store_retriever_rev_emb, state:GraphState):
    # Review similarity
    intent_guide = """
    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);">
        <h5 style="font-size: 16px; margin-bottom: 10px;">🔍 질문 의도 파악 및 알맞은 리뷰를 찾는 중...</h5>
        <ul style="list-style-type: none; padding-left: 0;">
    """

    candidates = []
    # query에 대한 리뷰 CONFIG.store_retriever_rev_emb_k개 후보에 추가
    rev_sim_result = store_retriever_rev_emb.invoke(state['query'])
    for document in rev_sim_result:
        if document.metadata['pk'] not in [d.metadata['pk'] for d in candidates]:  # 중복방지
            candidates.append(document)

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
            if document.metadata['pk'] not in [d.metadata['pk'] for d in candidates]:  # 중복방지
                candidates.append(document)

    intent_guide += f"""  	</ul>
    <h5 style="font-size: 16px;">⏳ 위 조건을 만족하는 {len(candidates)}개의 후보 중에서 최적의 추천 결과 선별 중...</h5>
    
</div>"""

    st.markdown(intent_guide, unsafe_allow_html=True)
    print(f"intent_guide : {intent_guide}")

    state['candidate'] = candidates

    

    # Text2Cypher

    


    return state
    
        
    