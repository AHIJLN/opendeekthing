# 入门使用教程

## 🚀 项目介绍

DeepSeek 增强版提示工程系统是一个集成了先进提示工程技术的智能对话系统，支持两种专业模式：

- **编程模式**：专注于代码开发、调试、技术问题解决和架构设计
- **战略分析模式**：专注于商业分析、战略规划、市场研究和决策支持

系统采用四层提示架构，该系统采用三层提示架构（认知架构层、元提示层、系统提示层），确保高质量的响应输出。

```
┌─────────────────────────────────────┐
│      认知架构 (Cognitive)           │
│  定义AI的基本思维方式和推理框架      │
├─────────────────────────────────────┤
│       元提示 (Meta-Prompt)          │
│  定义处理流程、质量标准和执行策略    │
├─────────────────────────────────────┤
│      系统提示 (System)              │
│  Claude风格的深度思考链机制         │
├─────────────────────────────────────┤
│      任务提示 (Task)                │
│  针对特定任务的优化指令             │
└─────────────────────────────────────┘
```


# Deepseek Plus

🚀 支持多种提示词模式管理、API 配置持久化和 Prompt 库功能。专为提示工程设计，让您能够高效地与大语言模型进行交互。

## ✨ 主要功能

### 1. **多模型支持**
- 支持 DeepSeek API
- 可扩展支持其他 OpenAI 兼容的 API

### 2. **API 配置管理**
- API 密钥安全存储
- 配置持久化（自动保存和加载）
- 支持自定义 API 端点
- 温度、最大 Tokens 等参数调节

### 3. **提示词模式管理**
- 预设三种专业模式：
  - 📝 **编程模式**：专业的代码助手，具备深度编程认知架构
  - 📊 **战略分析模式**：世界级战略顾问，提供 Fortune 500 级别的分析
  - 📚 **教程写作模式**：将复杂内容转化为清晰教程的专家
- 支持创建和保存自定义模式
- 三层提示词架构（认知架构、元提示、系统提示）

### 4. **Prompt 库管理**
- 保存常用 Prompt 模板
- 分页浏览（每页 10 条）
- 一键使用：点击即可发送到对话
- 支持编辑和删除

### 5. **对话管理**
- 流式响应显示
- 对话历史保存
- 导出为 Markdown 格式
- 一键开始新对话

## 🛠️ 安装指南

### 环境要求
- Python 3.8+
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/AHIJLN/opendeekthing.git
cd opendeekthing
```

2. **创建虚拟环境**（推荐）
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行应用**
```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`



## 📖 使用指南

### 1. 初次使用

1. **配置 API**
   - 在左侧边栏展开"🔑 通用API配置"
   - 输入您的 DeepSeek API Key
   - 选择模型（deepseek-chat 或 deepseek-reasoner）
   - 点击"💾 保存API配置"
<img width="1432" height="748" alt="image" src="https://github.com/user-attachments/assets/539a9d1e-1c06-4e16-90fb-ebffe7fce22b" />


2. **选择提示词模式**
   - 在"🧠 提示词模式管理"中选择预设模式
   - 或创建自定义模式

3. **开始对话**
   - 在主界面输入框中输入问题
   - 按 Enter 发送

### 2. 任务提示库使用

1. **添加 Prompt**
   - 展开"📚 任务提示库管理"
   - 在标题和内容框中输入
   - 点击"➕ 添加"

2. **使用 Prompt**
   - 浏览 Prompt 列表
   - 点击"💬 [Prompt标题]"直接使用

3. **管理 Prompt**
   - 点击"✏️"编辑
   - 点击"🗑️"删除

### 3. 提示词模式详解

每个模式包含三层架构：

- **认知架构（Cognitive）**：定义 AI 的思维框架和知识组织方式
- **元提示（Meta）**：指导 AI 如何优化响应和适应不同场景
- **系统提示（System）**：定义 AI 的身份、能力和输出规范

### 4. 导出对话

- 点击"📥 下载对话 (Markdown)"
- 自动生成包含配置信息和完整对话的 Markdown 文件


## ⚙️ 配置说明

### API 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| API Key | DeepSeek API 密钥 | 无 |
| Base URL | API 端点地址 | https://api.deepseek.com |
| 模型 | 选择使用的模型 | deepseek-chat |
| 温度 | 控制输出的随机性（0-2） | 1.0 |
| 最大 Tokens | 单次回复的最大长度 | 4096 |

### 自定义提示词模式

创建新模式时，建议参考预设模式的结构：

```json
{
  "cognitive": "定义AI的认知架构...",
  "meta": "定义元层面的优化策略...",
  "system": "定义系统级别的行为规范..."
}
```

## 🔒 安全说明

- API 密钥仅保存在本地 `user_configs/api_config.json`
- 建议将 `user_configs/` 添加到 `.gitignore`
- 不要分享包含 API 密钥的配置文件

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 添加新的 API 支持

1. 在 `api/` 目录创建新的客户端类
2. 实现与 `DeepSeekClient` 相同的接口
3. 在 `app.py` 中添加模型选项

### 添加新的预设模式

1. 在 `prompts/` 目录创建新的提示词文件
2. 定义三层提示词结构
3. 在 `prompt_manager.py` 的 `DEFAULT_PROMPTS` 中注册

## 📝 MIT 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。
MIT License
Copyright (c) 2024 opendeekthing
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🙏 致谢

- 基于 Streamlit 构建
- 使用 OpenAI Python 客户端库
- 灵感来自于先进的提示工程实践

---

如有问题或建议，欢迎提交 Issue 或联系作者。

祝您使用愉快！🎉
