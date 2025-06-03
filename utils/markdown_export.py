"""
Markdown导出工具
"""
import os
from datetime import datetime
from config import config

class MarkdownExporter:
    """导出对话为Markdown格式"""
    
    @staticmethod
    def export_conversation(messages, filename=None):
        """导出对话到Markdown文件"""
        # 创建输出目录
        output_dir = config.get("output_dir", "output/conversations")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            template = config.get("markdown_template", "conversation_{timestamp}.md")
            filename = template.format(timestamp=timestamp)
        
        filepath = os.path.join(output_dir, filename)
        
        # 生成Markdown内容
        content = MarkdownExporter._generate_markdown(messages)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    @staticmethod
    def _generate_markdown(messages):
        """生成Markdown格式内容"""
        lines = []
        
        # 添加标题
        lines.append("# DeepSeek 对话记录")
        lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 添加配置信息
        lines.append("## 配置信息")
        lines.append(f"- 模型: {config.get('model_name', 'unknown')}")
        lines.append(f"- 温度: {config.get('temperature', 'unknown')}")
        lines.append(f"- 最大令牌: {config.get('max_tokens', 'unknown')}")
        
        enabled_prompts = []
        if config.get("enable_cognitive"):
            enabled_prompts.append("认知架构")
        if config.get("enable_meta"):
            enabled_prompts.append("元提示")
        if config.get("enable_system"):
            enabled_prompts.append("系统提示")
        if config.get("enable_task"):
            enabled_prompts.append("任务提示")
        
        lines.append(f"- 启用的提示: {', '.join(enabled_prompts)}\n")
        
        # 添加对话内容
        lines.append("## 对话内容\n")
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            timestamp = msg.get("timestamp", "")
            
            if role == "system":
                lines.append("### 系统提示")
                lines.append("```")
                lines.append(content)
                lines.append("```\n")
            elif role == "user":
                lines.append(f"### 👤 用户")
                if timestamp:
                    lines.append(f"*{timestamp}*\n")
                lines.append(content + "\n")
            elif role == "assistant":
                lines.append(f"### 🤖 助手")
                if timestamp:
                    lines.append(f"*{timestamp}*\n")
                lines.append(content + "\n")
        
        return "\n".join(lines)
