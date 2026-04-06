output_sample = '''
[
  {
    "type": "Bug | Security | Readability | Performance | Design | Style",
    "conclusion": "总结代码变更的目的（<=50字）",
    "description": "详细描述问题及影响",
    "evidence": "引用相关代码片段",
    "advice": "给出优化建议",
    "confidence": 0~1,
    "relevance": 0~1,
    "severity": "Low | Medium | High"
  }
]

【字段说明】
- confidence：你对该问题“真实存在”的置信度（基于代码+上下文）
- relevance：该问题与“项目背景信息”的相关程度（是否利用了提供的背景信息）
'''