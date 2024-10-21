from neo4j import GraphDatabase
import os

graphdb_driver = GraphDatabase.driver(uri=os.environ["NEO4J_URI"], 
                                      auth=(
                                          os.environ["NEO4J_USERNAME"],
                                          os.environ["NEO4J_PASSWORD"]
                                          )
                                        )