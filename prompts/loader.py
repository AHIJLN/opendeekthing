"""
提示加载器
"""
from .cognitive import get_cognitive_prompt
from .meta import get_meta_prompt
from .system import get_system_prompt
from .task import get_task_prompt
from config import config

class PromptLoader:
    """提示词加载和组合"""
    
    def __init__(self, task_type="default"):
        self.cognitive = get_cognitive_prompt() if config.enable_cognitive else ""
        self.meta = get_meta_prompt() if config.enable_meta else ""
        self.system = get_system_prompt() if config.enable_system else ""
        self.task = get_task_prompt(task_type) if config.enable_task else ""
        self.task_type = task_type
    
    def get_combined_prompt(self):
        """获取组合后的完整提示"""
        prompts = []
        
        if self.cognitive:
            prompts.append(f"[COGNITIVE ARCHITECTURE]\n{self.cognitive}")
        
        if self.meta:
            prompts.append(f"[META-PROMPT]\n{self.meta}")
            
        if self.system:
            prompts.append(f"[SYSTEM PROMPT]\n{self.system}")
            
        if self.task:
            prompts.append(f"[TASK PROMPT - {self.task_type.upper()}]\n{self.task}")
        
        if prompts:
            combined = "\n\n".join(prompts)
            combined += "\n\nI understand these principles and I'm ready to help."
            return combined
        
        return ""
    
    def get_prompt_info(self):
        """获取启用的提示信息"""
        enabled = []
        if config.enable_cognitive:
            enabled.append("Cognitive Architecture")
        if config.enable_meta:
            enabled.append("Meta-Prompt")
        if config.enable_system:
            enabled.append("System Prompt")
        if config.enable_task:
            enabled.append(f"Task Prompt ({self.task_type})")
        return enabled
