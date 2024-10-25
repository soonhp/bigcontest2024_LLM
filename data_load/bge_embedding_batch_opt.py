from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
import os
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed 
import time

load_dotenv(find_dotenv())
uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]

# Initialize the Neo4j driver
driver = GraphDatabase.driver(uri, auth=(username, password), max_connection_lifetime=200)

# Download the model and move it to GPU for faster computation
model = SentenceTransformer("upskyy/bge-m3-korean").to('cuda')


def get_embedding(text):
    """텍스트를 임베딩하여 반환합니다."""
    return model.encode(text).squeeze().tolist()

def fetch_reviews_by_store(store_pk):
    """특정 storePk에 해당하는 리뷰를 가져옵니다."""
    with driver.session() as session:
        query = """
        MATCH (r:Review) 
        WHERE r.storePk = $store_pk AND r.textEmbedding IS NULL 
        RETURN r.id AS id, r.text AS text
        """
        results = session.run(query, store_pk=store_pk)
        return [(record["id"], record["text"]) for record in results]

def update_review_embedding(review_id, store_pk, embedding):
    """Neo4j에 리뷰 노드의 임베딩을 업데이트합니다."""
    with driver.session() as session:
        query = """
        MATCH (r:Review {id: $review_id, storePk: $store_pk})
        WHERE r.textEmbedding IS NULL
        SET r.textEmbedding = $embedding
        """
        session.run(query, review_id=review_id, store_pk=store_pk, embedding=embedding)

def process_store(store_pk):
    """특정 가게(storePk)의 모든 리뷰 임베딩을 생성하고 업데이트합니다."""
    reviews = fetch_reviews_by_store(store_pk)
    for review_id, review_text in reviews:
        embedding = get_embedding(review_text)
        update_review_embedding(review_id, store_pk, embedding)

def get_all_store_pks():
    """모든 storePk를 가져옵니다."""
    with driver.session() as session:
        query = "MATCH (r:Review) WHERE r.textEmbedding IS NULL RETURN DISTINCT r.storePk AS storePk"
        results = session.run(query)
        return [record["storePk"] for record in results]

def update_embeddings_in_parallel(batch_size=10, max_workers=4):
    """ThreadPoolExecutor를 사용해 가게별로 병렬로 임베딩을 처리합니다."""
    store_pks = get_all_store_pks()
    total_batches = (len(store_pks) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(store_pks), batch_size), total=total_batches, desc="Processing Stores"):
        batch = store_pks[i:i + batch_size]
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_store, store_pk) for store_pk in batch]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing store: {e}")

# 실행
update_embeddings_in_parallel(batch_size=10, max_workers=6)

# 드라이버 종료
driver.close()
