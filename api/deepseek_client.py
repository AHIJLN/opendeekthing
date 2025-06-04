"""
DeepSeek API 客户端
"""
from openai import OpenAI
from config import config
import logging
import time
from typing import List, Dict, Optional, Any, Generator

logger = logging.getLogger(__name__)

class DeepSeekClient:
    """DeepSeek API 客户端封装"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        self.model = config.model_name
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: Optional[float] = None, 
             max_tokens: Optional[int] = None,
             top_p: Optional[float] = None,
             frequency_penalty: Optional[float] = None,
             presence_penalty: Optional[float] = None,
             stop: Optional[List[str]] = None,
             stream: Optional[bool] = None,
             **kwargs) -> str:
        """发送聊天请求（带重试机制）- 非流式版本
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大令牌数
            top_p: 核采样参数
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            stop: 停止序列
            stream: 是否使用流式响应
            **kwargs: 其他参数
            
        Returns:
            str: AI的响应内容
        """
        # 如果明确指定stream=True，使用流式版本
        if stream is True:
            # 收集流式响应的所有内容
            full_response = ""
            for chunk in self.chat_stream(messages, temperature, max_tokens, 
                                        top_p, frequency_penalty, presence_penalty, 
                                        stop, **kwargs):
                full_response += chunk
            return full_response
        
        # 构建请求参数
        params = self._build_params(messages, temperature, max_tokens, 
                                   top_p, frequency_penalty, presence_penalty, 
                                   stop, stream=False)
        
        # 重试机制
        for attempt in range(config.max_retries):
            try:
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"API调用失败 (尝试 {attempt + 1}/{config.max_retries}): {e}")
                
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay * (attempt + 1))
                else:
                    logger.error(f"API调用最终失败: {e}")
                    raise
    
    def chat_stream(self, messages: List[Dict[str, str]], 
                   temperature: Optional[float] = None, 
                   max_tokens: Optional[int] = None,
                   top_p: Optional[float] = None,
                   frequency_penalty: Optional[float] = None,
                   presence_penalty: Optional[float] = None,
                   stop: Optional[List[str]] = None,
                   **kwargs) -> Generator[str, None, None]:
        """发送聊天请求（流式版本）
        
        Args:
            同chat方法
            
        Yields:
            str: 响应内容片段
        """
        # 构建请求参数
        params = self._build_params(messages, temperature, max_tokens, 
                                   top_p, frequency_penalty, presence_penalty, 
                                   stop, stream=True)
        
        # 重试机制
        for attempt in range(config.max_retries):
            try:
                response = self.client.chat.completions.create(**params)
                
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                
                return  # 成功完成，退出重试循环
                
            except Exception as e:
                logger.warning(f"流式API调用失败 (尝试 {attempt + 1}/{config.max_retries}): {e}")
                
                if attempt < config.max_retries - 1:
                    time.sleep(config.retry_delay * (attempt + 1))
                else:
                    logger.error(f"流式API调用最终失败: {e}")
                    raise
    
    def _build_params(self, messages: List[Dict[str, str]], 
                     temperature: Optional[float] = None, 
                     max_tokens: Optional[int] = None,
                     top_p: Optional[float] = None,
                     frequency_penalty: Optional[float] = None,
                     presence_penalty: Optional[float] = None,
                     stop: Optional[List[str]] = None,
                     stream: bool = False) -> Dict[str, Any]:
        """构建API请求参数"""
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or config.temperature,
            "max_tokens": max_tokens or config.max_tokens,
            "stream": stream
        }
        
        # 只添加非None的可选参数
        if top_p is not None:
            params["top_p"] = top_p
        elif hasattr(config, 'top_p'):
            params["top_p"] = config.top_p
            
        if frequency_penalty is not None:
            params["frequency_penalty"] = frequency_penalty
        elif hasattr(config, 'frequency_penalty'):
            params["frequency_penalty"] = config.frequency_penalty
            
        if presence_penalty is not None:
            params["presence_penalty"] = presence_penalty
        elif hasattr(config, 'presence_penalty'):
            params["presence_penalty"] = config.presence_penalty
            
        if stop is not None:
            params["stop"] = stop
        elif hasattr(config, 'stop_sequences') and config.stop_sequences:
            params["stop"] = config.stop_sequences
        
        return params
    
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
