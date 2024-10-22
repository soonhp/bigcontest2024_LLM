# bigcontest2024

## DB SCHEMA

<p align="center">
<img width="70%" alt="DB_SCHEMA" src="https://github.com/user-attachments/assets/9130ad7b-260a-4d32-8ce4-3ced6b46a3fd"
</p>

## Pipeline
![pipeline](./images/pipeline.png)

## Data Load
### 네이버, 카카오, 구글 플랫폼 별로

1. 사진(URL)
2. 리뷰 데이터(100개 미만)
  - 네이버 - 방문자리뷰(개수)
  - 카카오맵 - 후기(개수)
  - 구글 - 개수
3. 별점 정보

### + 추가적인 정보 활용

- 네이버
영업시간,
메뉴별 가격,
리뷰 추천순으로 100개 미만 -> (데이트 / 연인,배우자) 연결해서 크롤링

- 카카오맵
시설정보

# Streamlit
```
streamlit run app.py
```
