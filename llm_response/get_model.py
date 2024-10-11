import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv



def get_model():

    load_dotenv(verbose=True)

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=os.environ['KYEONGCHAN_GEMINI_API_KEY']
    )
    return llm