from typing import List, TypedDict


class GraphState(TypedDict):
    query: str
    query_type: str
    intent : List[str]

    t2c_for_search : str
    retrieval_result_for_search : str

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
    candidate: List[dict]
    recommendation: str
    status: str
    answer: str
    final_answer: str