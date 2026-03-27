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
