from openai import OpenAI
from flask import current_app  # 用于访问 Flask 的配置
import requests
import json

# 初始化 OpenAI 客户端
def query_llm(prompt, model="deepseek-chat"):
    '''封装 OpenAI 的接口'''
    # 从 Flask 配置中获取 API Key 和 Base URL
    api_key = current_app.config['DEEPSEEK_API_KEY']
    base_url = current_app.config['DEEPSEEK_BASE_URL']

    client = OpenAI(api_key=api_key, base_url=base_url)

    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,  # 模型输出的随机性，0 表示随机性最小
    )
    return response.choices[0].message.content