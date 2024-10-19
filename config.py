import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    neo4j_url = os.environ["NEO4J_URI"]
    neo4j_user = os.environ["NEO4J_USERNAME"]
    neo4j_password = os.environ["NEO4J_PASSWORD"] 


CONFIG = Config()