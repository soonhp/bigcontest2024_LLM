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

# Load BGE-M3-Korean model
tokenizer = AutoTokenizer.from_pretrained("upskyy/bge-m3-korean")
model = AutoModel.from_pretrained("upskyy/bge-m3-korean")

# Define mean pooling function
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# Function to get embeddings for a given text
def get_embedding(text):
    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**encoded_input)
    return mean_pooling(model_output, encoded_input["attention_mask"]).squeeze().tolist()

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
