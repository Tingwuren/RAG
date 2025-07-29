from sentence_transformers import CrossEncoder

def get_reranker(model_path="./models/bge-reranker-large"):
    """
    加载本地保存的 reranker 模型
    :param model_path: 本地模型路径
    :return: CrossEncoder 模型实例
    """
    model = CrossEncoder(model_path, max_length=512)
    return model

def rerank_with_model(reranker, query, combined_results):
    """
    使用 reranker 模型对 RRF 排序后的结果进行重排序。

    :param reranker: 已加载的 reranker 模型
    :param query: 用户查询
    :param combined_results: RRF 排序后的结果
    :return: 重排序后的结果，格式与 combined_results 一致
    """
    # 构造 reranker 输入
    reranker_inputs = [(query, doc) for doc in combined_results['documents'][0]]
    
    # 使用 reranker 模型预测分数
    reranker_scores = reranker.predict(reranker_inputs)
    
    # 根据分数进行排序
    reranked_results = sorted(
        zip(reranker_scores, combined_results['ids'][0], combined_results['documents'][0]),
        key=lambda x: x[0],
        reverse=True
    )
    
    # 构造重排序后的结果
    final_results = {
        "ids": [[item[1] for item in reranked_results]],
        "documents": [[item[2] for item in reranked_results]],
        "embeddings": None
    }
    return final_results