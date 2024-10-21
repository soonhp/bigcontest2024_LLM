from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate

from llm_response.get_llm_model import get_llm_model


llm = get_llm_model()

""" 
기존 경찬님 버전
def get_llm_response(user_input):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that recommeds must-go restaurants in Jeju island, Korea. Answer only in Korean.",
            ),
            ("human", "{user_input}"),
        ]
    )

    chain = prompt | llm

    ai_msg = chain.invoke({"user_input": user_input})

    return ai_msg.content
"""

"""
선진버전 : 1020
"""

def get_llm_response(query, response):

    prompt_template = f"""
    You're a chatbot that suggests stores based on user requests.

    TASK:
    1. Consider the user's needs.
    2. Suggest up to three suitable restaurants from the provided context.
    3. Ensure each recommendation truly fits the user's needs; if not don't recommend.
    4. Justify each suggestion without quoting reviews directly.
    5. Include each restaurant's image using markdown and change width of 200px (ignore if NaN), rating (ignore if NaN), and menu (ignore if NaN).
    6. Mention 'Nearby tourist attractions' for each restaurant.

    QUESTION: {query}

    CONTEXT: {response}

    ANSWER:"
    """

    ai_msg = llm.invoke(prompt_template)

    return ai_msg.content