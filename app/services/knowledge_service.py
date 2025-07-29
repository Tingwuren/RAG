import os

def create_knowledge_base(base_path, knowledge_name):
    """
    创建知识库文件夹
    :param base_path: 知识库的根路径
    :param knowledge_name: 知识库名称
    :return: 创建结果
    """
    knowledge_path = os.path.join(base_path, knowledge_name)

    if os.path.exists(knowledge_path):
        raise FileExistsError(f"知识库 '{knowledge_name}' 已经存在！")

    os.makedirs(knowledge_path)
    return knowledge_path