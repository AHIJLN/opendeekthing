# app.py (修复重复代码版本)

import streamlit as st
import json
import os
from datetime import datetime

# 导入重构后的核心模块
from conversation.manager import ConversationManager
from user_configs import prompt_manager
from user_configs.api_config_manager import APIConfigManager
from utils.markdown_export import MarkdownExporter

# --- 0. 页面基础配置 ---
st.set_page_config(
    page_title="🚀 Deepseek Pro",
    page_icon="🚀",
    layout="wide"
)

# --- 1. 初始化 & 状态管理 ---

def initialize_app():
    """初始化应用状态"""
    if "app_initialized" in st.session_state:
        return

    # 初始化API配置管理器
    api_config_manager = APIConfigManager()
    
    # 步骤1: 确保默认提示模式存在
    prompt_manager.initialize_default_prompts()
    
    # 步骤2: 初始化会话状态
    st.session_state.manager = None
    st.session_state.api_config_manager = api_config_manager
    
    # 加载保存的API配置
    st.session_state.api_config = api_config_manager.load_config()
    
    # 初始化Prompt库相关状态
    st.session_state.prompt_page = 0
    st.session_state.editing_prompt_id = None
    
    # 动态加载可用的提示模式
    available_modes = prompt_manager.get_available_modes()
    st.session_state.available_modes = available_modes
        
    # 设置默认选中的模式
    st.session_state.current_prompt_mode_name = available_modes[0] if available_modes else "新模式"

    # 加载默认模式的配置
    st.session_state.current_prompt_config = prompt_manager.load_prompt_mode(st.session_state.current_prompt_mode_name)

    # 标记为已初始化
    st.session_state.app_initialized = True

# 每次脚本重新运行时都调用初始化函数
initialize_app()

# --- 2. 侧边栏 (控制中心) ---

with st.sidebar:
    st.title("🚀 Deepseek Plus")
    st.caption("一个用于增强Deepseek功能的Prompt工具")

    # API配置
    with st.expander("🔑 通用API配置", expanded=False):
        # API Key输入 - 添加唯一的key
        api_key = st.text_input(
            "API Key", 
            value=st.session_state.api_config.get('api_key', ''), 
            type="password", 
            help="在此输入您的API密钥",
            key="api_key_input"  # 添加唯一key
        )
        st.session_state.api_config['api_key'] = api_key
        
        # Base URL输入 - 添加唯一的key
        st.session_state.api_config['base_url'] = st.text_input(
            "API Base URL", 
            value=st.session_state.api_config['base_url'], 
            help="例如: https://api.deepseek.com",
            key="base_url_input"  # 添加唯一key
        )
        
        # 模型选择
        model_options = ["deepseek-chat", "deepseek-reasoner"]
        current_model = st.session_state.api_config.get('model_name', 'deepseek-chat')
        if current_model not in model_options:
            current_model = model_options[0]
        
        st.session_state.api_config['model_name'] = st.selectbox(
            "模型选择",
            options=model_options,
            index=model_options.index(current_model),
            help="选择使用的模型",
            key="model_select"  # 添加唯一key
        )
        
        # 温度设置
        st.session_state.api_config['temperature'] = st.slider(
            "温度 (Temperature)", 
            0.0, 2.0, 
            st.session_state.api_config.get('temperature', 1.0),
            key="temperature_slider"  # 添加唯一key
        )
        
        # 最大Tokens设置
        st.session_state.api_config['max_tokens'] = st.slider(
            "最大Tokens", 
            256, 8192, 
            st.session_state.api_config.get('max_tokens', 4096),
            key="max_tokens_slider"  # 添加唯一key
        )
        
        # 保存配置按钮
        if st.button("💾 保存API配置", use_container_width=True, key="save_api_config"):
            st.session_state.api_config_manager.save_config(st.session_state.api_config)
            st.toast("API配置已保存!", icon="✅")

    # 提示词模式管理
    with st.expander("🧠 提示词模式管理", expanded=True):
        
        selected_mode = st.selectbox(
            "选择或编辑模式",
            options=st.session_state.available_modes,
            index=st.session_state.available_modes.index(st.session_state.current_prompt_mode_name) if st.session_state.current_prompt_mode_name in st.session_state.available_modes else 0,
            help="选择一个已保存的模式进行编辑或对话。",
            key="mode_select"  # 添加唯一key
        )
        
        if selected_mode != st.session_state.current_prompt_mode_name:
            st.session_state.current_prompt_mode_name = selected_mode
            st.session_state.current_prompt_config = prompt_manager.load_prompt_mode(selected_mode)
            st.rerun()

        st.session_state.current_prompt_config['cognitive'] = st.text_area(
            "认知架构 (Cognitive)", 
            value=st.session_state.current_prompt_config.get('cognitive', ''), 
            height=150,
            key="cognitive_textarea"  # 添加唯一key
        )
        st.session_state.current_prompt_config['meta'] = st.text_area(
            "元提示 (Meta)", 
            value=st.session_state.current_prompt_config.get('meta', ''), 
            height=150,
            key="meta_textarea"  # 添加唯一key
        )
        st.session_state.current_prompt_config['system'] = st.text_area(
            "系统提示 (System)", 
            value=st.session_state.current_prompt_config.get('system', ''), 
            height=150,
            key="system_textarea"  # 添加唯一key
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 更新当前模式", use_container_width=True, key="update_mode"):
                prompt_manager.save_prompt_mode(st.session_state.current_prompt_mode_name, st.session_state.current_prompt_config)
                st.toast(f"模式 '{st.session_state.current_prompt_mode_name}' 已更新!", icon="✅")
        
        with col2:
            new_mode_name = st.text_input(
                "新模式名称...", 
                label_visibility="collapsed", 
                placeholder="输入新模式名称...",
                key="new_mode_name"  # 添加唯一key
            )
            if st.button("✚ 另存为新模式", use_container_width=True, key="save_as_new") and new_mode_name:
                if f"{new_mode_name}.json" in os.listdir("user_configs"):
                    st.warning(f"模式 '{new_mode_name}' 已存在。")
                else:
                    prompt_manager.save_prompt_mode(new_mode_name, st.session_state.current_prompt_config)
                    st.session_state.available_modes = prompt_manager.get_available_modes()
                    st.session_state.current_prompt_mode_name = new_mode_name
                    st.toast(f"新模式 '{new_mode_name}' 已创建!", icon="🎉")
                    st.rerun()

    # 任务提示库管理
    with st.expander("📚 任务提示库管理", expanded=False):
        # 获取Prompt字典
        prompt_dict = prompt_manager.get_prompt_dictionary()
        
        # 新建/编辑Prompt表单
        st.write("### 📝 新建/编辑 Prompt")
        
        # 如果正在编辑，加载编辑的内容
        if st.session_state.editing_prompt_id:
            editing_prompt = next((p for p in prompt_dict if p['id'] == st.session_state.editing_prompt_id), None)
            if editing_prompt:
                default_title = editing_prompt['title']
                default_content = editing_prompt['content']
            else:
                st.session_state.editing_prompt_id = None
                default_title = ""
                default_content = ""
        else:
            default_title = ""
            default_content = ""
        
        prompt_title = st.text_input(
            "标题", 
            value=default_title, 
            placeholder="输入Prompt标题...",
            key="prompt_title_input"  # 添加唯一key
        )
        prompt_content = st.text_area(
            "内容", 
            value=default_content, 
            placeholder="输入Prompt内容...", 
            height=100,
            key="prompt_content_textarea"  # 添加唯一key
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.session_state.editing_prompt_id:
                if st.button("💾 更新", use_container_width=True, key="update_prompt"):
                    if prompt_title and prompt_content:
                        prompt_manager.update_prompt_entry(
                            st.session_state.editing_prompt_id, 
                            prompt_title, 
                            prompt_content
                        )
                        st.session_state.editing_prompt_id = None
                        st.toast("Prompt已更新!", icon="✅")
                        st.rerun()
            else:
                if st.button("➕ 添加", use_container_width=True, key="add_prompt"):
                    if prompt_title and prompt_content:
                        prompt_manager.add_prompt_entry(prompt_title, prompt_content)
                        st.toast("Prompt已添加!", icon="✅")
                        st.rerun()
        
        with col2:
            if st.session_state.editing_prompt_id:
                if st.button("❌ 取消编辑", use_container_width=True, key="cancel_edit"):
                    st.session_state.editing_prompt_id = None
                    st.rerun()
        
        st.divider()
        
        # 显示Prompt列表
        st.write("### 📋 Prompt列表")
        
        # 分页计算
        items_per_page = 10
        total_items = len(prompt_dict)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
        
        # 确保当前页有效
        if st.session_state.prompt_page >= total_pages:
            st.session_state.prompt_page = max(0, total_pages - 1)
        
        # 获取当前页的项目
        start_idx = st.session_state.prompt_page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        current_page_prompts = prompt_dict[start_idx:end_idx]
        
        # 显示当前页的Prompt
        if current_page_prompts:
            for prompt in current_page_prompts:
                with st.container():
                    col1, col2, col3, col4 = st.columns([5, 2, 1, 1])
                    with col1:
                        if st.button(
                            f"💬 {prompt['title']}", 
                            key=f"use_prompt_{prompt['id']}", 
                            use_container_width=True,
                            help="点击使用此Prompt"
                        ):
                            # 将Prompt内容设置为待发送
                            st.session_state.pending_prompt = prompt['content']
                            st.rerun()
                    
                    with col2:
                        st.caption(f"更新: {prompt.get('updated', prompt['created'])[:10]}")
                    
                    with col3:
                        if st.button("✏️", key=f"edit_{prompt['id']}", help="编辑"):
                            st.session_state.editing_prompt_id = prompt['id']
                            st.rerun()
                    
                    with col4:
                        if st.button("🗑️", key=f"delete_{prompt['id']}", help="删除"):
                            prompt_manager.delete_prompt_entry(prompt['id'])
                            st.toast("Prompt已删除!", icon="🗑️")
                            st.rerun()
        else:
            st.info("暂无Prompt，请添加新的Prompt")
        
        # 分页控制
        if total_pages > 1:
            col1, col2, col3 = st.columns([2, 3, 2])
            with col1:
                if st.button("⬅️ 上一页", disabled=st.session_state.prompt_page == 0, key="prev_page"):
                    st.session_state.prompt_page -= 1
                    st.rerun()
            with col2:
                st.write(f"第 {st.session_state.prompt_page + 1} / {total_pages} 页")
            with col3:
                if st.button("下一页 ➡️", disabled=st.session_state.prompt_page >= total_pages - 1, key="next_page"):
                    st.session_state.prompt_page += 1
                    st.rerun()

    # 对话历史与导出
    st.divider()
    st.header("📜 对话管理")
    
    if st.button("🗑️ 开始新对话", use_container_width=True, key="new_conversation"):
        st.session_state.manager = None
        st.rerun()

    if st.session_state.manager and st.session_state.manager.get_history():
        md_content = MarkdownExporter._generate_markdown(
            messages=st.session_state.manager.get_history(),
            api_config=st.session_state.api_config,
            prompt_config=st.session_state.current_prompt_config
        )
        st.download_button(
            label="📥 下载对话 (Markdown)",
            data=md_content,
            file_name=f"conversation_{st.session_state.current_prompt_mode_name}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_conversation"
        )

# --- 3. 主聊天界面 ---

st.title(f"对话模式: {st.session_state.current_prompt_mode_name}")

# 初始化对话管理器实例
if st.session_state.manager is None:
    if not st.session_state.api_config.get("api_key"):
        st.warning("欢迎使用！请在左侧侧边栏的\"通用API配置\"中输入您的API Key以开始对话。")
        st.stop()
    
    st.session_state.manager = ConversationManager(
        api_config=st.session_state.api_config,
        prompt_config=st.session_state.current_prompt_config,
        prompt_mode_name=st.session_state.current_prompt_mode_name
    )
    st.session_state.manager.initialize()

# 显示历史消息
for message in st.session_state.manager.get_history():
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 检查是否有待发送的Prompt
if hasattr(st.session_state, 'pending_prompt') and st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None  # 清除待发送状态
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 获取并显示助手回复
    with st.chat_message("assistant"):
        response_stream = st.session_state.manager.chat_stream(prompt)
        st.write_stream(response_stream)
    
    st.rerun()

# 正常的聊天输入
if prompt := st.chat_input("请输入您的问题..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_stream = st.session_state.manager.chat_stream(prompt)
        st.write_stream(response_stream)

    st.rerun()
