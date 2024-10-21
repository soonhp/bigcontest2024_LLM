from langgraph.graph import END, StateGraph
from typing import List, TypedDict
from llm_response.conditional_decision.route_query import is_search_query
from llm_response.get_llm_model import get_llm_model
from llm_response.langgraph_graph_state import GraphState
from llm_response.langgraph_nodes.final_formatting import final_formatting_for_search, final_formatting_for_recomm
from llm_response.langgraph_nodes.recommend import recommend
from llm_response.langgraph_nodes.retrieve_for_search_cypher import retrieve_for_search_cypher
from llm_response.langgraph_nodes.route_and_intent_analysis import route_and_intent_analysis
from langgraph.graph import END
from utils import graphdb_driver

from llm_response.langgraph_nodes.text_to_cypher_for_search import text_to_cypher_for_search

llm = get_llm_model()


workflow = StateGraph(GraphState)
# workflow.add_node("route_and_intent_analysis", route_and_intent_analysis)
workflow.add_node("route_and_intent_analysis", lambda state: route_and_intent_analysis(llm, state))
workflow.add_node("final_formatting_for_search", lambda state: final_formatting_for_search(llm, state))
workflow.add_node("final_formatting_for_recomm", final_formatting_for_recomm)
workflow.add_node("text_to_cypher_for_search", lambda state: text_to_cypher_for_search(llm, state))
workflow.add_node("retrieve_for_search_cypher", lambda state: retrieve_for_search_cypher(graphdb_driver, state))


# workflow.add_node("recommend", recommend)

workflow.add_conditional_edges(
    'route_and_intent_analysis',
    is_search_query,
    {
        'YES': 'text_to_cypher_for_search',
        'NO': 'final_formatting_for_recomm',
    }
)
workflow.add_edge('text_to_cypher_for_search', 'retrieve_for_search_cypher')
workflow.add_edge('retrieve_for_search_cypher', 'final_formatting_for_search')
workflow.add_edge('final_formatting_for_search', END)


workflow.set_entry_point("route_and_intent_analysis")
app = workflow.compile()