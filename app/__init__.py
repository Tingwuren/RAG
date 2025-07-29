from flask import Flask
from .extensions import db, MyVectorDBConnector, MyEsConnector
from .routes import auth_bp, chat_bp, knowledge_bp
from .config import Config
from .services.embedding_service import get_embeddings
from .services.file_service import process_rhyme_table, process_word_table
from .utils.chinese_utils import to_keywords 
from elasticsearch7 import Elasticsearch
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    
    # 初始化 ChromaDB Connector，使用配置文件中的持久化目录
    vector_db = MyVectorDBConnector(
        embedding_fn=get_embeddings,
        persist_directory=app.config.get("CHROMA_PERSIST_DIR")
    )
    app.vector_db = vector_db
    
    # 初始化 Elasticsearch Connector
    es = Elasticsearch(app.config.get("ELASTICSEARCH_URL"))
    es_connector = MyEsConnector(
        es_client=es,
        keyword_fn=to_keywords
    )
    app.es_connector = es_connector
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(knowledge_bp)

    with app.app_context():
        db.create_all()# 在应用上下文中创建数据库表

        # 使用 process_rhyme_table 处理韵母对照表
        rhyme_vector_data, rhyme_documents = process_rhyme_table()
        logging.info(f"处理后的韵母对照表文档数：{len(rhyme_documents)}")
        # 输出韵母对照表的前十个文档内容和向量数据
        for i, (doc, vector) in enumerate(zip(rhyme_documents[:10], rhyme_vector_data[:10])):
            logging.info(f"韵母对照表向量 {i + 1}: {vector}")
            logging.info(f"韵母对照表文档 {i + 1}: {doc}")

        # 使用 process_table 处理简明词汇表
        table_vector_data, word_documents = process_word_table()
        logging.info(f"处理后的简明词汇文档数：{len(word_documents)}")
        # 输出简明词汇表的前十个文档内容和向量数据
        for i, (doc, vector) in enumerate(zip(word_documents[:10], table_vector_data[:10])):
            logging.info(f"简明词汇表向量 {i + 1}: {vector}")
            logging.info(f"简明词汇表文档 {i + 1}: {doc}")

        # 合并向量数据和文档
        all_vector_data = rhyme_vector_data + table_vector_data
        all_documents = rhyme_documents + word_documents

        # 存储到向量数据库
        vector_db.add_documents("defualt", all_vector_data)

        # 存储到 Elasticsearch
        es_connector.add_documents("defualt", all_vector_data)
        
        app.all_vector_data = all_vector_data  # 将所有向量数据存储在应用上下文中
        app.all_documents = all_documents  # 将所有文档存储在应用上下文中
        app.rhyme_vector_data = rhyme_vector_data  # 将韵母对照表的向量数据存储在应用上下文中
        app.rhyme_documents = rhyme_documents  # 将韵母对照表的文档存储在应用上下文中
        app.table_vector_data = table_vector_data  # 将简明词汇表的向量数据存储在应用上下文中
        app.word_documents = word_documents  # 将简明词汇表的文档存储在应用上下文中
    
    return app