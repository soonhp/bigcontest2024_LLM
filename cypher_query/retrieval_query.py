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
