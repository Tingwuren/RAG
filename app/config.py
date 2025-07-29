# 应用内部配置模块，如配置默认参数、日志等
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://myuser:mypassword@localhost:3306/mydatabase"
    SECRET_KEY = '123456'  # 用于启用 session 和 cookie 的加密

    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    
    # Ollama 配置
    OLLAMA_API_URL = "http://localhost:11434"    # Ollama API的URL
    OLLAMA_DEFAULT_MODEL = "deepseek-r1:8b"     # 默认的Ollama模型
    OLLAMA_DEFAULT_TEMPERATURE = 0.5             # 默认的温度参数
    
    KNOWLEDGE_BASE_PATH = "./knowledge"
    
    CHROMA_PERSIST_DIR = "./data/chroma"
    
    ELASTICSEARCH_URL = "http://localhost:9200"