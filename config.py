import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    neo4j_url = os.environ["NEO4J_URI"]
    neo4j_user = os.environ["NEO4J_USERNAME"]
    neo4j_password = os.environ["NEO4J_PASSWORD"] 
    gemini_api_key = os.environ["KYEONGCHAN_GEMINI_API_KEY"]
    store_retriever_rev_emb_k = 2
    recomm_select_k = 2

CONFIG = Config()