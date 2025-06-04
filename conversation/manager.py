"""
对话管理器 - 支持编程和战略分析两种模式
"""
from api.deepseek_client import DeepSeekClient
from conversation.history import ConversationHistory
from prompts.loader import PromptLoader
from config import config
import logging
from typing import Generator, Optional

logger = logging.getLogger(__name__)

class ConversationManager:
    """管理对话流程和状态"""
    
    def __init__(self, mode="programming"):
        """初始化对话管理器
        
        Args:
            mode: 工作模式 - "programming" 或 "strategic"
        """
        self.client = DeepSeekClient()
        self.history = ConversationHistory()
        self.mode = mode
        self.prompt_loader = None
        self._initialized = False
    
    def initialize(self):
        """初始化系统提示"""
        if self._initialized:
            return
            
        try:
            # 加载提示词
            self.prompt_loader = PromptLoader(self.mode)
            system_prompt = self.prompt_loader.get_combined_prompt()
            
            if system_prompt:
                # 设置系统提示
                self.history.add_message("system", system_prompt)
                logger.info(f"已加载 {self.mode} 模式的系统提示")
                
                # 显示启用的提示信息
                prompt_info = self.prompt_loader.get_prompt_info()
                for info in prompt_info:
                    logger.info(f"  - {info}")
            else:
                logger.warning("未加载任何提示词")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    def chat(self, user_input: str, stream: bool = None) -> str:
        """处理用户输入并返回AI响应
        
        Args:
            user_input: 用户输入的文本
            stream: 是否使用流式响应（None时使用配置默认值）
            
        Returns:
            AI的响应文本
        """
        if not self._initialized:
            self.initialize()
        
        # 决定是否使用流式响应
        use_stream = stream if stream is not None else config.get("stream_response", False)
        
        try:
            # 添加用户消息
            self.history.add_message("user", user_input)
            
            # 获取模型参数
            model_params = config.get_model_params()
            
            if use_stream:
                # 流式响应 - 收集所有片段
                full_response = ""
                for chunk in self.chat_stream(user_input):
                    full_response += chunk
                
                # 添加完整响应到历史
                self.history.add_message("assistant", full_response)
                return full_response
            else:
                # 非流式响应
                response = self.client.chat(
                    messages=self.history.get_messages(),
                    **model_params
                )
                
                # 添加AI响应到历史
                self.history.add_message("assistant", response)
                return response
            
        except Exception as e:
            logger.error(f"对话出错: {e}")
            error_msg = f"抱歉，处理您的请求时出现错误: {str(e)}"
            self.history.add_message("assistant", error_msg)
            return error_msg
    
    def chat_stream(self, user_input: str) -> Generator[str, None, None]:
        """处理用户输入并返回流式AI响应
        
        Args:
            user_input: 用户输入的文本
            
        Yields:
            AI响应的文本片段
        """
        if not self._initialized:
            self.initialize()
        
        try:
            # 添加用户消息到历史
            self.history.add_message("user", user_input)
            
            # 获取模型参数
            model_params = config.get_model_params()
            
            # 收集完整响应用于保存到历史
            full_response = ""
            
            # 生成流式响应
            for chunk in self.client.chat_stream(
                messages=self.history.get_messages(),
                **model_params
            ):
                full_response += chunk
                yield chunk
            
            # 保存完整响应到历史
            self.history.add_message("assistant", full_response)
                
        except Exception as e:
            logger.error(f"流式对话出错: {e}")
            error_msg = f"抱歉，处理您的请求时出现错误: {str(e)}"
            self.history.add_message("assistant", error_msg)
            yield error_msg
    
    def get_mode(self):
        """获取当前模式"""
        return self.mode
    
    def get_mode_description(self):
        """获取当前模式的描述"""
        modes = PromptLoader.get_available_modes()
        return modes.get(self.mode, "未知模式")
    
    def clear_history(self):
        """清空对话历史"""
        self.history.clear()
        self._initialized = False
        logger.info("对话历史已清空")
