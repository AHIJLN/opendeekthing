# prompts/loader.py (重构后)
"""
提示加载器
"""

class PromptLoader:
    """根据传入的配置动态组合提示词"""
    
    def __init__(self, prompt_config: dict, mode_name: str = "custom"):
        """
        初始化加载器
        Args:
            prompt_config: 包含 'cognitive', 'meta', 'system' 键的字典
            mode_name: 当前模式的名称，用于显示
        """
        self.cognitive = prompt_config.get("cognitive", "")
        self.meta = prompt_config.get("meta", "")
        self.system = prompt_config.get("system", "")
        self.mode_name = mode_name.upper()

    def get_combined_prompt(self):
        """获取组合后的完整提示"""
        prompts = []
        if self.cognitive:
            prompts.append(f"[COGNITIVE ARCHITECTURE - {self.mode_name}]\n{self.cognitive}")
        if self.meta:
            prompts.append(f"[META-PROMPT - {self.mode_name}]\n{self.meta}")
        if self.system:
            prompts.append(f"[SYSTEM PROMPT - {self.mode_name}]\n{self.system}")
        
        if prompts:
            return "\n\n".join(prompts)
        
        return "" # 如果没有提示，返回空字符串
