# utils/markdown_export.py (修复后)

"""
Markdown导出工具
"""
import os
from datetime import datetime
# 注意：'from config import config' 已被彻底删除

class MarkdownExporter:
    """导出对话为Markdown格式"""
    
    @staticmethod
    def export_conversation(messages, api_config, prompt_config, filename=None, output_dir="output/conversations"):
        """
        导出对话到Markdown文件。
        现在接收 api_config 和 prompt_config 作为参数。
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.md"
        
        filepath = os.path.join(output_dir, filename)
        
        # 将配置信息传递给生成函数
        content = MarkdownExporter._generate_markdown(messages, api_config, prompt_config)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    @staticmethod
    def _generate_markdown(messages, api_config, prompt_config):
        """
        生成Markdown格式内容。
        使用传入的配置字典，而不是全局config。
        """
        lines = []
        
        lines.append("# DeepSeek 对话记录")
        lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 从传入的字典中获取配置信息
        lines.append("## 配置信息")
        lines.append(f"- 模型: {api_config.get('model_name', 'N/A')}")
        lines.append(f"- 温度: {api_config.get('temperature', 'N/A')}")
        lines.append(f"- 最大令牌: {api_config.get('max_tokens', 'N/A')}")
        
        enabled_prompts = []
        if prompt_config.get("cognitive"): enabled_prompts.append("认知架构")
        if prompt_config.get("meta"): enabled_prompts.append("元提示")
        if prompt_config.get("system"): enabled_prompts.append("系统提示")
        
        lines.append(f"- 启用的提示: {', '.join(enabled_prompts) or '无'}\n")
        
        lines.append("## 对话内容\n")
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            timestamp = msg.get("timestamp")
            
            header = f"### 👤 用户" if role == "user" else f"### 🤖 助手"
            if role == "system":
                header = "### ⚙️ 系统提示"
                lines.append(header)
                lines.append("```")
                lines.append(content)
                lines.append("```\n")
            elif role in ["user", "assistant"]:
                 lines.append(header)
                 if timestamp:
                     lines.append(f"*{timestamp}*\n")
                 lines.append(content + "\n")
        
        return "\n".join(lines)
