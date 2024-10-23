import json
from neo4j import GraphDatabase
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import os

# 환경 변수 설정
load_dotenv()
neo4j_url = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# Neo4j 드라이버 생성
driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

def preprocess_data(file_path):
    """리뷰 데이터를 가게별로 전처리합니다."""
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    processed_data = []
    for store_id, store_data in raw_data.items():
        reviews = store_data.get("review", {})
        for review_key, review_data in reviews.items():
            processed_data.append({
                "storeId": store_id,
                "reviewId": review_key,
                "text": review_data.get("review", ""),
                "user_id": review_data.get("user_id", ""),
                "visit_keywords": ", ".join(review_data.get("visit_keywords", []))
            })

    return processed_data

def insert_reviews_node(tx, review):
    """리뷰 노드를 생성하고 가게와의 관계를 생성합니다."""
    tx.run(
        """
        MERGE (r:Review:Naver {id: $reviewId, source: "Naver", storePk: toInteger($storeId)})
        ON CREATE SET r.text = $text,
                      r.user_id = $user_id,
                      r.visit_keywords = $visit_keywords
        """,
        **review
    )

def process_review(session, review):
    """리뷰 데이터를 처리합니다."""
    try:
        session.execute_write(insert_reviews_node, review)
    except Exception as e:
        print(f"리뷰 적재 중 오류 발생 - Store ID {review['storeId']}: {e}")

def insert_reviews_in_batches(processed_data, batch_size=100, max_workers=4):
    """배치 단위로 데이터를 처리합니다."""
    total_batches = (len(processed_data) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(processed_data), batch_size), total=total_batches, desc="Loading Store Batches"):
        batch = processed_data[i:i + batch_size]
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_review, driver.session(), review) for review in batch]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"배치 처리 중 오류 발생: {e}")

# JSON 파일 경로 설정
json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'naver-map-results-preprocessed.json')

# 데이터 전처리 및 리뷰 적재 실행
processed_data = preprocess_data(json_file_path)
insert_reviews_in_batches(processed_data, batch_size=100, max_workers=4)

# 드라이버 연결 닫기
driver.close()