from typing import Dict, List, TypedDict
from langchain_community.vectorstores.neo4j_vector import Neo4jVector


class GraphState(TypedDict):
    query: str
    query_type: str
    intent : List[str]

    t2c_for_search : str
    record_dict_lst : List[Dict]

    messages : List[Dict]
    t2c_for_recomm : str
    candidate_str: str
    selected_recommendations : Dict

    final_answer: str