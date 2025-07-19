# api/deepseek_client.py (重构后)

"""
DeepSeek API 客户端
"""
from openai import OpenAI
import logging
import time
from typing import List, Dict, Optional, Any, Generator

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek API 客户端封装"""

    def __init__(self, api_key: str, base_url: str, model_name: str, max_retries: int = 3, retry_delay: int = 1):
        """
        初始化客户端，接收所有必要的配置。
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def chat(self, messages: List[Dict[str, str]], stream: bool = False, **kwargs) -> str:
        """
        非流式聊天请求。
        kwargs: temperature, max_tokens, top_p, 等模型参数
        """
        params = self._build_params(messages, stream=False, **kwargs)

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"API调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"API调用最终失败: {e}")
                    raise

    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """
        流式聊天请求。
        kwargs: temperature, max_tokens, top_p, 等模型参数
        """
        params = self._build_params(messages, stream=True, **kwargs)

        for attempt in range(self.max_retries):
            try:
                response_stream = self.client.chat.completions.create(**params)
                for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return # 成功完成，退出重试循环
            except Exception as e:
                logger.warning(f"流式API调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"流式API调用最终失败: {e}")
                    raise

    def _build_params(self, messages: List[Dict[str, str]], stream: bool, **kwargs) -> Dict[str, Any]:
        """
        构建API请求参数。优先使用kwargs传入的参数。
        """
        params = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        # 合并来自kwargs的动态参数
        params.update(kwargs)
        return params
