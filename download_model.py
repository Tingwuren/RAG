from sentence_transformers import SentenceTransformer
from sentence_transformers import CrossEncoder

def download_embedding_model(model_name, save_path):
    """
    下载嵌入模型到本地
    :param model_name: 模型名称（如 "BAAI/bge-m3"）
    :param save_path: 本地保存路径
    """
    model = SentenceTransformer(model_name)
    model.save(save_path)
    print(f"Embedding 模型已保存到 {save_path}")
    
def download_reranker_model(model_name, save_path):
    """
    下载 reranker 模型到本地
    :param model_name: 模型名称（如 "BAAI/bge-reranker-large"）
    :param save_path: 本地保存路径
    """
    model = CrossEncoder(model_name, max_length=512)
    model.save(save_path)
    print(f"Reranker 模型已保存到 {save_path}")

if __name__ == "__main__":
    download_embedding_model("BAAI/bge-m3", "./models/bge-m3")
    download_reranker_model("BAAI/bge-reranker-large", "./models/bge-reranker-large")