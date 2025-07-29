import requests
import json
from flask import current_app

# 尝试导入ollama库，如果不存在则忽略
try:
    import ollama
    OLLAMA_LIBRARY_AVAILABLE = True
except ImportError:
    OLLAMA_LIBRARY_AVAILABLE = False

def query_local_llm(prompt=None, messages=None, model=None, temperature=None, stream=False, system=None):
    '''封装 Ollama 本地模型的接口
    
    参数:
        prompt: 单个提示词，如果提供了messages，此参数会被忽略
        messages: 对话历史消息列表，格式为[{"role": "user", "content": "内容"}, {"role": "assistant", "content": "回复"}]
        model: 要使用的Ollama模型名称
        temperature: 温度参数，控制输出的随机性，0-1之间
        stream: 是否使用流式返回
        system: 系统提示，用于设置模型的行为
        
    返回:
        非流式模式下返回模型响应的文本内容
        流式模式下返回完整的响应对象，需要调用者自行处理
    '''
    # 从配置中获取默认值
    if model is None:
        model = current_app.config.get('OLLAMA_DEFAULT_MODEL', 'deepseek-r1:8b')
    
    if temperature is None:
        temperature = current_app.config.get('OLLAMA_DEFAULT_TEMPERATURE', 0.5)
    
    # 获取API基础URL
    base_url = current_app.config.get('OLLAMA_API_URL', 'http://localhost:11434')
    ollama_api_url = f"{base_url}/api/chat"
    
    # 构建请求数据
    data = {
        "model": model,
        "options": {
            "temperature": temperature
        },
        "stream": stream
    }
    
    # 添加系统提示
    if system:
        data["system"] = system
    
    # 处理消息
    if messages is not None:
        data["messages"] = messages
    elif prompt is not None:
        data["messages"] = [{"role": "user", "content": prompt}]
    else:
        return "错误: 必须提供prompt或messages参数"
    
    # 发送请求
    try:
        response = requests.post(ollama_api_url, json=data)
        response_data = response.json()
        
        # 检查是否有错误
        if "error" in response_data:
            return f"错误: {response_data['error']}"
        
        # 如果没有stream，直接返回内容
        if not stream:
            return response_data["message"]["content"]
        
        # 如果是stream模式，返回整个响应对象，由调用者处理流
        return response_data
    except Exception as e:
        return f"调用Ollama API时出错: {str(e)}"

def stream_local_llm(prompt=None, messages=None, model=None, temperature=None, system=None):
    '''获取Ollama模型的流式响应
    
    参数与query_local_llm相同，但专门用于处理流式响应
    
    返回:
        生成器，产生模型流式响应的文本片段
    '''
    # 从配置中获取默认值
    if model is None:
        model = current_app.config.get('OLLAMA_DEFAULT_MODEL', 'deepseek-r1:8b')
    
    if temperature is None:
        temperature = current_app.config.get('OLLAMA_DEFAULT_TEMPERATURE', 0.5)
    
    # 获取API基础URL
    base_url = current_app.config.get('OLLAMA_API_URL', 'http://localhost:11434')
    ollama_api_url = f"{base_url}/api/chat"
    
    # 构建请求数据
    data = {
        "model": model,
        "options": {
            "temperature": temperature
        },
        "stream": True
    }
    
    # 添加系统提示
    if system:
        data["system"] = system
    
    # 处理消息
    if messages is not None:
        data["messages"] = messages
    elif prompt is not None:
        data["messages"] = [{"role": "user", "content": prompt}]
    else:
        yield "错误: 必须提供prompt或messages参数"
        return
    
    # 发送请求
    try:
        # 使用stream=True参数来获取流式响应
        with requests.post(ollama_api_url, json=data, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    # 解析JSON响应
                    try:
                        chunk = json.loads(line)
                        # 提取文本内容
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
                    except json.JSONDecodeError:
                        yield f"错误: 无法解析JSON响应: {line}"
    except Exception as e:
        yield f"调用Ollama API流式响应时出错: {str(e)}"

def query_ollama_lib(prompt=None, messages=None, model=None, temperature=None, stream=False, system=None):
    '''使用Ollama官方Python库调用本地模型
    
    参数:
        prompt: 单个提示词，如果提供了messages，此参数会被忽略
        messages: 对话历史消息列表，格式为[{"role": "user", "content": "内容"}, {"role": "assistant", "content": "回复"}]
        model: 要使用的Ollama模型名称
        temperature: 温度参数，控制输出的随机性，0-1之间
        stream: 是否使用流式返回
        system: 系统提示，用于设置模型的行为
        
    返回:
        非流式模式下返回模型响应的文本内容
        流式模式下返回响应对象，对于流式响应需要遍历返回的生成器
    '''
    if not OLLAMA_LIBRARY_AVAILABLE:
        return "错误: Ollama Python库未安装，请使用pip install ollama安装"
    
    # 从配置中获取默认值
    if model is None:
        model = current_app.config.get('OLLAMA_DEFAULT_MODEL', 'deepseek-r1:8b')
    
    if temperature is None:
        temperature = current_app.config.get('OLLAMA_DEFAULT_TEMPERATURE', 0.5)
    
    try:
        # 准备选项参数
        options = {"temperature": temperature}
        
        # 处理消息
        if messages is None and prompt is not None:
            messages = [{"role": "user", "content": prompt}]
        
        if messages is None:
            return "错误: 必须提供prompt或messages参数"
        
        # 如果有系统提示，添加到消息列表的开头
        if system:
            # 检查是否已经有system消息
            has_system = False
            for msg in messages:
                if msg.get("role") == "system":
                    has_system = True
                    break
            
            if not has_system:
                messages.insert(0, {"role": "system", "content": system})
        
        # 调用ollama库进行聊天
        response = ollama.chat(
            model=model,
            messages=messages,
            options=options,
            stream=stream
        )
        
        # 对于非流式响应，直接返回内容
        if not stream:
            return response["message"]["content"]
        
        # 对于流式响应，返回原始响应对象，由调用者处理流
        return response
    except Exception as e:
        return f"调用Ollama库时出错: {str(e)}"

def stream_ollama_lib(prompt=None, messages=None, model=None, temperature=None, system=None):
    '''使用Ollama官方Python库获取流式响应
    
    参数与query_ollama_lib相同，但专门用于处理流式响应
    
    返回:
        生成器，产生模型流式响应的文本片段
    '''
    if not OLLAMA_LIBRARY_AVAILABLE:
        yield "错误: Ollama Python库未安装，请使用pip install ollama安装"
        return
    
    # 从配置中获取默认值
    if model is None:
        model = current_app.config.get('OLLAMA_DEFAULT_MODEL', 'deepseek-r1:8b')
    
    if temperature is None:
        temperature = current_app.config.get('OLLAMA_DEFAULT_TEMPERATURE', 0.5)
    
    try:
        # 准备选项参数
        options = {"temperature": temperature}
        
        # 处理消息
        if messages is None and prompt is not None:
            messages = [{"role": "user", "content": prompt}]
        
        if messages is None:
            yield "错误: 必须提供prompt或messages参数"
            return
        
        # 如果有系统提示，添加到消息列表的开头
        if system:
            # 检查是否已经有system消息
            has_system = False
            for msg in messages:
                if msg.get("role") == "system":
                    has_system = True
                    break
            
            if not has_system:
                messages.insert(0, {"role": "system", "content": system})
        
        # 调用ollama库进行流式聊天
        stream = ollama.chat(
            model=model,
            messages=messages,
            options=options,
            stream=True
        )
        
        # 处理流式响应
        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]
    except Exception as e:
        yield f"调用Ollama库流式响应时出错: {str(e)}"

def get_available_models():
    '''获取本地可用的Ollama模型列表'''
    if OLLAMA_LIBRARY_AVAILABLE:
        try:
            # 使用官方库获取模型列表
            models_data = ollama.list()
            if "models" in models_data:
                return [model["name"] for model in models_data["models"]]
            return []
        except Exception as e:
            return [f"获取模型列表出错: {str(e)}"]
    
    # 使用API获取模型列表
    try:
        base_url = current_app.config.get('OLLAMA_API_URL', 'http://localhost:11434')
        response = requests.get(f"{base_url}/api/tags")
        if response.status_code == 200:
            data = response.json()
            if "models" in data:
                return [model["name"] for model in data["models"]]
        return []
    except Exception:
        return [] 