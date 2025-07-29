from flask import current_app
from .llm_service import query_llm
from .ollama_service import query_local_llm, query_ollama_lib, get_available_models
import logging

class ModelService:
    """统一的模型调用服务，支持本地和云端模型选择"""
    
    # 模型类型常量
    MODEL_TYPE_LOCAL = "local"
    MODEL_TYPE_CLOUD = "cloud"
    
    @staticmethod
    def get_available_model_types():
        """获取可用的模型类型"""
        return {
            "local": {
                "name": "本地模型 (Ollama)",
                "description": "使用本地部署的Ollama模型",
                "models": ModelService.get_local_models()
            },
            "cloud": {
                "name": "云端模型 (DeepSeek)",
                "description": "使用DeepSeek云端API",
                "models": ["deepseek-chat", "deepseek-coder"]
            }
        }
    
    @staticmethod
    def get_local_models():
        """获取本地可用的模型列表"""
        try:
            models = get_available_models()
            if not models or (len(models) == 1 and "获取模型列表出错" in models[0]):
                # 如果获取失败，返回默认模型
                return [current_app.config.get('OLLAMA_DEFAULT_MODEL', 'deepseek-r1:8b')]
            return models
        except Exception as e:
            logging.error(f"获取本地模型列表失败: {str(e)}")
            return [current_app.config.get('OLLAMA_DEFAULT_MODEL', 'deepseek-r1:8b')]
    
    @staticmethod
    def query_model(prompt=None, messages=None, model_type="local", model_name=None, 
                   temperature=None, stream=False, system=None):
        """
        统一的模型查询接口
        
        参数:
            prompt: 单个提示词
            messages: 对话历史消息列表
            model_type: 模型类型 ("local" 或 "cloud")
            model_name: 具体的模型名称
            temperature: 温度参数
            stream: 是否使用流式返回
            system: 系统提示
            
        返回:
            模型响应的文本内容
        """
        try:
            if model_type == ModelService.MODEL_TYPE_LOCAL:
                return ModelService._query_local_model(
                    prompt=prompt, 
                    messages=messages, 
                    model=model_name, 
                    temperature=temperature, 
                    stream=stream, 
                    system=system
                )
            elif model_type == ModelService.MODEL_TYPE_CLOUD:
                return ModelService._query_cloud_model(
                    prompt=prompt, 
                    messages=messages, 
                    model=model_name, 
                    temperature=temperature, 
                    system=system
                )
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
                
        except Exception as e:
            logging.error(f"模型查询失败: {str(e)}")
            return f"模型调用出错: {str(e)}"
    
    @staticmethod
    def _query_local_model(prompt=None, messages=None, model=None, temperature=None, 
                          stream=False, system=None):
        """调用本地模型"""
        return query_local_llm(
            prompt=prompt,
            messages=messages,
            model=model,
            temperature=temperature,
            stream=stream,
            system=system
        )
    
    @staticmethod
    def _query_cloud_model(prompt=None, messages=None, model=None, temperature=None, system=None):
        """调用云端模型"""
        # 对于云端模型，我们需要处理不同的参数格式
        if messages is not None:
            # 如果有消息历史，需要转换为单个prompt
            # 这里简化处理，实际可能需要更复杂的逻辑
            if system:
                full_prompt = f"系统: {system}\n\n"
            else:
                full_prompt = ""
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    full_prompt += f"用户: {content}\n"
                elif role == "assistant":
                    full_prompt += f"助手: {content}\n"
                elif role == "system" and not system:
                    full_prompt = f"系统: {content}\n\n" + full_prompt
            
            return query_llm(full_prompt, model=model or "deepseek-chat")
        elif prompt is not None:
            if system:
                full_prompt = f"系统: {system}\n\n用户: {prompt}"
            else:
                full_prompt = prompt
            return query_llm(full_prompt, model=model or "deepseek-chat")
        else:
            raise ValueError("必须提供prompt或messages参数")

def get_model_service():
    """获取模型服务实例"""
    return ModelService()
