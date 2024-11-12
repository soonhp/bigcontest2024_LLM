from langgraph.graph import END, StateGraph
from typing import List, TypedDict
from graphrag.retriever import get_neo4j_vector
from graphrag.graph_search import get_neo4j_vector_graph
from llm_response.conditional_decision.route_query import is_search_query
from llm_response.get_llm_model import get_llm_model
from llm_response.langgraph_graph_state import GraphState
from llm_response.langgraph_nodes.recommendation.final_formatting_for_recomm import final_formatting_for_recomm
from llm_response.langgraph_nodes.search.final_formatting import final_formatting_for_search
from llm_response.langgraph_nodes.recommendation.selecting import final_selecting_for_recomm
from llm_response.langgraph_nodes.recommendation.get_store_candidates import get_store_candidates
from llm_response.langgraph_nodes.search.retrieve_for_search_cypher import retrieve_for_search_cypher
from llm_response.langgraph_nodes.routing.route_and_intent_analysis import route_and_intent_analysis
from langgraph.graph import END
from utils import graphdb_driver
from config import CONFIG
from llm_response.langgraph_nodes.search.text_to_cypher_for_search import text_to_cypher_for_search

llm = get_llm_model()
store_retriever_rev_emb = get_neo4j_vector().as_retriever(search_kwargs={"k": CONFIG.store_retriever_rev_emb_k})
store_retriever_grp_emb = get_neo4j_vector_graph().as_retriever(search_kwargs={"k": CONFIG.store_retriever_rev_emb_k_grp})

workflow = StateGraph(GraphState)

# Nodes
## Routing & intent analysis node
workflow.add_node("route_and_intent_analysis", lambda state: route_and_intent_analysis(llm, state))

## Search query nodes
workflow.add_node("text_to_cypher_for_search", lambda state: text_to_cypher_for_search(llm, state))
workflow.add_node("retrieve_for_search_cypher", lambda state: retrieve_for_search_cypher(graphdb_driver, state))
workflow.add_node("final_formatting_for_search", lambda state: final_formatting_for_search(llm, graphdb_driver, state))

## Recomm query nodes
workflow.add_node("get_store_candidates", lambda state: get_store_candidates(llm, graphdb_driver, store_retriever_rev_emb, store_retriever_grp_emb, state))
workflow.add_node("final_selecting_for_recomm", lambda state: final_selecting_for_recomm(llm, state))
workflow.add_node("final_formatting_for_recomm", lambda state: final_formatting_for_recomm(graphdb_driver, state))

# Edges
## Conditional edges
workflow.add_conditional_edges(
    'route_and_intent_analysis',
    is_search_query,
    {
        'YES': 'text_to_cypher_for_search',
        'NO': 'get_store_candidates',
    }
)

## Search
workflow.add_edge('text_to_cypher_for_search', 'retrieve_for_search_cypher')
workflow.add_edge('retrieve_for_search_cypher', 'final_formatting_for_search')
workflow.add_edge('final_formatting_for_search', END)

## Recomm
workflow.add_edge('get_store_candidates', 'final_selecting_for_recomm')
workflow.add_edge('final_selecting_for_recomm', 'final_formatting_for_recomm')
workflow.add_edge('final_formatting_for_recomm', END)

workflow.set_entry_point("route_and_intent_analysis")
app = workflow.compile()
