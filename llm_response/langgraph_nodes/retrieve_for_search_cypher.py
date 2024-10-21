from llm_response.langgraph_graph_state import GraphState


def retrieve_for_search_cypher(graphdb_driver, state:GraphState):
    print(f"Cypher result".ljust(100, '-'))
    records, summary, keys = graphdb_driver.execute_query(state['t2c_for_search'])
    print(f"records : \n{records}")
    print(f"summary : \n{summary}")
    print(f"keys : \n{keys}")

    record_str_lst = []
    for record in records:
        record_str_lst.append(", ".join([f"{k} : {v}" for k, v in record.items()]))
    search_result = '\n'.join(record_str_lst)
    print(search_result)

    state['retrieval_result_for_search'] = search_result

    return state
