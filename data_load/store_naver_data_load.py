import json
from neo4j import GraphDatabase
from tqdm import tqdm

import os
import time

from dotenv import load_dotenv


# 환경 변수 설정
load_dotenv()
neo4j_url = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))

def preprocess_data(file_path):
    """데이터를 미리 전처리하여 최적화된 형식으로 변환합니다."""
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    processed_data = []

    for store_id, store_data in raw_data.items():
        # Menu 데이터를 "name:price" 형식으로 변환
        menu_string = ", ".join([f'{v["name"]}:{v["price"]}' for v in store_data.get("menu", {}).values()])

        # 키워드 중 상위 3개 추출
        def get_top_keywords(keyword_dict, top_n=3):
            return ", ".join([k for k, _ in sorted(keyword_dict.items(), key=lambda x: -x[1])[:top_n]])

        processed_data.append({
            "storeId": store_id,
            "rating": store_data.get("rating"),
            "rating_count": store_data.get("rating_count"),
            "image_url": store_data.get("image_url"),
            "latitude": store_data.get("coordinate", {}).get("lat"),
            "longitude": store_data.get("coordinate", {}).get("lng"),
            "menu": menu_string,
            "use_how": store_data.get("keyword_dict", {}).get("use_how", {}),
            "wait_time": store_data.get("keyword_dict", {}).get("wait_time", {}),
            "purpose": get_top_keywords(store_data.get("keyword_dict", {}).get("purpose", {})),
            "visit_with": get_top_keywords(store_data.get("keyword_dict", {}).get("visit_with", {})),
        })

    return processed_data

def insert_batch(tx, batch):
    """전처리된 데이터를 Neo4j에 적재하는 함수."""
    for item in batch:
        try:
            tx.run(
                """
                MATCH (s:STORE {pk: toInteger($storeId)})
                SET s.rating_naver = $rating,
                    s.rating_count_naver = $rating_count,
                    s.image_url_naver = $image_url,
                    s.latitude = $latitude,
                    s.longitude = $longitude,
                    s.menu = $menu,
                    s.use_how = apoc.convert.toJson($use_how),
                    s.wait_time = apoc.convert.toJson($wait_time),
                    s.purpose = $purpose,
                    s.visit_with = $visit_with
                """, 
                **item
            )
        except Exception as e:
            print(f"Batch 처리 중 오류 발생 - Store ID: {item['storeId']} | 오류: {e}")

def insert_data_in_batches(processed_data, batch_size=10):
    """배치 단위로 데이터를 Neo4j에 적재."""
    total_batches = (len(processed_data) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(processed_data), batch_size), total=total_batches, desc="Loading Batches"):
        batch = processed_data[i:i + batch_size]
        start_time = time.time()  # 시작 시간

        try:
            with driver.session() as session:
                session.execute_write(insert_batch, batch)
        except Exception as e:
            print(f"Batch {i // batch_size + 1} 처리 중 오류 발생: {e}")

        end_time = time.time()  # 종료 시간
        print(f"Batch {i // batch_size + 1}/{total_batches} processed in {end_time - start_time:.2f} seconds")

# JSON 파일 경로와 배치 사이즈 설정
json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'naver-map-results-preprocessed.json')
batch_size = 10

# 데이터 전처리 및 적재 실행
processed_data = preprocess_data(json_file_path)
insert_data_in_batches(processed_data, batch_size)

