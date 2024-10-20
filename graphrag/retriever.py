from dotenv import load_dotenv
from config import CONFIG
from cypher_query.retrieval_query import retrievalQuery, retrievalQuery_v2
from graphrag.get_embedding_model import get_embedding_model
from langchain_community.vectorstores.neo4j_vector import Neo4jVector


load_dotenv()


def get_neo4j_vector(index_name='queryVector'):
    neo4jvector = Neo4jVector.from_existing_index(
        embedding=get_embedding_model(),  # Using the custom embedding function
        url=CONFIG.neo4j_url,
        database='neo4j',
        username=CONFIG.neo4j_user,
        password=CONFIG.neo4j_password,
        index_name=index_name,
        text_node_property="textEmbedding",
        # retrieval_query=retrievalQuery
        retrieval_query=retrievalQuery_v2
    )
    return neo4jvector

# retrieve_store_nodes 함수에서 동기적으로 get_neo4j_vector 호출
def retrieve_store_nodes(query):
    store_retriever = get_neo4j_vector().as_retriever(search_kwargs={"k": 6})
    
    # 비동기 메서드는 동기 호출로 대체
    result_nodes = store_retriever.invoke(query)  # invoke는 동기적으로 실행되는 메서드
    return result_nodes

