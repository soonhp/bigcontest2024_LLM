def retrieve_top_k_reviews(store_pk, query_embedding, driver, k=2):
    """
    특정 STORE 노드에 연결된 리뷰 중 유사한 TOP-K 리뷰를 반환합니다.
    """
    query = """
    MATCH (s:STORE {pk: $store_pk})-[:HAS_REVIEW]->(r:Review)
    WHERE r.textEmbedding IS NOT NULL
    RETURN r.text AS text, gds.similarity.cosine(r.textEmbedding, $query_embedding) AS similarity
    ORDER BY similarity DESC
    LIMIT $k
    """
    with driver.session() as session:
        result = session.run(
            query, store_pk=store_pk, query_embedding=query_embedding, k=k
        )
        return [
            {"text": record["text"], "similarity": record["similarity"]}
            for record in result
        ]
    

def get_cypher_result_to_str(candidates_2nd, query_embedding, graphdb_driver, k=2):
    cypher_result_str = ''
    for r in candidates_2nd:
        r_keys = r.keys()
        one_record_str = ''
        for key in r_keys:
            one_record_str += f"{key} : {str(r[key])[:100]}\n"
            if key == 'pk':
                reviews = retrieve_top_k_reviews(r[key], query_embedding, graphdb_driver, k=k)
                if reviews:
                    reviews_lst = [f"{ri}. {review['text'][:100]}".strip() for ri, review in enumerate(reviews, start=1)]
                    one_record_str += "리뷰 : \n" + '\n'.join(reviews_lst) + "\n"
        cypher_result_str += one_record_str + '\n'
    return cypher_result_str