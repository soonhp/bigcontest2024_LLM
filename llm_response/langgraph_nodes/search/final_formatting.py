from llm_response.langgraph_graph_state import GraphState
from prompt.final_formatting_for_search import FINAL_FORMATTING_FOR_SEARCH
import streamlit as st
from datetime import datetime


def final_formatting_for_search(llm, graphdb_driver, state: GraphState):
    # 스토어 정보 보류 #############################################################
    # 리뷰 데이터 부정적인 것도 많고, 이미지 넣는 것보단 llm이 만들어주는 마크다운 리스팅
    # 그대로 쓰는게 더 깔끔
    # # Store 정보(신한만 사용)
    # stores = []
    # enum = 1
    # for r in state['record_dict_lst']:
    #    if 's.MCT_NM' in r:
    #       records, summary, keys = graphdb_driver.execute_query(f"MATCH (s:STORE) WHERE s.MCT_NM = '{r['s.MCT_NM']}' RETURN s")
    #       node_dict = dict(records[0]['s'])
    #       print(node_dict)
    #       f"""## {enum}. {node_dict['MCT_NM']}
    #       - **유형**: {node_dict['MCT_TYPE']}
    #       - **주소**: {node_dict['ADDR']}
    #       - **오픈일**: {datetime.strptime(str(node_dict['OP_YMD']), '%Y%m%d').strftime('%Y년 %m월 %d일')}
    #       """
    #       enum += 1

    print(f"Final formatting for search".ljust(100, '='))
    response = llm.invoke(
      FINAL_FORMATTING_FOR_SEARCH.format(
         query=state['query'], 
         cypher=state['t2c_for_search'], 
         search_result=str(state['record_dict_lst'])
         )
    )
    print(response.content)
    print(state.keys())

    st.markdown(response.content, unsafe_allow_html=True)
    state["final_answer"] = response.content
    return state
