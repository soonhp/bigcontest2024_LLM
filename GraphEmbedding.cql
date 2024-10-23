# Review와 STORE 노드의 Visit_with(구성원) 노드 연결관계를 기반으로 FastRP 그래프 임베딩 생성 Cypher 쿼리
CALL gds.graph.project(
    'csgraph',
    ['Review','STORE','Visit_with'],
    ['HAS_VISIT_WITH']
) YIELD graphName AS graph, nodeProjection, nodeCount AS nodes, relationshipCount AS rels

CALL gds.fastRP.mutate('csgraph',{
embeddingDimension : 16, // 임베딩 차원
randomSeed : 42,
mutateProperty : 'GraphEmbedding', // 새로운 속성(임베딩)의 이름
iterationWeights:[0.1,0.7,0.9] // k-step 전이행렬의 가중치
}
)
YIELD nodePropertiesWritten

CALL gds.graph.nodeProperties.write('csgraph',['GraphEmbedding'])
YIELD propertiesWritten
