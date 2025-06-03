"""
配置文件 - 支持环境变量和配置文件
"""
import os
import json
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# 加载环境变量
load_dotenv()

class Config:
    """配置管理类"""
    
    # 默认配置值
    DEFAULTS = {
        # API配置
        "api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "base_url": "https://api.deepseek.com",
        "api_version": "v1",
        "model_name": "deepseek-reasoner",
        
        # 模型参数
        "temperature": 1.0,
        "max_tokens": 4000,
        "top_p": 0.95,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop_sequences": None,
        
        # 提示词配置
        "enable_cognitive": True,
        "enable_meta": True,
        "enable_system": True,
        "enable_task": True,
        "default_task_type": "default",
        
        # 对话配置
        "max_history_length": 10,
        "stream_response": False,
        
        # API重试配置
        "max_retries": 3,
        "retry_delay": 1,
        "timeout": 30,
        
        # 输出配置
        "output_dir": "output/conversations",
        "markdown_template": "conversation_{timestamp}.md",
        "auto_save": False,
        "save_interval": 5,  # 每5轮对话自动保存
        
        # 日志配置
        "log_level": "INFO",
        "log_file": None,
        "show_api_calls": False,
        "show_token_usage": False,
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化配置"""
        self._config = self.DEFAULTS.copy()
        
        # 1. 从配置文件加载（如果提供）
        if config_file:
            self._load_from_file(config_file)
        else:
            # 尝试自动查找配置文件
            self._auto_load_config()
        
        # 2. 从环境变量覆盖
        self._load_from_env()
        
        # 3. 构建完整的API URL
        self._build_api_url()
    
    def _auto_load_config(self):
        """自动查找并加载配置文件"""
        config_files = [
            "deepseek.config.json",
            "deepseek.config.yaml",
            "deepseek.config.yml",
            "config.json",
            "config.yaml",
            "config.yml"
        ]
        
        for filename in config_files:
            if Path(filename).exists():
                self._load_from_file(filename)
                print(f"已加载配置文件: {filename}")
                break
    
    def _load_from_file(self, filepath: str):
        """从文件加载配置"""
        path = Path(filepath)
        if not path.exists():
            print(f"配置文件不存在: {filepath}")
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif path.suffix == '.json':
                    data = json.load(f)
                else:
                    print(f"不支持的配置文件格式: {path.suffix}")
                    return
                
                if data:
                    self._config.update(data)
                    
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        env_mappings = {
            # API配置
            "DEEPSEEK_API_KEY": "api_key",
            "DEEPSEEK_BASE_URL": "base_url",
            "DEEPSEEK_API_VERSION": "api_version",
            "DEEPSEEK_MODEL": "model_name",
            
            # 模型参数
            "DEEPSEEK_TEMPERATURE": ("temperature", float),
            "DEEPSEEK_MAX_TOKENS": ("max_tokens", int),
            "DEEPSEEK_TOP_P": ("top_p", float),
            "DEEPSEEK_FREQUENCY_PENALTY": ("frequency_penalty", float),
            "DEEPSEEK_PRESENCE_PENALTY": ("presence_penalty", float),
            
            # 提示词配置
            "DEEPSEEK_ENABLE_COGNITIVE": ("enable_cognitive", self._parse_bool),
            "DEEPSEEK_ENABLE_META": ("enable_meta", self._parse_bool),
            "DEEPSEEK_ENABLE_SYSTEM": ("enable_system", self._parse_bool),
            "DEEPSEEK_ENABLE_TASK": ("enable_task", self._parse_bool),
            "DEEPSEEK_DEFAULT_TASK": "default_task_type",
            
            # 其他配置
            "DEEPSEEK_MAX_HISTORY": ("max_history_length", int),
            "DEEPSEEK_STREAM": ("stream_response", self._parse_bool),
            "DEEPSEEK_TIMEOUT": ("timeout", int),
            "DEEPSEEK_LOG_LEVEL": "log_level",
        }
        
        for env_key, config_info in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                if isinstance(config_info, tuple):
                    config_key, converter = config_info
                    try:
                        self._config[config_key] = converter(env_value)
                    except ValueError:
                        print(f"无法转换环境变量 {env_key}={env_value}")
                else:
                    self._config[config_info] = env_value
    
    def _parse_bool(self, value: str) -> bool:
        """解析布尔值"""
        return value.lower() in ['true', '1', 'yes', 'on']
    
    def _build_api_url(self):
        """构建完整的API URL"""
        base_url = self._config["base_url"].rstrip('/')
        api_version = self._config["api_version"]
        self._config["full_api_url"] = f"{base_url}/{api_version}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self._config[key] = value
        if key in ["base_url", "api_version"]:
            self._build_api_url()
    
    def update(self, config_dict: Dict[str, Any]):
        """批量更新配置"""
        self._config.update(config_dict)
        self._build_api_url()
    
    def get_model_params(self) -> Dict[str, Any]:
        """获取模型参数"""
        return {
            "temperature": self._config["temperature"],
            "max_tokens": self._config["max_tokens"],
            "top_p": self._config["top_p"],
            "frequency_penalty": self._config["frequency_penalty"],
            "presence_penalty": self._config["presence_penalty"],
            "stop": self._config["stop_sequences"],
        }
    
    def save_to_file(self, filepath: str):
        """保存配置到文件"""
        path = Path(filepath)
        
        # 移除敏感信息
        config_to_save = self._config.copy()
        config_to_save["api_key"] = "your-api-key-here"
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                if path.suffix in ['.yaml', '.yml']:
                    yaml.dump(config_to_save, f, default_flow_style=False)
                elif path.suffix == '.json':
                    json.dump(config_to_save, f, indent=2)
                    
            print(f"配置已保存到: {filepath}")
            
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def display(self):
        """显示当前配置（隐藏敏感信息）"""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="当前配置")
        table.add_column("配置项", style="cyan")
        table.add_column("值", style="green")
        
        for key, value in sorted(self._config.items()):
            if key == "api_key":
                display_value = value[:8] + "..." if value != "your-api-key-here" else "未设置"
            else:
                display_value = str(value)
            
            table.add_row(key, display_value)
        
        console.print(table)
    
    # 为了向后兼容，提供属性访问
    def __getattr__(self, name):
        key = name.lower()
        if key in self._config:
            return self._config[key]
        raise AttributeError(f"配置项 '{name}' 不存在")


# 创建全局配置实例
config = Config()
