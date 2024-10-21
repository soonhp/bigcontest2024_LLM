from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import os
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
import torch

load_dotenv(find_dotenv())

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]

# Initialize the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Download the model
model = SentenceTransformer("upskyy/bge-m3-korean")

# Function to update embeddings in Neo4j with batching
def update_review_embeddings(batch_size=1024):
    with driver.session() as session:
        # Query to get all reviews with no embeddings
        query = "MATCH (r:Review) WHERE r.textEmbedding IS NULL RETURN r.id AS id, r.storePk AS storePk, r.text AS text"
        results = session.run(query)
        results_list = list(results)

        # Batch processing for embeddings
        for i in tqdm(range(0, len(results_list), batch_size), desc="Updating Embeddings"):
            batch_records = results_list[i:i + batch_size]

            # Prepare texts and ids for the batch
            texts = [record["text"] for record in batch_records]
            ids_storepks = [(record["id"], record["storePk"]) for record in batch_records]

            # Generate embeddings for the batch and keep them in GPU
            embeddings = model.encode(texts, batch_size=batch_size, convert_to_tensor=True)

            # Update each review with its embedding
            for (review_id, store_pk), embedding in zip(ids_storepks, embeddings):
                update_query = """
                MATCH (r:Review {id: $review_id, storePk: $store_pk})
                SET r.textEmbedding = $embedding
                """
                session.run(update_query, review_id=review_id, store_pk=store_pk, embedding=embedding.cpu().tolist())  # Only move to CPU at the final step

# Run the embedding update function
update_review_embeddings(batch_size=1024)

# Close the driver connection
driver.close()
