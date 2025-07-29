def build_prompt(prompt_template, **kwargs):
    '''将 prompt 模板和参数进行填充'''
    inputs = {}
    for k, v in kwargs.items():
        if isinstance(v, list) and all(isinstance(i, str) for i in v):
            val = '\n\n'.join(v)
        else:
            val = v
        inputs[k] = val
    return prompt_template.format(**inputs)

prompt_template = """
你是一个莆仙话问答助理。
你的任务是根据下述给定的已知信息，用莆仙话或普通话回答用户的问题。

已知信息:
{context}

用户问题:
{query}
"""

general_prompt_template = """
你是一个智能问答助手。
你的任务是根据下述给定的信息，准确、简洁地回答用户的问题。

已知信息:
{context}

用户问题:
{query}

请基于已知信息生成一个清晰且有帮助的回答。如果已知信息中没有相关内容，请直接说明。
"""