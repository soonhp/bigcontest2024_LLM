# 기존버전
retrievalQuery = """
MATCH (node)<-[:HAS_REVIEW]-(store)
RETURN node.text AS text,
       store AS store,
       score,
       {
         reviewText: node.text,
         storeName: store.MCT_NM,
         storeType: store.MCT_TYPE,	
         storeAddress: store.ADDR,
         storeImage: store.image_url,
         storeRating: store.rating,
         score: score
       } AS metadata
"""

# 수정버전(선진) 1020
retrievalQuery_v2 = """
MATCH (node)<-[:HAS_REVIEW]-(store)
RETURN node.text AS text,
       store AS store,
       score,
       {
         reviewText: node.text,
         storeName: store.MCT_NM,
         store_Type: store.MCT_TYPE,	
         store_Image: {kakao: store.image_url_kakao, google: store.image_url_google},
         store_Rating: {kakao: store.rating_kakao, google:store.rating_google}
       } AS metadata
"""