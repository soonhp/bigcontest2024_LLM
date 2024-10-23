FINAL_FORMATTING_FOR_SEARCH = """Answer to the user's question refer to cypher query and the search result.

user's question : {query}

cypher query : {cypher}

search result : {search_result}


- Start by giving a clear and direct answer based on the search result.
- Elaborate on how the result was obtained and explain the reasons behind it (explained step by step).
- Use simple and friendly language that is easy for a general audience to understand.
- Exclude any mention of the Cypher query.
- Do not use asterisks for emphasis, and respond in Korean.

"""

"""
기존버전
- Explain how the result was derived with reasons.
- Not technically, but kindly to general people who questioned.
"""