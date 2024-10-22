from neo4j import GraphDatabase
import os
from config import CONFIG
import timeit

graphdb_driver = GraphDatabase.driver(uri=CONFIG.neo4j_url, 
                                      auth=(
                                          CONFIG.neo4j_user,
                                          CONFIG.neo4j_password
                                          )
                                        )


def get_ratings_str(d):
    ratings_lst = []
    for platform in ['naver', 'kakao', 'google']:
        if (platform in d.metadata['store_Rating']) and (d.metadata['store_Rating'][platform] is not None):
            pf_rating = d.metadata['store_Rating'][platform]
        else:
            continue
        if platform in d.metadata['reviewCount'] and (d.metadata['reviewCount'][platform] is not None):
            pf_rc = d.metadata['reviewCount'][platform]
        else:
            continue
        ratings_lst.append(f"{platform} {pf_rating}({pf_rc}명)")
    rating_str = ', '.join(ratings_lst)
    return rating_str


def get_candidate_str(candidates):
    drop_dup = []
    for r in candidates:
        if r.metadata['pk'] not in [d.metadata['pk'] for d in drop_dup]:
            drop_dup.append(r)

    candidates_str = ''
    for d in drop_dup:
        # 가게명
        candidates_str += f"가게명 : {d.metadata['storeName']}\n"
        # pk
        candidates_str += f"pk : {d.metadata['pk']}\n"
        # 리뷰
        candidates_str += f"리뷰 : {d.metadata['reviewText']}\n"
        # 평점
        rating_str = get_ratings_str(d)
        candidates_str += f"평점 : {rating_str}\n"
        # 음식 유형
        if 'store_Type' in d.metadata:
            candidates_str += f"음식 유형 : {d.metadata['store_Type']}\n"
        # 방문 목적 top 3 
        if 'purpose' in d.metadata:
            candidates_str += f"방문 목적 top 3 : {d.metadata['purpose']}\n"
        # 대기 시간 통계
        if 'wait_time' in d.metadata:
            candidates_str += f"대기 시간 통계 : {d.metadata['wait_time']}\n"
        # 예약 필요 여부
        if 'use_how' in d.metadata:
            candidates_str += f"예약 필요 여부 통계 : {d.metadata['use_how']}\n"
        # 메뉴
        if 'menu' in d.metadata:
            candidates_str += f"메뉴 : {d.metadata['menu']}\n"

        candidates_str += '\n'
    return candidates_str


def get_ratings_str_for_node(node):
    """
    node 구하는 법
    result = driver.execute_query(pk_store_cypher.format(pk=pk))
    node = result.records[0]['s']
    """
    ratings_lst = []
    for platform in ['naver', 'kakao', 'google']:
        pf_rating = node[f'rating_{platform}']
        if pf_rating:
            pass
        else:
            continue
        pf_rc = node[f'rating_count_{platform}']
        if pf_rc:
            pass
        else:
            continue
        ratings_lst.append(f"{platform.capitalize()} {pf_rating}({pf_rc}명)")
    rating_str = '  '.join(ratings_lst)
    return rating_str