
from llm_response.langgraph_graph_state import GraphState
from prompt.final_formatting_for_search import FINAL_FORMATTING_FOR_SEARCH


def final_formatting_for_search(llm, state: GraphState):
   print(f"Final formatting for search".ljust(100, '-'))
   response = llm.invoke(
      FINAL_FORMATTING_FOR_SEARCH.format(
         query=state['query'], 
         cypher=state['t2c_for_search'], 
         search_result=state['retrieval_result_for_search']
         )
    )
   print(response.content)
   state['final_answer'] = response.content
   return state
