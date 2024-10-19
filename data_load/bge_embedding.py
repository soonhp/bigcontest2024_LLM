from sentence_transformers import SentenceTransformer

from neo4j import GraphDatabase
from transformers import AutoTokenizer, AutoModel
import torch
import os
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"] 

# Initialize the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Download from the 🤗 Hub
model = SentenceTransformer("upskyy/bge-m3-korean")

# Function to get embeddings for a given text
def get_embedding(text):
    text_embeddings = model.encode(text).squeeze().tolist()
    return text_embeddings

# Function to update embeddings in Neo4j
def update_review_embeddings():
    with driver.session() as session:
        # Query to get all reviews
        query = "MATCH (r:Review) WHERE r.textEmbedding IS NULL RETURN r.id AS id, r.storePk AS storePk, r.text AS text"
        results = session.run(query)
        results_list = list(results)

        # Iterate through each review and update its embedding
        for record in tqdm(results_list, desc="Updating Embeddings") :
            review_id = record["id"]
            store_pk = record["storePk"]
            review_text = record["text"]

            # Generate the embedding for the review text
            embedding = get_embedding(review_text)

            # Update the Review node with the embedding
            update_query = """
            MATCH (r:Review {id: $review_id, storePk: $store_pk})
            SET r.textEmbedding = $embedding
            """
            session.run(update_query, review_id=review_id, store_pk=store_pk, embedding=embedding)

# Run the embedding update function
update_review_embeddings()

# Close the driver connection
driver.close()
