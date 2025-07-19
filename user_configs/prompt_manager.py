# user_configs/prompt_manager.py (新文件)

import os
import json
from datetime import datetime 
from typing import Dict, List

# 从原始项目中导入默认提示
from prompts.programming_prompts import get_programming_prompts
from prompts.strategic_prompts import get_strategic_prompts
from prompts.tutorial_writing_prompts import get_tutorial_writing_prompts

CONFIG_DIR = "user_configs"
os.makedirs(CONFIG_DIR, exist_ok=True)

DEFAULT_PROMPTS = {
    "编程模式": get_programming_prompts(),
    "战略分析模式": get_strategic_prompts(),
    "教程写作模式": get_tutorial_writing_prompts(),
}

def initialize_default_prompts():
    """如果默认模式不存在，则创建它们"""
    for name, content in DEFAULT_PROMPTS.items():
        filepath = os.path.join(CONFIG_DIR, f"{name}.json")
        if not os.path.exists(filepath):
            save_prompt_mode(name, content)

def save_prompt_mode(name: str, config: Dict[str, str]):
    """将提示模式保存为JSON文件"""
    filename = f"{name}.json"
    filepath = os.path.join(CONFIG_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_prompt_mode(name: str) -> Dict[str, str]:
    """从JSON文件加载提示模式"""
    filename = f"{name}.json"
    filepath = os.path.join(CONFIG_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"cognitive": "", "meta": "", "system": ""}

# user_configs/prompt_manager.py (修改 get_available_modes 函数)

def get_available_modes() -> List[str]:
    """获取所有可用的模式名称"""
    # 需要排除的文件
    excluded_files = ['api_config.json', 'prompt_dictionary.json']
    
    modes = []
    for f in os.listdir(CONFIG_DIR):
        if f.endswith(".json") and f not in excluded_files:
            modes.append(f.replace(".json", ""))
    
    return sorted(modes)

def delete_prompt_mode(name: str):
    """删除一个提示模式"""
    filepath = os.path.join(CONFIG_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)


PROMPT_DICT_FILE = os.path.join(CONFIG_DIR, "prompt_dictionary.json")

def get_prompt_dictionary() -> List[Dict]:
    """获取Prompt字典列表"""
    if not os.path.exists(PROMPT_DICT_FILE):
        return []
    try:
        with open(PROMPT_DICT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_prompt_dictionary(prompts: List[Dict]):
    """保存整个Prompt字典"""
    with open(PROMPT_DICT_FILE, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=2, ensure_ascii=False)

def add_prompt_entry(title: str, content: str) -> Dict:
    """添加一个Prompt条目"""
    prompts = get_prompt_dictionary()
    new_prompt = {
        "id": int(datetime.now().timestamp() * 1000),
        "title": title,
        "content": content,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat()
    }
    prompts.append(new_prompt)
    save_prompt_dictionary(prompts)
    return new_prompt

def update_prompt_entry(prompt_id: int, title: str, content: str) -> bool:
    """更新Prompt条目"""
    prompts = get_prompt_dictionary()
    for i, prompt in enumerate(prompts):
        if prompt['id'] == prompt_id:
            prompts[i]['title'] = title
            prompts[i]['content'] = content
            prompts[i]['updated'] = datetime.now().isoformat()
            save_prompt_dictionary(prompts)
            return True
    return False

def delete_prompt_entry(prompt_id: int) -> bool:
    """删除Prompt条目"""
    prompts = get_prompt_dictionary()
    original_len = len(prompts)
    prompts = [p for p in prompts if p['id'] != prompt_id]
    if len(prompts) < original_len:
        save_prompt_dictionary(prompts)
        return True
    return False
