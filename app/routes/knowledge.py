from flask import Blueprint, request, jsonify, current_app, session
from app.services.knowledge_service import create_knowledge_base
from app.services.file_service import extract_text_from_pdf
import os
import shutil  # 添加导入，用于删除目录

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')

@knowledge_bp.route('/create', methods=['POST'])
def create_knowledge():
    """
    用户新建知识库接口
    """
    try:
        # 检查用户是否已登录
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 获取请求数据
        data = request.get_json()
        if not data or 'knowledge_name' not in data:
            return jsonify({'message': '知识库名称不能为空！'}), 400

        knowledge_name = data['knowledge_name']

        # 知识库根路径
        base_path = current_app.config.get('KNOWLEDGE_BASE_PATH', './knowledge')

        # 调用服务层逻辑创建知识库
        knowledge_path = create_knowledge_base(base_path, knowledge_name)

        return jsonify({'message': '知识库创建成功！', 'path': knowledge_path}), 201

    except FileExistsError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'发生错误：{str(e)}'}), 500

@knowledge_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    用户向指定知识库上传 PDF 文件
    """
    try:
        # 检查用户是否已登录
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 获取知识库名称
        knowledge_name = request.form.get('knowledge_name')
        if not knowledge_name:
            return jsonify({'message': '知识库名称不能为空！'}), 400

        # 知识库根路径
        base_path = current_app.config.get('KNOWLEDGE_BASE_PATH', './knowledge')
        knowledge_path = os.path.join(base_path, knowledge_name)

        # 检查知识库是否存在
        if not os.path.exists(knowledge_path):
            return jsonify({'message': f'知识库 "{knowledge_name}" 不存在！'}), 404

        # 获取上传的文件
        if 'file' not in request.files:
            return jsonify({'message': '未找到上传的文件！'}), 400

        file = request.files['file']

        # 检查文件类型是否为 PDF
        if not file.filename.endswith('.pdf'):
            return jsonify({'message': '仅支持上传 PDF 文件！'}), 400

        # 保存文件到知识库文件夹
        file_path = os.path.join(knowledge_path, file.filename)
        file.save(file_path)

        return jsonify({'message': '文件上传成功！', 'file_path': file_path}), 201

    except Exception as e:
        return jsonify({'message': f'发生错误：{str(e)}'}), 500
    
@knowledge_bp.route('/process', methods=['POST'])
def process_knowledge_files():
    """
    处理知识库中的文件并存储到向量数据库和 Elasticsearch
    """
    try:
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 获取知识库名称
        data = request.get_json()
        if not data or 'knowledge_name' not in data:
            return jsonify({'message': '知识库名称不能为空！'}), 400

        knowledge_name = data['knowledge_name']
        base_path = current_app.config.get('KNOWLEDGE_BASE_PATH', './knowledge')
        knowledge_path = os.path.join(base_path, knowledge_name)

        # 检查知识库是否存在
        if not os.path.exists(knowledge_path):
            return jsonify({'message': f'知识库 "{knowledge_name}" 不存在！'}), 404

        # 遍历知识库中的 PDF 文件
        pdf_files = [f for f in os.listdir(knowledge_path) if f.endswith('.pdf')]
        if not pdf_files:
            return jsonify({'message': '知识库中没有 PDF 文件！'}), 400

        # 提取文本并存储到向量数据库和 Elasticsearch
        for pdf_file in pdf_files:
            pdf_path = os.path.join(knowledge_path, pdf_file)
            paragraphs = extract_text_from_pdf(pdf_path)
            for idx, para in enumerate(paragraphs):
                print(f"段落 {idx + 1}: {para}\n")
            current_app.vector_db.add_documents(knowledge_name, paragraphs)
            current_app.es_connector.add_documents(knowledge_name, paragraphs)

        return jsonify({'message': '知识库文件已成功处理并存储到向量数据库和 Elasticsearch！'}), 200

    except Exception as e:
        return jsonify({'message': f'发生错误：{str(e)}'}), 500

@knowledge_bp.route('/list', methods=['GET'])
def list_knowledge_bases():
    """
    获取所有知识库列表
    """
    try:
        # 检查用户是否已登录
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 知识库根路径
        base_path = current_app.config.get('KNOWLEDGE_BASE_PATH', './knowledge')
        
        # 确保目录存在
        if not os.path.exists(base_path):
            os.makedirs(base_path)
            return jsonify({'knowledge_bases': []}), 200
        
        # 获取所有知识库文件夹（排除隐藏文件夹和非目录）
        knowledge_bases = [
            folder for folder in os.listdir(base_path) 
            if not folder.startswith('.') and os.path.isdir(os.path.join(base_path, folder))
        ]
        
        return jsonify({'knowledge_bases': knowledge_bases}), 200

    except Exception as e:
        return jsonify({'message': f'发生错误：{str(e)}'}), 500

@knowledge_bp.route('/delete', methods=['POST'])
def delete_knowledge():
    """
    删除指定的知识库
    """
    try:
        # 检查用户是否已登录
        if 'username' not in session:
            return jsonify({'message': 'Unauthorized. Please log in first.'}), 401

        # 获取请求数据
        data = request.get_json()
        if not data or 'knowledge_name' not in data:
            return jsonify({'message': '知识库名称不能为空！'}), 400

        knowledge_name = data['knowledge_name']

        # 知识库根路径
        base_path = current_app.config.get('KNOWLEDGE_BASE_PATH', './knowledge')
        knowledge_path = os.path.join(base_path, knowledge_name)

        # 检查知识库是否存在
        if not os.path.exists(knowledge_path):
            return jsonify({'message': f'知识库 "{knowledge_name}" 不存在！'}), 404

        # 删除知识库文件夹及其所有内容
        shutil.rmtree(knowledge_path)
        
        # 尝试从向量数据库删除数据（如果存在）
        try:
            if hasattr(current_app, 'vector_db'):
                current_app.vector_db.delete_collection(knowledge_name)
        except Exception as e:
            current_app.logger.error(f"删除向量数据库中的数据失败: {str(e)}")
        
        # 尝试从 Elasticsearch 删除数据（如果存在）
        try:
            if hasattr(current_app, 'es_connector'):
                current_app.es_connector.delete_index(knowledge_name)
        except Exception as e:
            current_app.logger.error(f"删除 Elasticsearch 中的数据失败: {str(e)}")

        return jsonify({'message': f'知识库 "{knowledge_name}" 已成功删除！'}), 200

    except Exception as e:
        return jsonify({'message': f'发生错误：{str(e)}'}), 500