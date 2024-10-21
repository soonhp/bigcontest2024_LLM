from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import os
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
import torch
from concurrent.futures import ThreadPoolExecutor

load_dotenv(find_dotenv())

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]

# Initialize the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password))

# Download the model and move it to GPU for faster computation
model = SentenceTransformer("upskyy/bge-m3-korean").to('cuda')

# Function to update embeddings in Neo4j with batching and threading for faster updates
def update_review_embeddings(batch_size=1024, update_batch_size=100):
    with driver.session() as session:
        # Query to get all reviews with no embeddings
        query = "MATCH (r:Review) WHERE r.textEmbedding IS NULL RETURN r.id AS id, r.storePk AS storePk, r.text AS text"
        results = session.run(query)
        results_list = list(results)

        # Thread pool for concurrent Neo4j updates
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Batch processing for embeddings
            for i in tqdm(range(0, len(results_list), batch_size), desc="Updating Embeddings"):
                batch_records = results_list[i:i + batch_size]

                # Prepare texts and ids for the batch
                texts = [record["text"] for record in batch_records]
                ids_storepks = [(record["id"], record["storePk"]) for record in batch_records]

                # Generate embeddings for the batch and keep them in GPU
                embeddings = model.encode(texts, batch_size=batch_size, convert_to_tensor=True)

                # Batch embeddings update to Neo4j
                for j in range(0, len(batch_records), update_batch_size):
                    update_batch_records = batch_records[j:j + update_batch_size]
                    update_batch_embeddings = embeddings[j:j + update_batch_size]

                    # Use a separate thread to update Neo4j in batches
                    executor.submit(update_neo4j_batch, update_batch_records, update_batch_embeddings, session)

# Function to update a batch of embeddings in Neo4j
def update_neo4j_batch(batch_records, batch_embeddings, session):
    for (record, embedding) in zip(batch_records, batch_embeddings):
        review_id = record["id"]
        store_pk = record["storePk"]
        embedding_list = embedding.cpu().tolist()

        update_query = """
        MATCH (r:Review {id: $review_id, storePk: $store_pk})
        SET r.textEmbedding = $embedding
        """
        session.run(update_query, review_id=review_id, store_pk=store_pk, embedding=embedding_list)

# Run the embedding update function
update_review_embeddings(batch_size=256, update_batch_size=25)

# Close the driver connection
driver.close()
