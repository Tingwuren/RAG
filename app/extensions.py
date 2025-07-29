# 第三方扩展（如 SQLAlchemy、缓存、消息队列等）的初始化
from flask_sqlalchemy import SQLAlchemy
import chromadb
from chromadb.config import Settings
import os
import time
from elasticsearch7.helpers import bulk

db = SQLAlchemy()

class MyVectorDBConnector:
    def __init__(self, embedding_fn, persist_directory=None):
        """
        :param embedding_fn: 生成向量嵌入的函数
        :param persist_directory: 持久化存储路径，若为 None，则使用内存模式
        """
        print(f"Initializing ChromaDB with persist_directory={persist_directory}")
        # 确保目标目录存在
        os.makedirs(persist_directory, exist_ok=True)
        print(f"Persist directory '{persist_directory}' created.")
        # 创建 Chroma 客户端
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_fn

    def get_or_create_collection(self, collection_name):
        """
        获取或创建指定的 collection
        :param collection_name: 知识库名称
        :return: ChromaDB collection 对象
        """
        return self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, collection_name, documents):
        """
        向指定 collection 中添加文档及其向量表示
        :param collection_name: 知识库名称
        :param documents: 文档列表
        """
        
        # 删除并重新创建 collection
        if collection_name in self.client.list_collections():
            self.client.delete_collection(name=collection_name)
            print(f"Collection '{collection_name}' has been deleted.")
        
        collection = self.get_or_create_collection(collection_name)
        embeddings = self.embedding_fn(documents)
        ids = [f"id{i}" for i in range(len(documents))]
        collection.add(
            embeddings=embeddings,
            documents=documents,
            ids=ids
        )
        # 显式触发持久化
        # self.client.persist()
        # print(f"ChromaDB 数据已持久化到磁盘 for collection '{collection_name}'")
        print(f"Add {len(documents)} documents to ChromaDB collection '{collection_name}'")

    def search(self, collection_name, query, top_n):
        """
        使用查询字符串检索指定 collection 中的向量数据库
        :param collection_name: 知识库名称
        :param query: 查询字符串
        :param top_n: 返回的结果数量
        :return: 检索结果
        """
        collection = self.get_or_create_collection(collection_name)
        query_embedding = self.embedding_fn([query])
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_n
        )
        return results

    def delete_collection(self, collection_name):
        """
        删除指定的collection
        :param collection_name: 要删除的知识库名称
        :return: 删除是否成功
        """
        try:
            if collection_name in [c.name for c in self.client.list_collections()]:
                self.client.delete_collection(name=collection_name)
                print(f"Collection '{collection_name}' has been deleted from ChromaDB.")
                return True
            else:
                print(f"Collection '{collection_name}' not found in ChromaDB.")
                return False
        except Exception as e:
            print(f"Error deleting ChromaDB collection '{collection_name}': {str(e)}")
            return False

class MyEsConnector:
    def __init__(self, es_client, keyword_fn):
        """
        初始化 Elasticsearch 连接器
        :param es_client: Elasticsearch 客户端实例
        :param keyword_fn: 用于提取关键词的函数
        """
        self.es_client = es_client
        self.keyword_fn = keyword_fn

    def add_documents(self, collection_name, documents):
        """
        向指定知识库（索引）中添加文档
        :param collection_name: 知识库名称（对应 Elasticsearch 索引名称）
        :param documents: 文档列表
        """
        index_name = collection_name  # 使用知识库名称作为索引名称

        # 如果索引已存在，删除并重新创建
        if self.es_client.indices.exists(index=index_name):
            self.es_client.indices.delete(index=index_name)
        self.es_client.indices.create(index=index_name)

        # 构造批量操作
        actions = [
            {
                "_index": index_name,
                "_id": f"id{i}",  # 使用文档 ID
                "_source": {
                    "keywords": self.keyword_fn(doc),
                    "text": doc
                }
            }
            for i, doc in enumerate(documents)
        ]

        # 批量插入文档
        bulk(self.es_client, actions)
        time.sleep(1)  # 等待索引刷新
        print(f"Add {len(documents)} documents to Elasticsearch index '{collection_name}'")

    def search(self, collection_name, query_string, top_n=3):
        """
        在指定知识库（索引）中搜索文档
        :param collection_name: 知识库名称（对应 Elasticsearch 索引名称）
        :param query_string: 查询字符串
        :param top_n: 返回的结果数量
        :return: 检索结果
        """
        index_name = collection_name  # 使用知识库名称作为索引名称

        # 构造搜索查询
        search_query = {
            "match": {
                "keywords": self.keyword_fn(query_string)
            }
        }

        # 执行搜索
        res = self.es_client.search(
            index=index_name, query=search_query, size=top_n
        )

        # 构造与 results 格式一致的返回值
        results = {
            "ids": [[hit["_id"] for hit in res["hits"]["hits"]]],  # 使用 _id 作为文档 ID
            "documents": [[hit["_source"]["text"] for hit in res["hits"]["hits"]]],
            "embeddings": None  # Elasticsearch 不返回嵌入信息
        }
        return results

    def delete_index(self, index_name):
        """
        删除Elasticsearch中的指定索引
        :param index_name: 要删除的索引名称（知识库名称）
        :return: 删除是否成功
        """
        try:
            if self.es_client.indices.exists(index=index_name):
                self.es_client.indices.delete(index=index_name)
                print(f"Index '{index_name}' has been deleted from Elasticsearch.")
                return True
            else:
                print(f"Index '{index_name}' not found in Elasticsearch.")
                return False
        except Exception as e:
            print(f"Error deleting Elasticsearch index '{index_name}': {str(e)}")
            return False