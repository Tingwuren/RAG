from flask import Blueprint, request, jsonify, session, current_app
from app.services.llm_service import query_llm  # 从服务层导入大模型接口逻辑
from app.services.ollama_service import query_local_llm
from app.services.model_service import ModelService  # 导入统一模型服务
from app.services.rag_service import chat_with_rag, chat_with_dialect_rag  # 导入 RAG 服务
import os

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/', methods=['POST'])
def chat():
    """
    调用大模型对话接口，要求用户登录，支持模型选择
    """
    try:
        # 检查用户是否已登录
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 获取用户输入
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'message': 'No query provided'}), 400

        user_query = data['query']
        model_type = data.get('model_type', 'local')  # 默认使用本地模型
        model_name = data.get('model_name')  # 具体模型名称
        temperature = data.get('temperature')  # 温度参数

        # 使用统一模型服务调用模型
        response = ModelService.query_model(
            prompt=user_query,
            model_type=model_type,
            model_name=model_name,
            temperature=temperature
        )

        # 返回模型回复
        return jsonify({
            'query': user_query,
            'response': response,
            'model_type': model_type,
            'model_name': model_name
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error occurred: {str(e)}'}), 500


@chat_bp.route('/models', methods=['GET'])
def get_available_models():
    """
    获取可用的模型类型和模型列表
    """
    try:
        # 检查用户是否已登录
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 获取可用的模型类型
        model_types = ModelService.get_available_model_types()

        return jsonify({
            'message': '获取模型列表成功',
            'model_types': model_types
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error occurred: {str(e)}'}), 500


@chat_bp.route('/with-knowledge', methods=['POST'])
def chat_with_knowledge():
    """
    用户选择知识库进行对话，支持模型选择
    """
    try:
        # 检查用户是否已登录
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 获取请求数据
        data = request.get_json()
        if not data or 'knowledge_name' not in data or 'query' not in data:
            return jsonify({'message': '知识库名称和查询内容不能为空！'}), 400

        knowledge_name = data['knowledge_name']
        user_query = data['query']
        model_type = data.get('model_type', 'cloud')  # 默认使用云端模型
        model_name = data.get('model_name')
        temperature = data.get('temperature')

        # 检查知识库是否存在
        base_path = current_app.config.get('KNOWLEDGE_BASE_PATH', './knowledge')
        knowledge_path = os.path.join(base_path, knowledge_name)
        if not os.path.exists(knowledge_path):
            return jsonify({'message': f'知识库 "{knowledge_name}" 不存在！'}), 404

        # 调用 RAG 服务进行对话，传递模型参数
        response = chat_with_rag(
            knowledge_name,
            user_query,
            model_type=model_type,
            model_name=model_name,
            temperature=temperature
        )

        return jsonify({
            'message': '对话成功！',
            'response': response,
            'model_type': model_type,
            'model_name': model_name
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error occurred: {str(e)}'}), 500

@chat_bp.route('/with-dialect-knowledge', methods=['POST'])
def chat_with_dialect_knowledge():
    """
    用户选择方言知识库进行对话，支持模型选择
    """
    try:
        # 检查用户是否已登录
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 获取请求数据
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'message': '查询内容不能为空！'}), 400

        user_query = data['query']
        model_type = data.get('model_type', 'cloud')  # 默认使用云端模型
        model_name = data.get('model_name')
        temperature = data.get('temperature')

        # 调用方言RAG服务，传递模型参数
        response = chat_with_dialect_rag(
            user_query,
            model_type=model_type,
            model_name=model_name,
            temperature=temperature
        )

        return jsonify({
            'message': '对话成功！',
            'response': response,
            'model_type': model_type,
            'model_name': model_name
        }), 200

    except Exception as e:
        return jsonify({'message': f'Error occurred: {str(e)}'}), 500