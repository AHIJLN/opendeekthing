"""
对话历史管理
"""
from datetime import datetime
from typing import List, Dict

class ConversationHistory:
    """管理对话历史记录"""
    
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.start_time = datetime.now()
    
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_messages(self, limit: int = None) -> List[Dict[str, str]]:
        """获取消息历史（用于API调用）"""
        # 获取指定数量的最新消息
        messages = self.messages
        
        if limit and len(messages) > limit:
            # 保留系统消息和最新的对话
            system_messages = [m for m in messages if m["role"] == "system"]
            other_messages = [m for m in messages if m["role"] != "system"]
            
            # 保留最新的limit条对话
            recent_messages = other_messages[-(limit-len(system_messages)):]
            
            messages = system_messages + recent_messages
        
        # 返回API所需格式
        return [{"role": m["role"], "content": m["content"]} for m in messages]
    
    def get_all_messages(self) -> List[Dict[str, str]]:
        """获取所有消息（包含时间戳）"""
        return self.messages
    
    def clear(self):
        """清除历史"""
        self.messages = []
        self.start_time = datetime.now()
