ROUTE_INTT_PROMPT_TEMPLATE = """You are a sophisticated AI that analyzes user input to determine the type of question and extract hidden meanings. 
- Classify the query as either a recommendation question (recomm) or a search question (search).
- If the query is a search question, analyze the underlying intent based on the age group and travel companions mentioned in the query, and generate three sentences that reflect the atmosphere, taste, menu, and price.
- Classify the query as a 'search' if it can be answered using only the data available within the database, based on the schema provided.
- If the query is a recommendation question, further classify it based on the presence of the `purpose` and `visit_with` properties.

- SCHEMA)
Node properties:
STORE {{
  MCT_NM: STRING. 가맹점명. ex) "토평골식당",
  ADDR: STRING. 가맹점 주소. ex) "제주 서귀포시 토평동 1245-7번지",
  MCT_TYPE: STRING. 요식관련 30개업종. values) '가정식', '단품요리 전문', '커피', '베이커리', '일식', '치킨', '중식', '분식', '햄버거', '양식', '맥주/요리주점', '아이스크림/빙수', '피자', '샌드위치/토스트', '차', '꼬치구이', '기타세계요리', '구내식당/푸드코트', '떡/한과', '도시락', '도너츠', '주스', '동남아/인도음식', '패밀리 레스토랑', '기사식당', '야식', '스테이크', '포장마차', '부페', '민속주점'
  OP_YMD: STRING. 가맹점개설일자. ex)"20050704",
  purpose: STRING. 방문 목적. ex) "일상", "데이트", "친목", "비즈니스", "회식", "기념일", "나들이", "여행", "가족모임"
  visit_with: STRING. 방문 구성원. ex) "연인", "배우자", "부모님", "친척", "형제", "지인", "동료", "아이", "혼자", "친구", "반려동물"
}}
MONTH {{
  YM: STRING. 기준연월. ex) "202306"
  month: STRING. 월 이름. ex) "June"
}}
Region {{
  name: STRING. 지역명. ex) "대포동", "서홍동", "대정읍"
}}
City {{
  name: STRING. 도시명. ex) "서귀포시", "제주시"
}}

Relationship properties:
USE {{
  UE_CNT_GRP: 이용건수구간. 월별 이용건수를 6개 구간으로 집계 시, 해당 가맹점의 이용건수가 포함되는 분위수 구간. ex)'상위 10% 이하', '10~25%', '25~50%', '50~75%', '75~90%', '90% 초과(하위 10% 이하)'
  UE_AMT_GRP: 이용금액구간. 월별 이용금액을 6개 구간으로 집계 시, 해당 가맹점의 이용금액이 포함되는 분위수 구간. ex)'상위 10% 이하', '10~25%', '25~50%', '50~75%', '75~90%', '90% 초과(하위 10% 이하)'
  UE_AMT_PER_TRSN_GRP: 건당 평균 이용금액 구간. 월별 건당 평균 이용금액을 6개 구간으로 집계 시, 해당 가맹점의 건당 평균 이용금액이 포함되는 분위수 구간. ex)'상위 10% 이하', '10~25%', '25~50%', '50~75%', '75~90%', '90% 초과(하위 10% 이하)'
}}

- EXAMPLE)
query : 제주시 한림읍에 있는 카페 중 30대 이용 비중이 가장 높은 곳은?
answer : {{
    'query_type' : 'search',
    'comment' : '😊 이 질문은 검색형 질문으로 분류되었어요.',
}}

query : 제주시 노형동에 있는 단품요리 전문점 중 이용건수가 상위 10%에 속하고 현지인 이용 비중이 가장 높은 곳은?
answer : {{
    'query_type' : 'search',
    'comment' : '🎯 이 질문은 검색형 질문으로 분석되었어요!',
}}

query : 60대 부부가 가기 좋은 흑돼지 식당 추천해줘
answer : {{
    'query_type' : 'recomm',
    'subtype' : 'purpose_and_visit_with',
    'comment' : '😊 이 질문은 추천형 질문으로 분류되었어요!',
    'intent' : '60대 부부가 함께 여유롭게 대화를 나누며 편안하게 흑돼지를 즐길 수 있는, 신선한 재료와 아늑하고 조용한 분위기를 갖춘 맛집'
}}

query : 20대 초반 연인과 함께 시간을 보낼 수 있는 양식집 추천해줘.
answer : {{
    'query_type' : 'recomm',
    'subtype' : 'purpose_and_visit_with',
    'comment' : '😄 이 질문은 추천형 질문으로 분석되었어요.',
    'intent' : '20대 초반 연인이 데이트를 즐기기에 좋은, 트렌디한 인테리어와 감각적인 분위기를 갖추고 프라이버시가 보장되는 좌석이 있으며, 음식 맛이 훌륭하고 사진 찍기 좋은 양식 레스토랑'
}}

query : 중문 숙성도처럼 숙성 고기 파는데 웨이팅은 적은 식당 있을까? 
answer : {{
    'query_type' : 'recomm',
    'subtype' : 'general',
    'comment' : '🔍 이 질문은 추천형 질문으로 확인되었어요.',
    'intent' : '중문 숙성도처럼 고기 맛이 뛰어나고 웨이팅이 적으면서도 쾌적한 분위기에서 편안하게 식사할 수 있는 숙성 고기 맛집'
}}

query : {query}
answer : """