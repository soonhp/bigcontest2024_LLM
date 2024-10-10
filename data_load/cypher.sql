// shinhan MCT data load

// CREATE STORE NODES
LOAD CSV WITH HEADERS FROM 'file:///JEJU_MCT_DATA_v2_PK_utf.csv' AS row
MERGE (store:STORE {
    pk: toInteger(row.pk)
})
ON CREATE SET
    store.MCT_NM = row.MCT_NM,
    store.OP_YMD = toInteger(row.OP_YMD),
    store.MCT_TYPE = row.MCT_TYPE,
    store.ADDR = row.ADDR;

// CREATE MONTH NODES WITH MONTH NAME
LOAD CSV WITH HEADERS FROM 'file:///JEJU_MCT_DATA_v2_PK_utf.csv' AS row
MERGE (month:MONTH {
    YM: toInteger(row.YM)
})
ON CREATE SET
    month.month = CASE toInteger(row.YM) % 100
        WHEN 1 THEN 'January'
        WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'
        WHEN 4 THEN 'April'
        WHEN 5 THEN 'May'
        WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'
        WHEN 8 THEN 'August'
        WHEN 9 THEN 'September'
        WHEN 10 THEN 'October'
        WHEN 11 THEN 'November'
        WHEN 12 THEN 'December'
        ELSE 'Unknown'
    END;

// CREATE USE RELATIONSHIPS
:auto LOAD CSV WITH HEADERS FROM 'file:///JEJU_MCT_DATA_v2_PK_utf.csv' AS row
CALL {
WITH ROW
MATCH (store:STORE {pk: toInteger(row.pk)})
MATCH (month:MONTH {YM: toInteger(row.YM)})
MERGE (store)-[use:USE]->(month)
ON CREATE SET
    use.UE_CNT_GRP = row.UE_CNT_GRP,
    use.UE_AMT_GRP = row.UE_AMT_GRP,
    use.UE_AMT_PER_TRSN_GRP = row.UE_AMT_PER_TRSN_GRP,
    use.MON_UE_CNT_RAT = toFloat(row.MON_UE_CNT_RAT),
    use.TUE_UE_CNT_RAT = toFloat(row.TUE_UE_CNT_RAT),
    use.WED_UE_CNT_RAT = toFloat(row.WED_UE_CNT_RAT),
    use.THU_UE_CNT_RAT = toFloat(row.THU_UE_CNT_RAT),
    use.FRI_UE_CNT_RAT = toFloat(row.FRI_UE_CNT_RAT),
    use.SAT_UE_CNT_RAT = toFloat(row.SAT_UE_CNT_RAT),
    use.SUN_UE_CNT_RAT = toFloat(row.SUN_UE_CNT_RAT),
    use.HR_5_11_UE_CNT_RAT = toFloat(row.HR_5_11_UE_CNT_RAT),
    use.HR_12_13_UE_CNT_RAT = toFloat(row.HR_12_13_UE_CNT_RAT),
    use.HR_14_17_UE_CNT_RAT = toFloat(row.HR_14_17_UE_CNT_RAT),
    use.HR_18_22_UE_CNT_RAT = toFloat(row.HR_18_22_UE_CNT_RAT),
    use.HR_23_4_UE_CNT_RAT = toFloat(row.HR_23_4_UE_CNT_RAT),
    use.LOCAL_UE_CNT_RAT = toFloat(row.LOCAL_UE_CNT_RAT),
    use.RC_M12_MAL_CUS_CNT_RAT = toFloat(row.RC_M12_MAL_CUS_CNT_RAT),
    use.RC_M12_FME_CUS_CNT_RAT = toFloat(row.RC_M12_FME_CUS_CNT_RAT),
    use.RC_M12_AGE_UND_20_CUS_CNT_RAT = toFloat(row.RC_M12_AGE_UND_20_CUS_CNT_RAT),
    use.RC_M12_AGE_30_CUS_CNT_RAT = toFloat(row.RC_M12_AGE_30_CUS_CNT_RAT),
    use.RC_M12_AGE_40_CUS_CNT_RAT = toFloat(row.RC_M12_AGE_40_CUS_CNT_RAT),
    use.RC_M12_AGE_50_CUS_CNT_RAT = toFloat(row.RC_M12_AGE_50_CUS_CNT_RAT),
    use.RC_M12_AGE_OVR_60_CUS_CNT_RAT = toFloat(row.RC_M12_AGE_OVR_60_CUS_CNT_RAT)
} IN TRANSACTIONS OF 1000 ROWS


// Create a unique constraint and index on the pk property of STORE nodes
CREATE CONSTRAINT store_pk_constraint IF NOT EXISTS
FOR (store:STORE)
REQUIRE store.pk IS UNIQUE;


// google review data Load JSON data using APOC
CALL apoc.load.json('file:///google_crawling.json') YIELD value
UNWIND keys(value) AS storeId
WITH storeId, value[storeId] AS storeData
MATCH (s:STORE {pk: toInteger(storeId)})
SET s.name = storeData.search_result_nm,
    s.rating = storeData.rating,
    s.rating_count = storeData.rating_count,
    s.image_url = storeData.image_url

WITH s, storeData, storeId
UNWIND keys(storeData.review) AS reviewKey
WITH s, reviewKey,storeId,storeData.review[reviewKey] AS reviewData
MERGE (r:Review {id: reviewKey, storePk: toInteger(storeId)})
SET r.text = reviewData.review,
    r.user_id = reviewData.user_id
MERGE (s)-[:HAS_REVIEW]->(r);


// 시, [동,읍,리] 주소 파싱하여 Hierarchy 구조로 STORE 노드 연결
CALL apoc.periodic.iterate(
    'MATCH (s:STORE) WHERE s.ADDR IS NOT NULL RETURN s, split(s.ADDR, " ") AS addrParts',
    '
    WITH s, addrParts
    WHERE size(addrParts) > 2
    WITH s, addrParts[1] AS city, addrParts[2] AS region

    MERGE (c:City {name: city})

    WITH s, c, region
    WHERE region CONTAINS "동" OR region CONTAINS "읍" OR region CONTAINS "리"
    MERGE (r:Region {name: region})
    MERGE (c)-[:HAS_REGION]->(r)

    MERGE (r)-[:HAS_STORE]->(s)
    ',
    {batchSize: 1000, parallel: true}
);
