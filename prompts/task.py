"""
任务提示 - 针对特定任务的增强提示
"""

TASK_PROMPTS = {
    "code": """
### Code Assistant Mode
When helping with code:
1. Analyze requirements thoroughly
2. Consider edge cases and error handling
3. Follow best practices and conventions
4. Provide clear explanations
5. Include usage examples when helpful
""",
    
    "analysis": """
### Analysis Mode
When performing analysis:
1. Gather all relevant data points
2. Apply appropriate analytical frameworks
3. Present findings systematically
4. Support conclusions with evidence
5. Highlight key insights and recommendations
""",
    
    "creative": """
### Creative Mode
When generating creative content:
1. Understand the tone and style needed
2. Balance originality with requirements
3. Iterate based on feedback
4. Maintain consistency throughout
5. Add unique perspectives when appropriate
""",
    
    "learning": """
### Learning Assistant Mode
When helping with learning:
1. Start from the learner's current level
2. Break complex concepts into steps
3. Use analogies and examples
4. Check understanding regularly
5. Provide practice opportunities
""",
    
    "default": """
### General Assistant Mode
I'm ready to help with your task. I will:
1. Understand your needs precisely
2. Apply appropriate reasoning
3. Provide clear, useful responses
4. Acknowledge any limitations
5. Focus on practical value
"""
}

def get_task_prompt(task_type="default"):
    """获取任务提示"""
    return TASK_PROMPTS.get(task_type, TASK_PROMPTS["default"])


def get_available_tasks():
    """返回可用的任务类型及其描述"""
    return {
        "code": "代码助手模式 - 专注于编程和技术问题",
        "analysis": "分析助手模式 - 深度分析和问题解决",
        "creative": "创意写作模式 - 创意内容和文学创作",
        "learning": "学习辅导模式 - 教育和知识传授",
        "default": "通用对话模式 - 日常对话和通用问答"
    }

