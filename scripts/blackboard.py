"""
Mind-OS 黑板系统 - 交互式对话学习模块
"""
import os
import sys
from datetime import datetime

BLACKBOARD_FILE = "黑板.md"
ARCHIVE_DIR = "对话记录"

def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def init_blackboard():
    """初始化或获取今日黑板"""
    today = get_today_str()
    
    if os.path.exists(BLACKBOARD_FILE):
        with open(BLACKBOARD_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        # 检查是否是今天的黑板
        if f"日期: {today}" in content:
            return content
    
    # 创建新黑板
    header = f"""---
title: Mind-OS 学习黑板
日期: {today}
状态: 进行中
---

# 🖥️ Mind-OS 学习黑板

> 这是你与 AI 的对话空间，所有内容增量记录，学习完毕后可归档。

---

"""
    with open(BLACKBOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(header)
    
    return header

def ai_write(content, section_type="question"):
    """AI 在黑板上写内容"""
    init_blackboard()
    timestamp = get_timestamp()
    
    icons = {
        "question": "❓",
        "teach": "📚",
        "insight": "💡",
        "task": "📝",
        "feedback": "🎯"
    }
    icon = icons.get(section_type, "🤖")
    
    block = f"""
## {icon} AI ({timestamp})

{content}

---
"""
    
    with open(BLACKBOARD_FILE, 'a', encoding='utf-8') as f:
        f.write(block)
    
    print(f"✏️ 已写入黑板 [{section_type}]")
    print(f"📂 请打开 {BLACKBOARD_FILE} 查看")

def user_reply(message):
    """用户回复，记录到黑板"""
    init_blackboard()
    timestamp = get_timestamp()
    
    block = f"""
## 👤 用户 ({timestamp})

> {message}

---
"""
    
    with open(BLACKBOARD_FILE, 'a', encoding='utf-8') as f:
        f.write(block)
    
    print(f"✅ 回复已记录")

def archive_blackboard(summary=None):
    """归档黑板内容到对话记录，并同步到记忆系统"""
    if not os.path.exists(BLACKBOARD_FILE):
        print("⚠️ 黑板为空，无需归档")
        return
    
    with open(BLACKBOARD_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    today = get_today_str()
    timestamp = get_timestamp()
    
    # 创建归档目录
    month_dir = os.path.join(ARCHIVE_DIR, datetime.now().strftime("%Y-%m"))
    os.makedirs(month_dir, exist_ok=True)
    
    # 生成归档文件名
    archive_name = f"对话_{today}_{datetime.now().strftime('%H%M')}.md"
    archive_path = os.path.join(month_dir, archive_name)
    
    # 添加归档头部和总结
    archive_content = content.replace("状态: 进行中", "状态: 已归档")
    
    if summary:
        archive_content += f"""
## 📋 学习总结 ({timestamp})

{summary}

---
"""
    
    # 写入归档
    with open(archive_path, 'w', encoding='utf-8') as f:
        f.write(archive_content)
    
    print(f"📦 已归档到: {archive_path}")
    
    # 同步到 flomo
    try:
        from scripts.flomo_sync import sync_learning
        if summary:
            sync_learning("Mind-OS学习", summary)
            print("📤 已同步到 flomo")
    except Exception as e:
        print(f"⚠️ flomo 同步跳过: {e}")
    
    # 同步到向量记忆
    try:
        from scripts.memory_engine import sync_memory
        print("🧠 正在同步到记忆系统...")
        sync_memory()
    except Exception as e:
        print(f"⚠️ 记忆同步跳过: {e}")
    
    # 清空黑板（保留模板）
    clear_blackboard()
    
    return archive_path

def clear_blackboard():
    """清空黑板，准备新对话"""
    if os.path.exists(BLACKBOARD_FILE):
        os.remove(BLACKBOARD_FILE)
    print("🧹 黑板已清空，准备新的学习")

def show_blackboard():
    """显示当前黑板内容"""
    if not os.path.exists(BLACKBOARD_FILE):
        print("📭 黑板为空")
        return
    
    with open(BLACKBOARD_FILE, 'r', encoding='utf-8') as f:
        print(f.read())

def start_session(topic=None):
    """开始一个新的学习会话"""
    init_blackboard()
    timestamp = get_timestamp()
    
    welcome = f"""
## 🚀 学习会话开始 ({timestamp})

"""
    if topic:
        welcome += f"**今日主题**: {topic}\n\n"
    
    welcome += """准备好了吗？让我们开始探索吧！

---
"""
    
    with open(BLACKBOARD_FILE, 'a', encoding='utf-8') as f:
        f.write(welcome)
    
    print(f"🎯 学习会话已开始")
    print(f"📂 黑板文件: {BLACKBOARD_FILE}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python blackboard.py start [主题]  - 开始学习会话")
        print("  python blackboard.py write <内容>  - AI写入黑板")
        print("  python blackboard.py reply <内容>  - 用户回复")
        print("  python blackboard.py show          - 显示黑板")
        print("  python blackboard.py archive [总结] - 归档并记入记忆")
        print("  python blackboard.py clear         - 清空黑板")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "start":
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        start_session(topic)
    elif cmd == "write":
        content = " ".join(sys.argv[2:])
        ai_write(content)
    elif cmd == "reply":
        message = " ".join(sys.argv[2:])
        user_reply(message)
    elif cmd == "show":
        show_blackboard()
    elif cmd == "archive":
        summary = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        archive_blackboard(summary)
    elif cmd == "clear":
        clear_blackboard()
    else:
        print(f"未知命令: {cmd}")
