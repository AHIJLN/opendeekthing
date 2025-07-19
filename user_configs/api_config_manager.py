# user_configs/api_config_manager.py
import json
import os
from typing import Dict

class APIConfigManager:
    """API配置管理器"""
    
    CONFIG_FILE = "user_configs/api_config.json"
    
    def __init__(self):
        os.makedirs("user_configs", exist_ok=True)
    
    def save_config(self, config: Dict):
        """保存配置到文件"""
        # 不保存空的API key
        save_config = config.copy()
        if not save_config.get('api_key'):
            save_config.pop('api_key', None)
            
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_config, f, indent=2, ensure_ascii=False)
    
    def load_config(self) -> Dict:
        """从文件加载配置"""
        default_config = {
            "api_key": "",
            "base_url": "https://api.deepseek.com",
            "model_name": "deepseek-reasoner",
            "temperature": 1.0,
            "max_tokens": 4096,
            "top_p": 0.95
        }
        
        if not os.path.exists(self.CONFIG_FILE):
            return default_config
        
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            # 合并保存的配置和默认配置
            default_config.update(saved_config)
            return default_config
        except:
            return default_config
