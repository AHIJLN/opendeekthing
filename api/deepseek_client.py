"""
DeepSeek API 客户端
"""
from openai import OpenAI
from config import config  # 导入实例而不是类
import logging
import time
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek API 客户端封装"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.api_key,  # 使用小写的属性名
            base_url=config.base_url  # 使用小写的属性名
        )
        self.model = config.model_name  # 使用小写的属性名
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: Optional[float] = None, 
             max_tokens: Optional[int] = None) -> str:
        """发送聊天请求（带重试机制）"""
        for attempt in range(config.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature or config.temperature,
                    max_tokens=max_tokens or config.max_tokens
                )
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"API调用失败 (尝试 {attempt + 1}/{config.max_retries}): {e}")
                
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay * (attempt + 1))  # 递增延迟
                else:
                    logger.error(f"API调用最终失败: {e}")
                    raise
    
    def create_message(self, role: str, content: str) -> Dict[str, str]:
        """创建消息对象"""
        return {"role": role, "content": content}
    
    def validate_api_key(self) -> bool:
        """验证API密钥是否有效"""
        try:
            # 发送一个简单的测试请求
            self.chat([{"role": "user", "content": "Hi"}], max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"API密钥验证失败: {e}")
            return False
