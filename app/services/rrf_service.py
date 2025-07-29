def rrf(ranks, k=1):
    """
    使用 Reciprocal Rank Fusion (RRF) 对多个排序结果进行融合。
    返回统一的 results 格式。
    """
    ret = {}
    for ranker in ranks:
        for i, doc_id in enumerate(ranker["ids"][0]):
            # 直接使用 doc_id，无需编号统一
            if doc_id not in ret:
                ret[doc_id] = {"score": 0, "text": ranker["documents"][0][i]}
            ret[doc_id]["score"] += 1.0 / (k + i)
    
    # 按分数排序
    sorted_items = sorted(ret.items(), key=lambda x: x[1]["score"], reverse=True)
    
    # 构造 results 格式
    results = {
        "ids": [[item[0] for item in sorted_items]],
        "documents": [[item[1]["text"] for item in sorted_items]],
        "embeddings": None  # RRF 不涉及嵌入信息
    }
    return results