import json
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm
import math

path = "../data/naver-map-results-preprocessed.json"
save_path = "../data/naver-map-results-postprocessed-coord.json"
coord_path = "../data/old_addr_with_coordinates.csv"

# Haversine 공식을 사용하여 두 지점 간의 실제 거리 계산
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 지구의 반지름 (km)
    phi1, phi2 = map(math.radians, [lat1, lat2])
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 + 
         math.cos(phi1) * math.cos(phi2) * 
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # km 단위로 반환

def main():
    # JSON 파일 열기
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    coord_data = pd.read_csv(coord_path, encoding='utf-8')

    # 좌표 데이터에서 위도와 경도 추출 및 NaN 값 제거
    coords = coord_data[['lat', 'lng']].dropna().values

    # NearestNeighbors 모델 생성
    nbrs = NearestNeighbors(n_neighbors=3).fit(coords)

    # 각 데이터에 대해 가장 가까운 관광명소 찾기
    for entry in tqdm(data):
        location = data[entry]['coordinate']  # entry에서 좌표 추출
        distances, indices = nbrs.kneighbors([[location['lat'], location['lng']]])
        
        # 가장 가까운 관광명소 선택
        nearest_attractions = coord_data.iloc[indices[0]].copy()
        
        # Haversine 함수를 사용하여 실제 거리 계산
        nearest_attractions['distance'] = [
            haversine(location['lat'], location['lng'], coord_data.iloc[i]['lat'], coord_data.iloc[i]['lng']) 
            for i in indices[0]
        ]
        
        data[entry]['nearest_attractions'] = nearest_attractions.to_dict(orient='records')

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
