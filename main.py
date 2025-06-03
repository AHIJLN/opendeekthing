"""
增强版DeepSeek提示工程系统 - 主程序
支持多种输入模式：普通输入、多行输入、粘贴模式、文件输入
"""
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text
from conversation.manager import ConversationManager
from prompts.task import get_available_tasks
from utils.markdown_export import MarkdownExporter
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建Console时禁用宽度限制
console = Console(width=None, legacy_windows=False)

# 创建调试目录
debug_dir = "debug_logs"
try:
    os.makedirs(debug_dir, exist_ok=True)
    if os.path.exists(debug_dir):
        print(f"✓ 调试目录已创建: {os.path.abspath(debug_dir)}")
        test_file = os.path.join(debug_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✓ 文件写入权限正常")
    else:
        print("✗ 无法创建调试目录")
except Exception as e:
    print(f"✗ 创建调试目录时出错: {e}")
    debug_dir = "."

class EnhancedInput:
    """增强的输入处理类"""
    
    @staticmethod
    def detect_truncation(text, max_expected=4000):
        """检测输入是否可能被截断"""
        # 检测截断的特征
        indicators = [
            len(text) > max_expected * 0.9,  # 接近最大长度
            text.endswith('?') and len(text) > 200,  # 以问号结束且较长
            text.count('。') == 0 and len(text) > 300,  # 没有句号的长文本
            not text.endswith(('.', '。', '!', '！', '?', '？', '"', '"', '）', ')')) and len(text) > 200
        ]
        return any(indicators)
    
    @staticmethod
    def multiline_input(prompt="", first_line=""):
        """多行输入模式"""
        if prompt:
            console.print(prompt)
        
        console.print("[dim cyan]提示: 输入 'END' 单独一行结束输入，或连续两次Enter结束[/dim cyan]")
        
        lines = [first_line] if first_line else []
        empty_count = 0
        
        while True:
            try:
                line = input()
                
                # 检查是否输入END
                if line.strip().upper() == 'END':
                    break
                
                # 检查连续空行
                if not line:
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                
                lines.append(line)
                
            except EOFError:
                break
            except KeyboardInterrupt:
                console.print("\n[yellow]输入已取消[/yellow]")
                return ""
        
        return '\n'.join(lines).strip()
    
    @staticmethod
    def paste_mode():
        """粘贴模式 - 使用sys.stdin读取"""
        console.print("[cyan]粘贴模式已激活[/cyan]")
        console.print("[dim]请粘贴内容，然后按 Ctrl+D (Mac/Linux) 或 Ctrl+Z (Windows) 结束[/dim]")
        
        try:
            content = sys.stdin.read()
            return content.strip()
        except KeyboardInterrupt:
            console.print("\n[yellow]粘贴已取消[/yellow]")
            return ""
        except Exception as e:
            console.print(f"[red]读取错误: {e}[/red]")
            return ""
    
    @staticmethod
    def file_input():
        """从文件读取输入"""
        console.print("[cyan]文件输入模式[/cyan]")
        filename = input("请输入文件路径 (支持拖拽文件): ").strip().strip('"\'')
        
        # 处理路径中的空格和特殊字符
        filename = os.path.expanduser(filename)  # 展开~
        
        if not filename:
            console.print("[yellow]未提供文件路径[/yellow]")
            return ""
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            console.print(f"[green]✓ 成功读取文件: {filename}[/green]")
            console.print(f"[dim]文件大小: {len(content)} 字符[/dim]")
            
            # 显示文件内容预览
            preview_lines = content.split('\n')[:5]
            if len(preview_lines) < len(content.split('\n')):
                preview_lines.append('...')
            
            console.print("\n[dim]文件内容预览:[/dim]")
            for line in preview_lines:
                console.print(f"[dim]{line[:100]}{'...' if len(line) > 100 else ''}[/dim]")
            
            return content
            
        except FileNotFoundError:
            console.print(f"[red]文件未找到: {filename}[/red]")
            return ""
        except PermissionError:
            console.print(f"[red]没有权限读取文件: {filename}[/red]")
            return ""
        except Exception as e:
            console.print(f"[red]读取文件错误: {e}[/red]")
            return ""
    
    @staticmethod
    def smart_input(first_attempt=""):
        """智能输入 - 自动选择最佳输入方式"""
        if first_attempt and EnhancedInput.detect_truncation(first_attempt):
            console.print("\n[yellow]⚠️  检测到输入可能被截断[/yellow]")
            console.print("[cyan]已自动切换到多行输入模式[/cyan]")
            return EnhancedInput.multiline_input(first_line=first_attempt)
        
        return first_attempt

def display_welcome():
    """显示欢迎信息"""
    welcome_text = """
# 🚀 DeepSeek 增强版提示工程系统

这是一个集成了多层次提示工程技术的对话系统，包括：

- **认知架构**: 模拟人类认知过程
- **元提示**: 自我改进和反思能力
- **系统提示**: 深度思考和推理
- **任务提示**: 特定领域优化

## 可用命令：
- `/help` - 显示帮助信息
- `/task` - 切换任务模式
- `/save` - 保存对话记录
- `/clear` - 清空对话历史
- `/input` - 切换输入模式
- `/file` - 从文件读取输入
- `/paste` - 进入粘贴模式
- `/debug` - 测试调试功能
- `/exit` - 退出程序

## 输入模式：
- **普通模式**: 直接输入（默认）
- **多行模式**: 输入END结束
- **粘贴模式**: Ctrl+D结束
- **文件模式**: 从文件读取

开始对话吧！
    """
    console.print(Panel(Markdown(welcome_text), title="欢迎使用", border_style="green"))

def display_tasks():
    """显示可用任务"""
    table = Table(title="可用任务模式")
    table.add_column("编号", style="cyan", width=6)
    table.add_column("任务类型", style="magenta")
    table.add_column("描述", style="green")
    
    tasks_dict = {
        "code": "代码助手模式 - 专注于编程和技术问题",
        "analysis": "分析助手模式 - 深度分析和问题解决",
        "creative": "创意写作模式 - 创意内容和文学创作",
        "learning": "学习辅导模式 - 教育和知识传授",
        "default": "通用对话模式 - 日常对话和通用问答"
    }
    
    tasks = get_available_tasks()
    
    if isinstance(tasks, dict):
        for idx, (task_type, description) in enumerate(tasks.items(), 1):
            table.add_row(str(idx), task_type, description)
    elif isinstance(tasks, list):
        for idx, task_type in enumerate(tasks, 1):
            description = tasks_dict.get(task_type, "任务模式")
            table.add_row(str(idx), task_type, description)
    else:
        for idx, (task_type, description) in enumerate(tasks_dict.items(), 1):
            table.add_row(str(idx), task_type, description)
    
    console.print(table)

def display_help():
    """显示帮助信息"""
    help_text = """
## 命令说明：

### 基本命令：
- `/help` - 显示此帮助信息
- `/task` - 查看并切换任务模式
- `/save` - 保存当前对话到Markdown文件
- `/clear` - 清空对话历史（重新开始）
- `/exit` - 退出程序

### 输入命令：
- `/input` - 选择输入模式
- `/file` - 从文件读取输入
- `/paste` - 进入粘贴模式（适合超长文本）
- `/debug` - 测试调试日志功能

### 输入技巧：
1. **普通输入**: 直接输入文本，适合短内容
2. **多行输入**: 
   - 自动检测：当输入可能被截断时自动切换
   - 手动触发：在行尾加反斜杠\\
   - 结束方式：输入END或双击Enter
3. **粘贴模式**: 使用`/paste`命令，适合从其他地方复制的长文本
4. **文件输入**: 使用`/file`命令，适合超长文本或结构化内容

### 自动功能：
- 输入截断检测：自动识别被截断的输入并切换到多行模式
- 自动保存：每5轮对话自动保存
- 调试日志：超过200字符的输入自动保存到debug_logs目录
    """
    console.print(Panel(Markdown(help_text), title="帮助信息", border_style="yellow"))

def save_debug_input(user_input, timestamp):
    """保存用户输入到调试文件"""
    try:
        os.makedirs(debug_dir, exist_ok=True)
        filename = f"{debug_dir}/input_{timestamp}.txt"
        full_path = os.path.abspath(filename)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"时间: {datetime.now()}\n")
            f.write(f"长度: {len(user_input)} 字符\n")
            f.write(f"内容:\n{user_input}\n")
        
        if os.path.exists(filename):
            console.print(f"[dim green]✓ 调试文件已创建: {full_path}[/dim green]")
        
        return filename
    except Exception as e:
        console.print(f"[red]保存调试文件失败: {e}[/red]")
        return None

def get_enhanced_input(input_mode="auto"):
    """获取用户输入 - 支持多种模式"""
    console.print("\n[bold cyan]您:[/bold cyan]", end=" ")
    sys.stdout.flush()
    
    try:
        if input_mode == "auto":
            # 自动模式：先尝试普通输入，检测截断
            first_line = input()
            
            # 检查命令
            if first_line.startswith('/'):
                return first_line
            
            # 检查是否需要多行输入
            if first_line.endswith('\\') or len(first_line) > 200:
                console.print("[dim cyan]检测到多行输入标记，进入多行模式...[/dim cyan]")
                return EnhancedInput.multiline_input(first_line=first_line.rstrip('\\'))
            
            # 智能检测截断
            return EnhancedInput.smart_input(first_line)
            
        elif input_mode == "multiline":
            return EnhancedInput.multiline_input()
            
        elif input_mode == "paste":
            return EnhancedInput.paste_mode()
            
        elif input_mode == "file":
            return EnhancedInput.file_input()
            
        else:
            return input()
            
    except EOFError:
        return '/exit'
    except KeyboardInterrupt:
        console.print("\n[yellow]输入已取消[/yellow]")
        return ""
    except Exception as e:
        console.print(f"[red]输入错误: {e}[/red]")
        return ""

def select_input_mode():
    """选择输入模式"""
    console.print("\n[cyan]选择输入模式:[/cyan]")
    console.print("1. 自动模式（智能检测，推荐）")
    console.print("2. 多行模式（适合长文本）")
    console.print("3. 粘贴模式（适合复制粘贴）")
    console.print("4. 文件模式（从文件读取）")
    console.print("5. 返回")
    
    choice = input("选择 (1-5): ").strip()
    
    mode_map = {
        "1": "auto",
        "2": "multiline",
        "3": "paste",
        "4": "file",
        "5": None
    }
    
    return mode_map.get(choice, "auto")

def main():
    """主程序入口"""
    display_welcome()
    
    # 初始化管理器
    manager = ConversationManager()
    manager.initialize()
    
    # 对话计数器和输入模式
    conversation_count = 0
    current_input_mode = "auto"
    
    while True:
        try:
            # 获取用户输入
            user_input = get_enhanced_input(current_input_mode)
            
            # 处理命令
            if user_input.lower() == '/exit':
                console.print("\n[yellow]感谢使用，再见！[/yellow]")
                break
                
            elif user_input.lower() == '/help':
                display_help()
                continue
                
            elif user_input.lower() == '/input':
                new_mode = select_input_mode()
                if new_mode:
                    current_input_mode = new_mode
                    console.print(f"[green]已切换到 {current_input_mode} 输入模式[/green]")
                continue
                
            elif user_input.lower() == '/file':
                # 直接进入文件输入模式
                user_input = EnhancedInput.file_input()
                if not user_input:
                    continue
                    
            elif user_input.lower() == '/paste':
                # 直接进入粘贴模式
                user_input = EnhancedInput.paste_mode()
                if not user_input:
                    continue
                    
            elif user_input.lower() == '/task':
                display_tasks()
                console.print("\n[yellow]选择任务模式 (输入编号):[/yellow]", end=" ")
                choice = input()
                
                try:
                    tasks = get_available_tasks()
                    if isinstance(tasks, dict):
                        task_list = list(tasks.keys())
                    elif isinstance(tasks, list):
                        task_list = tasks
                    else:
                        task_list = ["code", "analysis", "creative", "learning", "default"]
                    
                    task_idx = int(choice) - 1
                    if 0 <= task_idx < len(task_list):
                        new_task = task_list[task_idx]
                        manager.switch_task(new_task)
                        console.print(f"[green]已切换到 {new_task} 模式[/green]")
                    else:
                        console.print("[red]无效的选择[/red]")
                except ValueError:
                    console.print("[red]请输入有效的数字[/red]")
                continue
                
            elif user_input.lower() == '/save':
                exporter = MarkdownExporter()
                filename = exporter.export_conversation(
                    manager.history.messages,
                    manager.task_type
                )
                console.print(f"[green]对话已保存到: {filename}[/green]")
                continue
                
            elif user_input.lower() == '/debug':
                test_text = "这是一个测试文本。" * 50
                console.print("[yellow]正在测试调试日志功能...[/yellow]")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_file = save_debug_input(test_text, timestamp)
                
                if debug_file and os.path.exists(debug_file):
                    console.print(f"[green]✓ 测试成功！文件已保存到: {os.path.abspath(debug_file)}[/green]")
                    console.print(f"[green]文件大小: {os.path.getsize(debug_file)} 字节[/green]")
                else:
                    console.print("[red]✗ 测试失败！请检查文件权限。[/red]")
                
                if os.path.exists(debug_dir):
                    files = os.listdir(debug_dir)
                    console.print(f"\n[cyan]debug_logs目录内容 ({len(files)} 个文件):[/cyan]")
                    for f in files[-5:]:
                        console.print(f"  - {f}")
                continue
                
            elif user_input.lower() == '/clear':
                manager.history.clear()
                console.print("[yellow]对话历史已清空[/yellow]")
                manager.initialize()
                conversation_count = 0
                continue
            
            # 如果是空输入，跳过
            if not user_input.strip():
                continue
            
            # 正常对话处理
            conversation_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 处理输入显示
            input_length = len(user_input)
            
            if input_length > 200:
                debug_file = save_debug_input(user_input, timestamp)
                preview = user_input[:100] + "..."
                console.print(f"\n[dim]您: {preview}[/dim]")
                console.print(f"[dim](输入长度: {input_length} 字符，完整内容已保存到: {debug_file})[/dim]")
            else:
                console.print(f"\n[dim]您: {user_input}[/dim]")
            
            console.print("\n[bold green]AI:[/bold green]")
            
            # 获取响应
            try:
                response = manager.chat(user_input)
                
                if len(response) > 2000:
                    console.print(f"[dim](响应长度: {len(response)} 字符)[/dim]")
                
                md = Markdown(response)
                console.print(md)
                
            except Exception as e:
                console.print(f"[red]生成响应时出错: {str(e)}[/red]")
                logging.error(f"Chat error: {e}", exc_info=True)
            
            # 自动保存对话（每5轮）
            if conversation_count % 5 == 0:
                try:
                    exporter = MarkdownExporter()
                    filename = exporter.export_conversation(
                        manager.history.messages,
                        manager.task_type
                    )
                    console.print(f"\n[dim](自动保存: {filename})[/dim]")
                except Exception as e:
                    logging.error(f"Auto-save error: {e}")
            
        except KeyboardInterrupt:
            console.print("\n\n[yellow]检测到中断信号，退出程序...[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]发生错误: {str(e)}[/red]")
            logging.error(f"Error in main loop: {e}", exc_info=True)

if __name__ == "__main__":
    main()
