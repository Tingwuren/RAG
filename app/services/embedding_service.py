from sentence_transformers import SentenceTransformer

def get_embeddings(text, model_path="./models/bge-m3", dimensions=None):
    """
    从本地加载嵌入模型并生成嵌入
    :param text: 输入文本
    :param model_path: 本地模型路径
    :param dimensions: 嵌入维度（可选，当前未使用）
    :return: 文本的嵌入向量
    """
    # 从本地加载模型
    model = SentenceTransformer(model_path)
    embeddings = model.encode(text)
    return embeddings