import json
import os
from tqdm import tqdm

def get_group_index(store_pk, total_groups):
    """storePk를 기준으로 그룹 번호를 계산."""
    return int(store_pk) % total_groups

def extract_relevant_data(store_pk, reviews, start, batch_size):
    """리뷰 ID와 임베딩 정보에서 50개씩 배치로 추출."""
    review_embeddings = {
        review_id: review_data.get("reviewEmbedding", [])
        for review_id, review_data in list(reviews.items())[start:start + batch_size]
        if "reviewEmbedding" in review_data
    }
    return {"review": review_embeddings} if review_embeddings else None

def process_large_json_in_batches(input_file, total_groups, batch_size=10):
    """큰 JSON 파일을 읽고 리뷰를 50개씩 배치로 처리."""
    groups = [{} for _ in range(total_groups)]  # 10개 그룹 초기화

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

        # tqdm을 사용해 진행 상황 표시
        for store_pk, store_data in tqdm(data.items(), desc="Processing stores"):
            reviews = store_data.get("review", {})
            total_reviews = len(reviews)

            # 리뷰를 50개씩 배치로 처리
            for start in range(0, total_reviews, batch_size):
                relevant_data = extract_relevant_data(store_pk, reviews, start, batch_size)
                if relevant_data:
                    group_index = get_group_index(store_pk, total_groups)
                    if store_pk not in groups[group_index]:
                        groups[group_index][store_pk] = {"review": {}}
                    # 해당 그룹에 리뷰 배치 추가
                    groups[group_index][store_pk]["review"].update(relevant_data["review"])

    return groups

def save_groups_to_files(groups, output_dir):
    """그룹별 데이터를 개별 JSON 파일로 저장."""
    for i, group in enumerate(groups):
        output_file = os.path.join(output_dir, f"review_embeddings_group_{i + 1}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(group, f, ensure_ascii=False, indent=4)
        print(f"{output_file} 저장 완료.")

# 경로 설정
input_file = "../data/naver-map-results-preprocessed-coord-embedding.json"
output_dir = "../data/review_embeddings_groups"
os.makedirs(output_dir, exist_ok=True)

try:
    # JSON 데이터를 그룹으로 나누기
    total_groups = 10
    groups = process_large_json_in_batches(input_file, total_groups)

    # 그룹별 데이터를 파일로 저장
    save_groups_to_files(groups, output_dir)

except MemoryError:
    print("메모리 에러가 발생했습니다.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")

