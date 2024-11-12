from llm_response.langgraph_graph_state import GraphState
from prompt.final_selecting_for_recomm import FINAL_SELECTING_FOR_RECOMM, FINAL_SELECTING_FOR_RECOMM_v2
from pprint import pprint


def final_selecting_for_recomm(llm, state: GraphState):
   print("Selecting for recomm".ljust(100, '='))

   prompt = FINAL_SELECTING_FOR_RECOMM_v2.format(
   query=state['query'], 
   intent=state['intent'],
   candidates=state['candidate_str']
   )

   response = llm.invoke(prompt)
   print(f"Candidates str : \n{state['candidate_str']}\n")
   print(f"input tokens : {response.usage_metadata['input_tokens']:,}")
   state["selected_recommendations"] = eval(
      response.content.replace("```", "").replace("json", "").strip()
   )
   pprint(f"Seleted : \n{state['selected_recommendations']}")
   return state
