from router import handle_user_query

def test_handle_user_query():
    test_inputs = [
        "20대 친구들과 함께 방문할 만한 맛집을 알려줘",
        "제주도에서 할 수 있는 액티비티 추천해줘",
        "가족과 함께 가기 좋은 카페를 찾고 있어",
    ]

    for user_input in test_inputs:
        result = handle_user_query(user_input)
        print(f"Input: {user_input}\nOutput: {result}\n")

# 테스트 실행
if __name__ == "__main__":
    test_handle_user_query()