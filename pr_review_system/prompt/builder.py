from . import system_prompt
from . import user_prompt

class PromptBuilder:

    def build(self, strategy, diff, commit, context=None):

        if strategy == "baseline":
            system = system_prompt.build_baseline_system_prompt()
            user = user_prompt.build_user_prompt(diff=diff, commit=commit)

        elif strategy == "with_readme":
            if not context:
                raise ValueError("with_readme 策略必须提供项目背景")
            system = system_prompt.build_context_system_prompt()
            user = user_prompt.build_user_prompt(diff=diff, commit=commit, context=context)

        else:
            raise ValueError("未知的策略")

        return {
            "system": system,
            "user": user
        }