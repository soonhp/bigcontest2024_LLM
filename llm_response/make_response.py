from langchain_core.prompts import ChatPromptTemplate
from llm_response.get_llm_model import get_llm_model


llm = get_llm_model()


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
