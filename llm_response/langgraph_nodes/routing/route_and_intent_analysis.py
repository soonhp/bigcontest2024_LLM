from llm_response.langgraph_graph_state import GraphState
from prompt.routing_and_intent_analysis import ROUTE_INTT_PROMPT_TEMPLATE
import streamlit as st

def route_and_intent_analysis(llm, state: GraphState):
    print(f"Routing and intent analysis".ljust(100, '-'))
    print(f"query : {state['query']}")

    placeholder = st.empty()
    placeholder.markdown("> 질문 분류 중(검색/추천)...", unsafe_allow_html=True)

    route_response = llm.invoke(ROUTE_INTT_PROMPT_TEMPLATE.format(query=state["query"]))
    print(f"\n{route_response.content}")

    route_response_json = eval(
        route_response.content.replace("```", "").replace("json", "")
    )
    state["query_type"] = route_response_json["query_type"]
    state["intent"] = (
        route_response_json["intent"] if "intent" in route_response_json else None
    )
    if state["query_type"] == "search":
        placeholder.markdown(f"> {route_response_json['comment']}", unsafe_allow_html=True)
    if state["query_type"] == "recomm":
        placeholder.markdown(
            f"> {route_response_json['comment']}", unsafe_allow_html=True
        )
    return state
