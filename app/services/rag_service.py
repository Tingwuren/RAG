import logging
from .prompt_service import build_prompt, prompt_template, general_prompt_template
from .rrf_service import rrf
from .reranker_service import get_reranker, rerank_with_model
from flask import current_app
from .llm_service import query_llm
from .ollama_service import query_local_llm
from .file_service import build_vector_to_doc_map
# 配置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RAG_Bot:
    def __init__(self, vector_db, es_connector, llm_api, collection_name, n_results=5, vector_top_n=10, es_top_n=10):
        """
        初始化 RAG_Bot
        :param vector_db: 向量数据库连接器
        :param es_connector: Elasticsearch 连接器
        :param llm_api: LLM API 接口
        :param n_results: 最终返回的结果数
        :param vector_top_n: 向量数据库检索的条目上限
        :param es_top_n: Elasticsearch 检索的条目上限
        """
        self.vector_db = vector_db
        self.es_connector = es_connector
        self.llm_api = llm_api
        self.collection_name = collection_name  # 知识库名称
        self.n_results = n_results
        self.vector_top_n = vector_top_n
        self.es_top_n = es_top_n
        self.reranker = get_reranker()  # 初始化 reranker 模型

    def chat(self, user_query):
        # 向量数据库检索
        vector_results = self.vector_db.search(self.collection_name, user_query, self.vector_top_n)
        logging.info(f'向量数据库检索结果：{vector_results["ids"]}')
        for i, (doc_id, doc) in enumerate(zip(vector_results['ids'][0], vector_results['documents'][0])):
            logging.info(f"文档 {i + 1} (ID: {doc_id}): {doc}")

        # Elasticsearch 检索
        keyword_results = self.es_connector.search(self.collection_name, user_query, self.es_top_n)
        logging.info(f'Elasticsearch 检索结果：{keyword_results["ids"]}')
        for i, (doc_id, doc) in enumerate(zip(keyword_results['ids'][0], keyword_results['documents'][0])):
            logging.info(f"文档 {i + 1} (ID: {doc_id}): {doc}")

        # RRF 排序
        combined_results = rrf([vector_results, keyword_results])
        logging.info(f'RRF 排序后的结果：{combined_results["ids"]}')
        for i, (doc_id, doc) in enumerate(zip(combined_results['ids'][0], combined_results['documents'][0])):
            logging.info(f"文档 {i + 1} (ID: {doc_id}): {doc}")

        # 使用 reranker 进行重排序
        final_results = rerank_with_model(self.reranker, user_query, combined_results)
        logging.info(f'Reranker 重排序后的结果：{final_results["ids"]}')
        for i, (doc_id, doc) in enumerate(zip(final_results['ids'][0], final_results['documents'][0])):
            logging.info(f"文档 {i + 1} (ID: {doc_id}): {doc}")

        # 构建提示并生成回复
        prompt = build_prompt(general_prompt_template, context=final_results['documents'][0][:self.n_results], query=user_query)
        logging.info(f'提示：{prompt}')
        response = self.llm_api(prompt)
        return response

def chat_with_rag(knowledge_name, user_query, model_type="cloud", model_name=None, temperature=None):
    """
    使用RAG进行对话，支持模型选择

    参数:
        knowledge_name: 知识库名称
        user_query: 用户查询
        model_type: 模型类型 ("local" 或 "cloud")
        model_name: 具体模型名称
        temperature: 温度参数
    """
    from .model_service import ModelService

    # 创建一个包装函数来使用统一模型服务
    def llm_api_wrapper(prompt):
        return ModelService.query_model(
            prompt=prompt,
            model_type=model_type,
            model_name=model_name,
            temperature=temperature
        )

    bot = RAG_Bot(current_app.vector_db, current_app.es_connector, llm_api=llm_api_wrapper, collection_name=knowledge_name)

    # 用户查询
    response = bot.chat(user_query)
    logging.info(f'响应：{response}')
    return response

class Dialect_RAG_Bot:
    def __init__(self, vector_db, es_connector, llm_api, n_results=5, vector_top_n=10, es_top_n=10):
        """
        初始化 RAG_Bot
        :param vector_db: 向量数据库连接器
        :param es_connector: Elasticsearch 连接器
        :param llm_api: LLM API 接口
        :param n_results: 最终返回的结果数
        :param vector_top_n: 向量数据库检索的条目上限
        :param es_top_n: Elasticsearch 检索的条目上限
        """
        self.vector_db = vector_db
        self.es_connector = es_connector
        self.llm_api = llm_api
        self.n_results = n_results
        self.vector_top_n = vector_top_n
        self.es_top_n = es_top_n
        self.reranker = get_reranker()  # 初始化 reranker 模型
        
    def map_retrieved_vectors_to_documents(self, retrieved_vectors):
        full_documents = []
        for vec in retrieved_vectors:
            if vec in self.rhyme_map:
                full_documents.append(self.rhyme_map[vec])
            elif vec in self.word_map:
                full_documents.append(self.word_map[vec])
        return full_documents

    def chat(self, user_query):
        collection_name = "defualt"
        
        
        # 向量数据库检索
        vector_results = self.vector_db.search(collection_name, user_query, self.vector_top_n)
        logging.info(f'向量数据库检索结果：{vector_results["ids"]}')
        for i, (doc_id, doc) in enumerate(zip(vector_results['ids'][0], vector_results['documents'][0])):
            logging.info(f"文档 {i + 1} (ID: {doc_id}): {doc}")

        # Elasticsearch 检索
        keyword_results = self.es_connector.search(collection_name, user_query, top_n=self.es_top_n)
        logging.info(f'Elasticsearch 检索结果：{keyword_results["ids"]}')
        for i, (doc_id, doc) in enumerate(zip(keyword_results['ids'][0], keyword_results['documents'][0])):
            logging.info(f"文档 {i + 1} (ID: {doc_id}): {doc}")

        # RRF 排序
        combined_results = rrf([vector_results, keyword_results])
        logging.info(f'RRF 排序后的结果：{combined_results["ids"]}')
        for i, (doc_id, doc) in enumerate(zip(combined_results['ids'][0], combined_results['documents'][0])):
            logging.info(f"文档 {i + 1} (ID: {doc_id}): {doc}")

        # 使用 reranker 进行重排序
        final_results = rerank_with_model(self.reranker, user_query, combined_results)
        logging.info(f'Reranker 重排序后的结果：{final_results["ids"]}')
        for i, (doc_id, doc) in enumerate(zip(final_results['ids'][0], final_results['documents'][0])):
            logging.info(f"文档 {i + 1} (ID: {doc_id}): {doc}")

        
        full_documents = self.map_retrieved_vectors_to_documents(final_results['documents'][0])


        # 构建提示并生成回复
        prompt = build_prompt(prompt_template, context=full_documents[:self.n_results], query=user_query)
        logging.info(f'提示：{prompt}')
        response = self.llm_api(prompt)
        return response
    
    

    
def chat_with_dialect_rag(user_query, model_type="cloud", model_name=None, temperature=None):
    """
    使用方言RAG进行对话，支持模型选择

    参数:
        user_query: 用户查询
        model_type: 模型类型 ("local" 或 "cloud")
        model_name: 具体模型名称
        temperature: 温度参数
    """
    from .model_service import ModelService

    # 创建一个包装函数来使用统一模型服务
    def llm_api_wrapper(prompt):
        return ModelService.query_model(
            prompt=prompt,
            model_type=model_type,
            model_name=model_name,
            temperature=temperature
        )

    bot = Dialect_RAG_Bot(current_app.vector_db, current_app.es_connector, llm_api=llm_api_wrapper)
    bot.all_documents = current_app.all_documents  # 传递完整文档内容
    bot.rhyme_vector_data = current_app.rhyme_vector_data  # 传递韵母对照表的向量数据
    bot.rhyme_documents = current_app.rhyme_documents  # 传递韵母对照表的文档
    bot.table_vector_data = current_app.table_vector_data  # 传递简明词汇表的向量数据
    bot.word_documents = current_app.word_documents  # 传递简明词汇表的文档
    bot.rhyme_map = build_vector_to_doc_map(bot.rhyme_vector_data, bot.rhyme_documents)
    bot.word_map = build_vector_to_doc_map(bot.table_vector_data, bot.word_documents)

    # 用户查询
    response = bot.chat(user_query)
    logging.info(f'响应：{response}')
    return response

def extract_core_query(user_input):
    """
    从用户问题中提取核心词 + 意图，如“你好 发音” / “听 字义”
    """
    import re

    # 提取 1~4 个连续汉字词
    word_match = re.findall(r"[\u4e00-\u9fa5]{1,4}", user_input)
    keyword = word_match[0] if word_match else user_input.strip()

    if "怎么说" in user_input or "怎么讲" in user_input or "口音" in user_input or "发音" in user_input or "怎么读" in user_input:
        return f"{keyword} 发音"
    elif "什么意思" in user_input or "含义" in user_input or "解释" in user_input:
        return f"{keyword} 字义"
    else:
        return keyword


