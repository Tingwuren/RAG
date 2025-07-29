from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import re

def extract_text_from_pdf(filename, page_numbers=None, min_paragraph_length=20, use_punctuation_split=True):
    '''
    从 PDF 文件中提取中文自然段文本

    参数说明：
    - filename: PDF 文件路径
    - page_numbers: 指定页码（None 表示全部页）
    - min_paragraph_length: 最小段落长度，防止误切碎片
    - use_punctuation_split: 是否启用中文标点断段识别
    '''
    paragraphs = []
    buffer = ''
    full_text = ''

    if not filename.lower().endswith('.pdf'):
        raise ValueError('文件格式必须是 PDF')

    # Step 1: 提取所有页文本合并为 raw 文本
    for i, page_layout in enumerate(extract_pages(filename)):
        if page_numbers is not None and i not in page_numbers:
            continue
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                full_text += element.get_text()

    # Step 2: 文本行预处理
    lines = full_text.splitlines()
    for line in lines:
        line = line.strip()
        # 忽略纯页码或空白行
        if not line or re.fullmatch(r'\d+', line):
            continue

        # 判断是否为段落起始：缩进两字符以上，或上一句结尾为句号
        if use_punctuation_split and re.match(r'^[　\s]{2,}[^　\s]', line):
            if buffer.strip():
                paragraphs.append(buffer.strip())
                buffer = ''
            buffer = line.strip()
        elif use_punctuation_split and re.search(r'[。！？]”?$|[。！？]$', buffer):
            paragraphs.append(buffer.strip())
            buffer = line.strip()
        else:
            # 合并相邻行
            if buffer:
                buffer += line
            else:
                buffer = line

    # 追加最后一个段落
    if buffer and len(buffer.strip()) >= min_paragraph_length:
        paragraphs.append(buffer.strip())

    return paragraphs

def process_word_table(file_path="knowledge/defualt/简明词汇.md"):
    """
    将表格文件切分为 RAG 的 documents 格式。
    每个词生成两条 vector_data：一个是释义关键词，一个是汉字关键词。
    :param file_path: 表格文件路径
    :return: vector_data, documents（数量为原始行数的两倍）
    """
    documents = []
    vector_data = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 跳过表头和分隔符行
    for line in lines[2:]:  # 从第三行开始处理
        columns = line.strip().split("|")
        if len(columns) < 5:
            continue  # 跳过无效行（注意这里判断 len(columns) >= 5）

        word = columns[1].strip()
        pinyin = columns[2].strip()
        ipa = columns[3].strip()
        definition = columns[4].strip()

        # 构造统一文档内容
        document = f"汉字：{word}；拼音：{pinyin}；音标：{ipa}；释义：{definition}"

        # 添加两个向量查询项
        vector_data.append(f"{word} 字义")        # 用于“某字是什么意思”类问题
        documents.append(document)

        vector_data.append(definition)            # 用于“XX是什么意思”类问题
        documents.append(document)

    return vector_data, documents

from opencc import OpenCC

def process_rhyme_table(file_path="knowledge/defualt/莆仙語韻母對照表.md"):
    cc = OpenCC('t2s')  # t2s: 繁体转简体

    documents = []
    vector_data = []
    region_names = [
        "莆田", "江口", "南日", "华亭", "常泰", "新县", "笏石", "平海",
        "湄洲", "东庄", "东海", "仙游", "游洋", "枫亭", "园庄", "凤山"
    ]

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header = lines[1].strip().split("|")
    data = [line.strip().split("|") for line in lines[2:]]

    for col_idx in range(len(header)):
        last_value = None
        for row in data:
            if col_idx < len(row):
                if row[col_idx].strip():
                    last_value = row[col_idx].strip()
                else:
                    row[col_idx] = last_value if last_value else ""

    for row in data:
        if len(row) < 3:
            row += [""] * (3 - len(row))

        rhyme_category = row[1].strip()
        example_words = cc.convert(row[2].strip())  # <-- 转为简体
        locations = row[3:3 + len(region_names)]

        if rhyme_category == "古韻攝" and example_words == "例字（白、文）":
            continue
                # 构造每个汉字的独立 vector_data（适配RAG）
        for i, location in enumerate(locations):
            region_name = region_names[i]
            clean_location = location.replace("<br>", " ").strip()

            for char in example_words:
                if not char.strip():
                    continue  # 跳过空格
                # 构造检索关键词（简洁向量查询字段）
                vector_entry = f"{char} {region_name}"

                # 构造完整回答文本（供 RAG 使用）
                doc_text = (
                    f"“{char}”字在{region_name}的莆仙话韵母为："
                    f"{clean_location if clean_location else '无数据'} ，该字的完整发音为声母 + 韵母"
                )

                vector_data.append(vector_entry)
                documents.append(doc_text)

    return vector_data, documents

def build_vector_to_doc_map(vector_data, documents):
    """
    构造 vector_data 到 documents 的映射字典
    :param vector_data: 向量查询关键词列表
    :param documents: 完整文档内容列表
    :return: 映射字典 {vector_data: document}
    """
    return {vec: doc for vec, doc in zip(vector_data, documents)}