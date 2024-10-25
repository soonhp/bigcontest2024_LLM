from llm_response.langgraph_graph_state import GraphState
from neo4j.exceptions import ServiceUnavailable

def retrieve_for_search_cypher(graphdb_driver, state:GraphState):
    print(f"[Search] Cypher result : neo4j 추출 결과".ljust(100, '-'))
    try:
        records, summary, keys = graphdb_driver.execute_query(state['t2c_for_search'])
        print(f"records : \n")

        record_dict_lst = []
        for r in records:
            record_dict_lst.append(dict(r))
            if 's' in r.keys():
                print(f"{dict(r['s'])}")
                print()

        print(f"record_dict_lst : {record_dict_lst}")
        state['record_dict_lst'] = record_dict_lst
    except ServiceUnavailable:
        state['record_dict_lst'] = """Retrieval failed because of the database connection issue temporally.
        Make your own answer for not providing information that sorry about this.."""

    return state
