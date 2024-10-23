from typing import Dict, List, TypedDict
from langchain_community.vectorstores.neo4j_vector import Neo4jVector


class GraphState(TypedDict):
    query: str
    query_type: str
    intent : List[str]

    t2c_for_search : str
    record_dict_lst : List[Dict]

    messages : List[Dict]
    candidate: List[str]
    selected_recommendations : Dict

    final_answer: str

    ###########################
    filter: str  # 메타 정보 필터링 쿼리
    type_: str  # 영화 질문 타입
    username: str
    id: str
    genre_ids: List[str]
    name: str
    profile: str
    movies: List[str]
    history: List[dict]
    
    recommendation: str
    status: str
    answer: str
    