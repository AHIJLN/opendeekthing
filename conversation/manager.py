"""
对话管理器
"""
from typing import List, Dict
from api.deepseek_client import DeepSeekClient
from prompts.loader import PromptLoader
from prompts.task import get_available_tasks
from .history import ConversationHistory
from config import config
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    """管理对话流程"""
    
    def __init__(self, task_type: str = None):
        self.client = DeepSeekClient()
        self.task_type = task_type or config.default_task_type
        self.prompt_loader = PromptLoader(self.task_type)
        self.history = ConversationHistory()
        self.initialized = False
    
    def initialize(self):
        """初始化对话，加载所有提示"""
        if not self.initialized:
            # 验证API密钥
            if not self.client.validate_api_key():
                raise ValueError("无效的API密钥，请检查配置")
            
            # 获取组合提示
            combined_prompt = self.prompt_loader.get_combined_prompt()
            
            if combined_prompt:
                # 添加系统消息
                self.history.add_message("system", combined_prompt)
                logger.info(f"已加载提示: {', '.join(self.prompt_loader.get_prompt_info())}")
            
            self.initialized = True
    
    def switch_task(self, task_type: str):
        """切换任务类型"""
        if task_type not in get_available_tasks():
            raise ValueError(f"未知的任务类型: {task_type}")
        
        self.task_type = task_type
        self.prompt_loader = PromptLoader(task_type)
        self.clear_history()
        logger.info(f"已切换到任务类型: {task_type}")
    
    def chat(self, user_input: str) -> str:
        """处理用户输入并返回回复"""
        # 确保已初始化
        self.initialize()
        
        # 添加用户消息到历史
        self.history.add_message("user", user_input)
        
        # 获取对话历史（限制长度）
        messages = self.history.get_messages(config.max_history_length)
        
        # 调用API
        try:
            response = self.client.chat(messages)
            
            # 添加助手回复到历史
            self.history.add_message("assistant", response)
            
            return response
        
        except Exception as e:
            logger.error(f"对话处理失败: {e}")
            # 移除失败的用户消息
            self.history.messages.pop()
            return f"抱歉，处理您的请求时出现错误: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取完整对话历史"""
        return self.history.get_all_messages()
    
    def clear_history(self):
        """清除对话历史（保留系统提示）"""
        self.history.clear()
        self.initialized = False
        self.initialize()  # 重新初始化以加载系统提示
