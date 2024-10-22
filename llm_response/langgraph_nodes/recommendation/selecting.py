from llm_response.langgraph_graph_state import GraphState
from prompt.final_selecting_for_recomm import FINAL_SELECTING_FOR_RECOMM, FINAL_SELECTING_FOR_RECOMM_v2
from utils import get_candidate_str


def final_selecting_for_recomm(llm, state: GraphState):
   print("Final formatting for recomm".ljust(100, '-'))
   print("state['query'] : ", {state['query']})
   print("state['intent'] : ", {',\n'.join(state['intent'])})
   print("get_candidate_str(state['candidate']) : ", {get_candidate_str(state['candidate'])})
   prompt = FINAL_SELECTING_FOR_RECOMM_v2.format(
      query=state['query'], 
      intent=',\n'.join(state['intent']),
      candidates=get_candidate_str(state['candidate'])
   )
   print(f"prompt : {prompt}")
   response = llm.invoke(prompt)
   print(response.content)
   state['selected_recommendations'] = eval(response.content.replace('```', '').replace('json', '').strip())
   return state