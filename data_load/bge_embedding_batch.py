from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import os
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
import torch
from concurrent.futures import ThreadPoolExecutor
import time

load_dotenv(find_dotenv())

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]

# Initialize the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password), max_connection_lifetime=200)

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
            futures = []  # Future 객체를 저장할 리스트
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
                    future = executor.submit(update_neo4j_batch, update_batch_records, update_batch_embeddings, session)
                    futures.append(future)  # Future 객체를 리스트에 추가
                    # 각 업데이트 사이에 0.5초 대기
                    time.sleep(0.5)  # 추가된 코드
            # 모든 Future 객체의 상태를 확인하고 완료될 때까지 대기
            for j, future in enumerate(futures):
                future.result()  # 실제로 적재가 완료될 때까지 대기
                # 적재가 완료되었는지 확인하기 위해 로그를 출력
                if future.done() and not future.exception():
                    print(f"Batch starting at index {i} successfully updated.")
                else:
                    print(f"Batch starting at index {i} encountered an error.")

        # 데이터가 실제로 적재되었는지 확인하는 코드 추가
        check_embeddings(session)

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

    # 매 배치마다 적재가 되었는지 확인하는 코드 추가
    check_embeddings(session)  # 적재된 임베딩 수를 확인
    print(f"Batch with {len(batch_records)} records updated successfully.")

# 데이터가 실제로 적재되었는지 확인하는 함수
def check_embeddings(session):
    query = "MATCH (r:Review) WHERE r.textEmbedding IS NOT NULL RETURN COUNT(r) AS count"
    result = session.run(query)
    count = result.single()["count"]
    print(f"Total reviews with embeddings: {count}")

# Run the embedding update function
update_review_embeddings(batch_size=3, update_batch_size=3)

# Close the driver connection
driver.close()
