"""
提示加载器 - 支持编程模式和战略分析模式
"""
from .programming_prompts import get_programming_prompts
from .strategic_prompts import get_strategic_prompts
from config import config

class PromptLoader:
    """提示词加载和组合"""
    
    # 可用模式
    MODES = {
        "programming": "编程模式 - 专注于代码开发和技术问题解决",
        "strategic": "战略分析模式 - 专注于商业战略和深度分析"
    }
    
    def __init__(self, mode="programming"):
        """初始化加载器
        
        Args:
            mode: "programming" 或 "strategic"
        """
        if mode not in self.MODES:
            raise ValueError(f"无效的模式: {mode}。可用模式: {list(self.MODES.keys())}")
        
        self.mode = mode
        self._load_prompts()
    
    def _load_prompts(self):
        """根据模式加载相应的提示词"""
        if self.mode == "programming":
            prompts = get_programming_prompts()
        else:  # strategic
            prompts = get_strategic_prompts()
        
        # 根据配置启用相应的提示层
        self.cognitive = prompts["cognitive"] if config.enable_cognitive else ""
        self.meta = prompts["meta"] if config.enable_meta else ""
        self.system = prompts["system"] if config.enable_system else ""
    
    def get_combined_prompt(self):
        """获取组合后的完整提示"""
        prompts = []
        
        if self.cognitive:
            prompts.append(f"[COGNITIVE ARCHITECTURE - {self.mode.upper()}]\n{self.cognitive}")
        
        if self.meta:
            prompts.append(f"[META-PROMPT - {self.mode.upper()}]\n{self.meta}")
            
        if self.system:
            prompts.append(f"[SYSTEM PROMPT - {self.mode.upper()}]\n{self.system}")
        
        if prompts:
            combined = "\n\n".join(prompts)
            combined += f"\n\nI understand these {self.mode} principles and I'm ready to help."
            return combined
        
        return ""
    
    def get_prompt_info(self):
        """获取启用的提示信息"""
        enabled = []
        mode_desc = self.MODES[self.mode]
        
        enabled.append(f"模式: {mode_desc}")
        
        if config.enable_cognitive:
            enabled.append("认知架构层 (Cognitive Architecture)")
        if config.enable_meta:
            enabled.append("元提示层 (Meta-Prompt)")
        if config.enable_system:
            enabled.append("系统提示层 (System Prompt)")
        
        return enabled
    
    @classmethod
    def get_available_modes(cls):
        """获取可用的模式列表"""
        return cls.MODES.copy()
