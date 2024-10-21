from llm_response.langgraph_graph_state import GraphState


def is_search_query(state: GraphState):
    print(f"route_query edge")
    if state['query_type'] == 'search':
        return 'YES'
    elif state['query_type'] == 'recomm':
        return 'NO'
    else:
        return 'NO'