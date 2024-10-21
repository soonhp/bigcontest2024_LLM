
from llm_response.langgraph_graph_state import GraphState
from prompt.firnal_formatting_for_search import FINAL_FORMATTING_FOR_SEARCH


def final_formatting_for_search(llm, state: GraphState):
   print(f"Final formatting for search".ljust(100, '-'))
   search_question_response = llm.invoke(
      FINAL_FORMATTING_FOR_SEARCH.format(
         query=state['query'], 
         cypher=state['t2c_for_search'], 
         search_result=state['retrieval_result_for_search']
         )
    )
   print(search_question_response.content)
   return state

def final_formatting_for_recomm(state: GraphState):
   print(f"Final formatting for recomm".ljust(100, '-'))
   print(f"Pass")
   return state

