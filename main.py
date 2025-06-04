"""
增强版DeepSeek提示工程系统 - 支持编程模式和战略分析模式
"""
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.live import Live
from rich.text import Text
from conversation.manager import ConversationManager
from prompts.loader import PromptLoader
from utils.markdown_export import MarkdownExporter
from config import config
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
except Exception as e:
    print(f"✗ 创建调试目录时出错: {e}")
    debug_dir = "."

class EnhancedInput:
    """增强的输入处理类"""
    
    @staticmethod
    def detect_truncation(text, max_expected=4000):
        """检测输入是否可能被截断"""
        indicators = [
            len(text) > max_expected * 0.9,
            text.endswith('?') and len(text) > 200,
            text.count('。') == 0 and len(text) > 300,
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
                
                if line.strip().upper() == 'END':
                    break
                
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
        """粘贴模式"""
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
        
        filename = os.path.expanduser(filename)
        
        if not filename:
            console.print("[yellow]未提供文件路径[/yellow]")
            return ""
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            console.print(f"[green]✓ 成功读取文件: {filename}[/green]")
            console.print(f"[dim]文件大小: {len(content)} 字符[/dim]")
            
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
        """智能输入"""
        if first_attempt and EnhancedInput.detect_truncation(first_attempt):
            console.print("\n[yellow]⚠️  检测到输入可能被截断[/yellow]")
            console.print("[cyan]已自动切换到多行输入模式[/cyan]")
            return EnhancedInput.multiline_input(first_line=first_attempt)
        
        return first_attempt

def display_mode_selection():
    """显示模式选择界面"""
    console.print("\n" + "="*60)
    console.print("[bold cyan]请选择工作模式:[/bold cyan]\n")
    
    modes = PromptLoader.get_available_modes()
    
    console.print("[bold green]1. 编程模式 (Programming Mode)[/bold green]")
    console.print("   " + modes["programming"])
    console.print("   适用于：代码开发、调试、技术问题解决、架构设计\n")
    
    console.print("[bold yellow]2. 战略分析模式 (Strategic Analysis Mode)[/bold yellow]")
    console.print("   " + modes["strategic"])
    console.print("   适用于：商业分析、战略规划、市场研究、决策支持\n")
    
    console.print("="*60)
    
    while True:
        choice = input("\n请选择模式 (1 或 2): ").strip()
        if choice == "1":
            return "programming"
        elif choice == "2":
            return "strategic"
        else:
            console.print("[red]无效选择，请输入 1 或 2[/red]")

def display_welcome(mode):
    """显示欢迎信息"""
    mode_name = "编程模式" if mode == "programming" else "战略分析模式"
    mode_color = "green" if mode == "programming" else "yellow"
    
    welcome_text = f"""
# 🚀 DeepSeek 增强版提示工程系统

## 当前模式：{mode_name}

您已选择 **{mode_name}**，系统已加载相应的三层提示架构：
- **认知架构层 (Cognitive Architecture)**: 定义思维模式和知识组织
- **元提示层 (Meta-Prompt)**: 优化响应策略和质量标准
- **系统提示层 (System Prompt)**: 具体执行协议和输出规范

## 可用命令：
- `/help` - 显示帮助信息
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
    console.print(Panel(Markdown(welcome_text), title=f"欢迎使用 - {mode_name}", border_style=mode_color))

def display_help(mode):
    """显示帮助信息"""
    mode_name = "编程模式" if mode == "programming" else "战略分析模式"
    
    help_text = f"""
## 当前模式：{mode_name}

### 基本命令：
- `/help` - 显示此帮助信息
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

### 注意事项：
- 选择模式后，在对话过程中无法切换模式
- 如需切换模式，请使用 `/exit` 退出后重新启动程序
    """
    console.print(Panel(Markdown(help_text), title="帮助信息", border_style="cyan"))

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
    """获取用户输入"""
    console.print("\n[bold cyan]您:[/bold cyan]", end=" ")
    sys.stdout.flush()
    
    try:
        if input_mode == "auto":
            first_line = input()
            
            if first_line.startswith('/'):
                return first_line
            
            if first_line.endswith('\\') or len(first_line) > 200:
                console.print("[dim cyan]检测到多行输入标记，进入多行模式...[/dim cyan]")
                return EnhancedInput.multiline_input(first_line=first_line.rstrip('\\'))
            
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
    # 选择工作模式
    selected_mode = display_mode_selection()
    
    # 显示欢迎信息
    display_welcome(selected_mode)
    
    # 初始化管理器
    manager = ConversationManager(mode=selected_mode)
    manager.initialize()
    
    # 对话计数器和输入模式
    conversation_count = 0
    current_input_mode = "auto"
    
    console.print(f"\n[bold green]已进入 {manager.get_mode_description()}[/bold green]")
    console.print("[dim]提示：在对话过程中无法切换模式。如需切换，请退出后重新启动。[/dim]\n")
    
    while True:
        try:
            # 获取用户输入
            user_input = get_enhanced_input(current_input_mode)
            
            # 处理命令
            if user_input.lower() == '/exit':
                console.print("\n[yellow]感谢使用，再见！[/yellow]")
                break
                
            elif user_input.lower() == '/help':
                display_help(selected_mode)
                continue
                
            elif user_input.lower() == '/input':
                new_mode = select_input_mode()
                if new_mode:
                    current_input_mode = new_mode
                    console.print(f"[green]已切换到 {current_input_mode} 输入模式[/green]")
                continue
                
            elif user_input.lower() == '/file':
                user_input = EnhancedInput.file_input()
                if not user_input:
                    continue
                    
            elif user_input.lower() == '/paste':
                user_input = EnhancedInput.paste_mode()
                if not user_input:
                    continue
                    
            elif user_input.lower() == '/save':
                exporter = MarkdownExporter()
                filename = exporter.export_conversation(
                    manager.history.messages,
                    selected_mode
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
                continue
                
            elif user_input.lower() == '/clear':
                manager.clear_history()
                manager.initialize()
                console.print("[yellow]对话历史已清空[/yellow]")
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
            
            mode_indicator = "[green]编程模式[/green]" if selected_mode == "programming" else "[yellow]战略分析模式[/yellow]"
            console.print(f"\n[bold]AI ({mode_indicator}):[/bold]")
            
            # 获取响应
            try:
                # 检查是否启用流式响应
                use_stream = config.get("stream_response", True)  # 默认启用流式响应

                if use_stream:
                    # 流式响应
                    full_response = ""

                    # 使用 Live 实现平滑的实时更新
                    with Live(Text("正在生成响应...", style="dim italic"),
                             console=console,
                             refresh_per_second=10) as live:

                        # 收集响应片段并实时显示
                        for chunk in manager.chat_stream(user_input):
                            full_response += chunk
                            # 实时更新显示的文本（显示最后500个字符作为预览）
                            preview = full_response[-500:] if len(full_response) > 500 else full_response
                            live.update(Text(preview + "▌", style="dim"))

                    # 流式响应完成后，渲染完整的 Markdown
                    if len(full_response) > 2000:
                        console.print(f"[dim](响应长度: {len(full_response)} 字符)[/dim]")

                    # 使用 Markdown 渲染最终响应
                    md = Markdown(full_response)
                    console.print(md)

                else:
                    # 非流式响应（原来的方式）
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
                        selected_mode
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
