import json
from neo4j import GraphDatabase
from tqdm import tqdm
from json import loads
from dotenv import load_dotenv, find_dotenv
import os
import time

load_dotenv()

os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI")
os.environ["NEO4J_USERNAME"] =os.getenv("NEO4J_USERNAME")
os.environ["NEO4J_PASSWORD"] =os.getenv("NEO4J_PASSWORD")

neo4j_url = os.environ["NEO4J_URI"]
neo4j_user = os.environ["NEO4J_USERNAME"]
neo4j_password = os.environ["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

def load_data_in_batches(file_path, batch_size=1000):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    store_ids = list(data.keys())
    total_batches = (len(store_ids) + batch_size - 1) // batch_size

    # tqdm으로 진행률 표시
    for i in tqdm(range(0, len(store_ids), batch_size), total=total_batches, desc="Loading Batches"):
        start_time = time.time()  # 시작 시간 기록
        batch = store_ids[i:i + batch_size]
        batch_data = [{ "storeId": store_id, "data": data[store_id] } for store_id in batch]
        insert_batch_with_cypher(batch_data)
        end_time = time.time()  # 종료 시간 기록
        print(f"Batch {i // batch_size + 1}/{total_batches} processed in {end_time - start_time:.2f} seconds")

def run_batch_transaction(tx, batch_data):
    for item in batch_data:
        tx.run(
            """
            MATCH (s:STORE {pk: toInteger($storeId)})
            SET s.rating_google = $rating,
                s.rating_count_google = $rating_count,
                s.image_url_google = $image_url
                
            WITH s, $reviews AS reviews, $storeId AS storeId
            UNWIND keys($reviews) AS reviewKey
            WITH s, reviewKey, storeId, $reviews[reviewKey] AS reviewData
            MERGE (r:Review {id: reviewKey, source: "Google", storePk: toInteger(storeId)})
            SET r:Google,
                r.text = reviewData.review,
                r.user_id = reviewData.user_id
            MERGE (s)-[:HAS_REVIEW]->(r)
            """,
            storeId=item["storeId"],
            rating=item["data"].get("rating"),
            rating_count=item["data"].get("rating_count"),
            image_url=item["data"].get("image_url"),
            reviews=item["data"].get("review", {})
        )

def insert_batch_with_cypher(batch_data):
    with driver.session() as session:
        # 각 배치를 트랜잭션으로 실행
        session.execute_write(run_batch_transaction, batch_data)

# JSON 파일 경로와 배치 사이즈 설정
json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'google_crawling.json')

batch_size = 1000

# 데이터 적재 실행
load_data_in_batches(json_file_path, batch_size)


# 연결 닫기
driver.close()
