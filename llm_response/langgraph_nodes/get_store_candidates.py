from llm_response.langgraph_graph_state import GraphState
import streamlit as st

def get_store_candidates(graphdb_driver, retriever, state:GraphState):
    # Review similarity
    st.markdown(f"<small>아래와 같은 조건을 만족하는 식당 리뷰를 찾는 중...</small>", unsafe_allow_html=True)
    candidates = []
    for intent in state['intent']:
        st.markdown(f"<small>{intent}</small>", unsafe_allow_html=True)

        rev_sim_result = retriever.invoke(intent)  # invoke는 동기적으로 실행되는 메서드
        document = rev_sim_result[0]
        store_name = document.metadata['storeName']
        store_image_kakao = document.metadata['store_Image']['kakao']
        review_text = document.page_content  # 페이지 내용에 접근할 때는 page_content

        print(f"Store Name: {store_name}")
        print(f"Store Image (Kakao): {store_image_kakao}")
        print(f"Review Text: {review_text}")
        if document.metadata['pk'] not in [d.metadata['pk'] for d in candidates]:  # 중복방지
            candidates.append(document)

    st.markdown(f"<small>{len(candidates)}개의 후보 중에서 최적의 추천 결과 선별 중...</small>", unsafe_allow_html=True)

    state['candidate'] = candidates

    # Text2Cypher


    return state
    
        
    