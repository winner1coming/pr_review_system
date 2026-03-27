def build_user_prompt(diff, commit, context=None):
    if context == None:
        return f'''以下是项目的代码变更，请对以下代码进行代码审查：
        提交信息：
        {commit}，
        代码变更（Diff）:
        {diff}
        '''
    else:
        return f'''以下是项目的代码变更，请结合项目背景对以下代码进行代码审查：
        项目背景：
        {context}，
        提交信息：
        {commit},
        代码变更（Diff）:
        {diff}
        '''

def build_match_base_user_prompt(people_comment, ai_review):
    return f'''以下分别是人类review提出的问题和AI生成的审查意见，请判断AI生成的审查意见，是否覆盖了人类review提出的问题。
    【人类Review（Ground Truth）】
    {people_comment}
    【AI生成的Review】
    {ai_review}'''