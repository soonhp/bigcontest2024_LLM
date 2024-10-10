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
