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

def build_match_base_user_prompt(people_comments, ai_review):

    return f"""以下是同一个 Pull Request 的人类 Review 与 AI 生成的 Review。

请从“整体语义覆盖”的角度进行评估。

【人类 Review（Ground Truth）】
{people_comments}

【AI 生成的 Review】
{ai_review}

请分析 AI Review 覆盖了哪些问题，遗漏了哪些问题，并给出覆盖程度评分。
"""