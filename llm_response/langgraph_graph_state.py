from typing import Dict, List, TypedDict


class GraphState(TypedDict):
    query: str
    query_type: str
    subtype : str
    intent : List[str]
    t2c_for_search : str
    record_dict_lst : List[Dict]
    messages : List[Dict]
    t2c_for_recomm : str
    candidate_str: str
    selected_recommendations : Dict
    final_answer: str