from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.prompts.prompt import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from retry import retry
from timeit import default_timer as timer
# import streamlit as st

from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm
from dotenv import load_dotenv, find_dotenv


from neo4j import GraphDatabase
from json import loads
import json

import os


load_dotenv()

os.environ["KYEONGCHAN_GEMINI_API_KEY"] = os.getenv("KYEONGCHAN_GEMINI_API_KEY") 
gemini_key = os.environ["KYEONGCHAN_GEMINI_API_KEY"]
os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI")
os.environ["NEO4J_USERNAME"] =os.getenv("NEO4J_USERNAME")
os.environ["NEO4J_PASSWORD"] =os.getenv("NEO4J_PASSWORD")

neo4j_url = os.environ["NEO4J_URI"]
neo4j_user = os.environ["NEO4J_USERNAME"]
neo4j_password = os.environ["NEO4J_PASSWORD"] 

import google.generativeai as genai


# Load BGE-M3-Korean model
tokenizer = AutoTokenizer.from_pretrained("upskyy/bge-m3-korean")
model = AutoModel.from_pretrained("upskyy/bge-m3-korean")

# Define mean pooling function
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# Function to get embeddings for a given text
def get_embedding(text):
    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**encoded_input)
    return mean_pooling(model_output, encoded_input["attention_mask"]).squeeze().tolist()



# 제미나이 API 키 설정
genai.configure(api_key=gemini_key)
llm_model = genai.GenerativeModel(model_name='gemini-pro')

SYSTEM_PROMPT = """You are an expert in recommending restaurants.
* Create answers in Korean
* If the question is not about restaurants recommendation, please answer like this:
Sorry, I can only answer questions related to restaurants recommendation.
* Don't answer the same sentence repeatedly.

"""

PROMPT_TEMPLATE = """

{questions}

Here is the context in JSON format. This dataset contains information about restaurants that will be recommended to the user.


<context>
{context}
</context>

When recommending restaurants to a user related to a question, make sure to recommend at least five restaurants included in the context!
Create answers in Korean
Please add the following phrase at the end of your answer : 

The following is an example of a response when recommending a restaurants to a user :
Hello! My name is 😎 Agent SH , a restaurants recommendation chatbot that specializes in restaurants recommendations. I recommend restaurants based on GraphRAG.
Based on your questions, I'll recommend restaurants you might like.

🍴 음식점 : (주)시더스초밥제주연동점
🚩 주소 : 제주 제주시 연동 355-8번지 1층
📷 사진 : https://lh5.googleusercontent.com/p/AF1QipPI4j5Ml2zbxvH86gKvyYaGl55jHtWYR-l7PcTU=w408-h306-k-no
🌟 별점 : 4.5
✓ 음식점 추천 이유 : 질문에서 초밥이 포함되어 있기 때문에 추천하였습니다.

"""
PROMPT = PromptTemplate(
    input_variables=["questions","context"], template= PROMPT_TEMPLATE
)
# prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
# # embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def run_query(uri, user, password, query, params):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        # print(params)
        result = session.run(query, params)
        # print(result)
        return [record for record in result]

def vector_graph_qa(query):
    query_vector = get_embedding(query)
    # print(query_vector)
    uri = neo4j_url
    user = neo4j_user
    password = neo4j_password
    params = {'queryVector':query_vector}
    cypher_query = """
    CALL db.index.vector.queryNodes('queryVector', 5, $queryVector)
    YIELD node AS doc, score
    match (doc)<-[s:HAS_REVIEW]-(store:STORE)
    RETURN store AS store_Info, 
        collect('The type of the store ' + store.MCT_NM + ' is ' + store.MCT_TYPE + 
        ', the rating of store is ' + store.rating + ' and the review of the store is ' + doc.text) AS StoreInfo,  
        score
    ORDER BY score DESC LIMIT 5
    """
    result = run_query(uri, user, password, cypher_query, params)
    # print(result)
    return result

# def df_to_context(df):
#     result = df.to_json(orient="records")
#     print('df_to_context-RESULT : ', result )
#     parsed = loads(result)
#     print('df_to_context-parsed : ', parsed)
#     # text = yaml.dump(
#     #     parsed,
#     #     sort_keys=False, indent=1,
#     #     default_flow_style=None)
#     text = json.dumps(parsed, indent=1)
#     return text
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
retrievalQuery = """
  RETURN node.text AS text,
  score,
  {
    score: score
  } AS metadata
"""
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings_model = HuggingFaceEmbeddings(
    model_name='upskyy/bge-m3-korean',
    model_kwargs={'device':'cpu'},
    encode_kwargs={'normalize_embeddings':True},
)
def get_neo4j_vector(index_name='queryVector'):
    neo4jvector = Neo4jVector.from_existing_index(
        embedding=embeddings_model,  # Using the custom embedding function
        url=neo4j_url,
        database='neo4j',
        username=neo4j_user,
        password=neo4j_password,
        index_name=index_name,
        text_node_property="textEmbedding",
        retrieval_query=retrievalQuery
    )
    return neo4jvector

store_retriever = get_neo4j_vector().as_retriever(search_kwargs={"k": 5})

from langchain.chains.retrieval import create_retrieval_chain

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
@retry(tries=5, delay=5)
def get_results(question):
    start = timer()
    try:
        df = vector_graph_qa(question)

        ans = PROMPT.format(questions=question, context=df)
        
        # # 제미나이 모델을 사용하여 답변 생성
        # response = llm_model.generate_content(ans)
        

        # result = response.text
        # print(result)

        chat_llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=gemini_key,
                                    convert_system_message_to_human=True) 
        messages = chat_llm(
        [  
            SystemMessage(content="SYSTEM_PROMPT"),
            HumanMessage(content=ans)
        ]
        )
        result = messages.content
        r = {'context': df, 'result': result}
        # messages = [
        #     SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        #     HumanMessagePromptTemplate.from_template(ans),
        # ]
        # CHAT_PROMPT = ChatPromptTemplate.from_messages(messages)
        # response = llm_model.generate_content(CHAT_PROMPT)
        # result = response.text

        # messages = [
        #     SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        #     HumanMessagePromptTemplate.from_template(PROMPT)
        # ]
        # prompt = ChatPromptTemplate.from_messages(messages)
        # chain_type_kwargs = {"prompt": prompt}
        # llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key = gemini_key,convert_system_message_to_human=True)
        # chain = prompt | llm | StrOutputParser()
        # kg = create_retrieval_chain(store_retriever, chain)
        # result = kg.invoke({"input": question})
        # print(f"{result['answer']}")

        # # 제미나이 모델을 사용하여 답변 생성
        # response = genai.generate_chat_message(
        #     model=llm_model.model_name,
        #     messages=[
        #         {'author': 'system', 'content': SYSTEM_PROMPT},
        #         {'author': 'user', 'content': ans}
        #     ]
        # )
        # result = response.candidates[0]['content']
        return result
    finally:
        print('Response Generation Time : {}'.format(timer() - start))
        
print(get_results('제주의 고기집을 갈려고하는데 추천해줘!'))