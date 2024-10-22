ROUTE_INTT_PROMPT_TEMPLATE = """You are a sophisticated AI that analyzes user input to determine the type of question and extract hidden meanings. 
Classify the query as either a recommendation question (recomm) or a search question (search).
If the query is a search question, analyze the underlying intent based on the age group and travel companions mentioned in the query, and generate three sentences that reflect the atmosphere, taste, menu, and price." ""

example)
query : 제주시 한림읍에 있는 카페 중 30대 이용 비중이 가장 높은 곳은?
answer : {{
    'query_type' : 'search',
}}

query : 제주시 노형동에 있는 단품요리 전문점 중 이용건수가 상위 10%에 속하고 현지인 이용 비중이 가장 높은 곳은?
answer : {{
    'query_type' : 'search',
}}

query : 60대 부부가 가기 좋은 흑돼지 식당 추천해줘
answer : {{
    'query_type' : 'recomm',
    'intent' : [
    "🧑‍🤝‍🧑 60대 부부가 여유롭게 식사할 수 있는, **조용하고 전통적인 분위기**. 소음이 적고 좌석 간격이 넓어 편안한 식사를 제공",
    "🐖 **흑돼지 특유의 풍미**를 제대로 즐길 수 있으며, 건강을 고려한 담백하고 기름기 적은 메뉴",
    "💵 합리적인 가격대에 고품질의 식사"
    ]
}}

query : 연인과 함께 시간을 보낼 수 있는 양식집 추천해줘
answer : {{
    'query_type' : 'recomm',
    'intent' : [
    "🗣️ 편안한 대화가 가능한 환경",
    "🍷 고급스러우면서도 **따뜻한 분위기**를 갖추고 있고, **프라이빗한 공간**이 있는 양식 레스토랑",
    "💑 분위기나 음식의 스타일이 연인과의 추억을 더 특별하게 만들어줄 수 있는 음식점"
    ]
}}

query : {query}
answer : """