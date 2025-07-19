# conversation/manager.py (重构后)

from api.deepseek_client import DeepSeekClient
from conversation.history import ConversationHistory
from prompts.loader import PromptLoader
import logging
from typing import Generator, List, Dict

logger = logging.getLogger(__name__)

class ConversationManager:
    """管理对话流程和状态，接收动态配置"""

    def __init__(self, api_config: dict, prompt_config: dict, prompt_mode_name: str):
        self.api_config = api_config
        self.client = DeepSeekClient(
            api_key=api_config['api_key'],
            base_url=api_config['base_url'],
            model_name=api_config['model_name']
        )
        self.history = ConversationHistory()
        self.prompt_loader = PromptLoader(prompt_config, prompt_mode_name)
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return
        system_prompt = self.prompt_loader.get_combined_prompt()
        if system_prompt:
            self.history.add_message("system", system_prompt)
            logger.info(f"已加载 {self.prompt_loader.mode_name} 模式的系统提示")
        self._initialized = True

    def chat_stream(self, user_input: str) -> Generator[str, None, None]:
        if not self._initialized:
            self.initialize()
        
        self.history.add_message("user", user_input)
        
        model_params = {
            "temperature": self.api_config.get("temperature", 1.0),
            "max_tokens": self.api_config.get("max_tokens", 4096),
            "top_p": self.api_config.get("top_p", 0.95),
            # 其他参数可以类似添加
        }

        try:
            full_response = ""
            stream_generator = self.client.chat_stream(
                messages=self.history.get_messages(),
                **model_params
            )
            for chunk in stream_generator:
                full_response += chunk
                yield chunk
            
            self.history.add_message("assistant", full_response)
        except Exception as e:
            error_msg = f"抱歉，处理您的请求时出现错误: {str(e)}"
            logger.error(f"流式对话出错: {e}")
            yield error_msg
            self.history.add_message("assistant", error_msg)

    def get_history(self) -> List[Dict[str, str]]:
        return self.history.get_all_messages()
