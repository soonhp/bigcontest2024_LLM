import json
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm
import math
from sentence_transformers import SentenceTransformer


path = "../data/naver-map-results-postprocessed-coord.json"
save_path = "../data/naver-map-results-preprocessed-coord-embedding.json"

def main():
    # JSON 파일 열기
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 모델 로드
    model = SentenceTransformer("upskyy/bge-m3-korean").to('cuda')

    # 배치 단위로 리뷰 임베딩 생성
    batch_size = 256  # 배치 크기 설정
    entries = list(data.keys())
    
    # 리뷰 텍스트를 한 번에 가져오기
    all_review_texts = []
    all_review_ids = []
    for entry in tqdm(entries):
        reviews = data[entry]['review']
        for review_id in reviews:
            all_review_texts.append(reviews[review_id]['review'])  # 모든 리뷰 텍스트 수집
            all_review_ids.append((entry, review_id))  # 리뷰 ID 저장

    # 배치 임베딩 생성
    embeddings = []
    for i in tqdm(range(0, len(all_review_texts), batch_size), desc="Generating embeddings"):
        batch_texts = all_review_texts[i:i + batch_size]
        batch_embeddings = model.encode(batch_texts, batch_size=batch_size, convert_to_tensor=True).cpu().tolist()
        embeddings.extend(batch_embeddings)
    
    # 결과를 각 리뷰에 추가
    for (entry, review_id), embedding in tqdm(zip(all_review_ids, embeddings), total=len(embeddings), desc="Adding embeddings to reviews"):
        data[entry]['review'][review_id]['embedding'] = embedding  # 'embedding' 키에 추가

    # JSON 파일 저장
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # 메모리 해제
    del model  # 모델 메모리 해제


if __name__ == "__main__":
    main()
