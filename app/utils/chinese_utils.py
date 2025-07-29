import jieba

def to_keywords(text):
    """
    将输入文本转换为关键词列表。
    使用 jieba 分词工具提取关键词。
    """
    # 使用 jieba 分词
    words = jieba.lcut(text)
    
    # 去除停用词和无意义的短词
    keywords = [word for word in words if len(word) > 1]
    
    return " ".join(keywords)