import sys
import argparse
import pandas as pd
import os
import re
from datetime import datetime
# Imports moved to lazy loading inside main()

CONFIG_FILE = "个人配置.md"
USER_MANUAL_FILE = "核心记忆/用户说明书.md"

def check_user_profile_exists():
    """检查用户是否已填写个人信息"""
    if not os.path.exists(CONFIG_FILE):
        return False
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查用户名是否还是默认的 [待填写]
    if "[待填写]" in content or "用户名**: \n" in content:
        return False
    
    return True

def collect_user_info():
    """首次使用时收集用户信息"""
    print("\n" + "="*50)
    print("🧠 欢迎使用 Mind-OS - 你的心智操作系统")
    print("="*50)
    print("\n📋 检测到这是您首次使用，需要收集一些基本信息。")
    print("💡 这些信息仅存储在本地，用于为您提供更个性化的体验。\n")
    
    # 收集基本信息
    username = input("👤 请输入您的昵称/用户名: ").strip()
    if not username:
        username = "用户"
    
    print("\n🎯 您的主要成长目标是什么？")
    print("   (例如: 提升认知能力、建立知识体系、自我觉察等)")
    goal = input("   > ").strip()
    if not goal:
        goal = "通过对话认识自我，发现盲区，持续学习成长"
    
    print("\n📚 您主要关注哪些领域？(可多选，用逗号分隔)")
    print("   1.技术 2.商业 3.人文 4.艺术 5.心理 6.其他")
    domains_input = input("   > ").strip()
    
    domains = []
    domain_map = {"1": "技术领域", "2": "商业领域", "3": "人文领域", 
                  "4": "艺术领域", "5": "心理领域", "6": "其他"}
    for d in domains_input.replace("，", ",").split(","):
        d = d.strip()
        if d in domain_map:
            domains.append(domain_map[d])
        elif d:
            domains.append(d)
    
    print("\n💪 您认为自己的优势是什么？")
    strengths = input("   > ").strip()
    
    print("\n🎭 您希望AI在什么情况下如何帮助您？")
    print("   (例如: 迷茫时给方向、焦虑时安抚、学习时督促)")
    help_style = input("   > ").strip()
    
    # 更新个人配置文件
    update_config_file(username, goal, domains)
    
    # 更新用户说明书
    update_user_manual(strengths, help_style)
    
    print("\n" + "="*50)
    print(f"✅ 配置完成！欢迎你，{username}！")
    print("🚀 Mind-OS 已准备就绪，开始你的心智成长之旅吧！")
    print("="*50 + "\n")
    
    return True

def update_config_file(username, goal, domains):
    """更新个人配置文件"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    domain_checklist = ""
    all_domains = ["技术领域", "商业领域", "人文领域", "艺术领域", "心理领域"]
    for d in all_domains:
        if d in domains:
            domain_checklist += f"- [x] {d}\n"
        else:
            domain_checklist += f"- [ ] {d}\n"
    
    # 添加其他自定义领域
    for d in domains:
        if d not in all_domains and d != "其他":
            domain_checklist += f"- [x] {d}\n"
    
    content = f"""---
date: '{today}'
last_modified: {today}
tags: [个人配置]
title: 个人配置
---

# 个人配置

## 👤 基本信息

- **创建日期**: {today}
- **用户名**: {username}

---

## 🎯 成长目标

> {goal}

---

## 📚 关注领域

{domain_checklist}
---

## 📊 对话统计

- 总对话次数: 0
- 发现的知识点: 0
- 发现的盲区: 0
- 最近一次对话: 无

---

## 📝 备注

（可以记录任何想让AI知道的背景信息）

"""
    
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def update_user_manual(strengths, help_style):
    """更新用户说明书"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""---
date: '{today}'
last_modified: {today}
tags: [用户画像]
title: 用户说明书
---

# 用户说明书 (User Manual)

## 📖 关于我

>这是一份给AI（以及未来的我）看的"操作指南"

### 1. 我的优势 (My Superpowers)
- {strengths if strengths else "待发现..."}

### 2. 我的弱点 (My Kryptonite)
- 待发现...

### 3. 我在压力下的表现
- 待观察...

### 4. 如何最好地帮助我
- {help_style if help_style else "待了解..."}

---

*这份文档将随着我们越来越了解而不断完善*

"""
    
    os.makedirs(os.path.dirname(USER_MANUAL_FILE), exist_ok=True)
    with open(USER_MANUAL_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    # 首次使用检查 - 收集用户信息
    if not check_user_profile_exists():
        collect_user_info()
    
    parser = argparse.ArgumentParser(description="Mind-OS CLI - Your Psyche's Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Audit command
    subparsers.add_parser("audit", help="Scan system for logical gaps and metadata issues")

    # Viz command
    subparsers.add_parser("viz", help="Generate 5D Ability Radar chart")
    
    # UI/Dashboard command
    subparsers.add_parser("ui", help="Launch the real-time Visual Dashboard")

    # Memory Sync command
    subparsers.add_parser("sync", help="Sync local notes into semantic memory (LlamaIndex)")

    # Query command
    query_parser = subparsers.add_parser("query", help="Query semantic memory")
    query_parser.add_argument("text", type=str, help="The query text")
    
    # Report command
    subparsers.add_parser("report", help="Generate a narrative AI synthesis of your current growth state")

    # Capture command
    capture_parser = subparsers.add_parser("capture", help="Quickly log a thought or insight")
    capture_parser.add_argument("message", type=str, help="The thought to record")
    
    # Set command
    set_parser = subparsers.add_parser("set", help="Quickly update a score and log evidence")
    set_parser.add_argument("dimension", type=str, help="The dimension to update (e.g., 执行力)")
    set_parser.add_argument("score", type=int, help="The new score (0-100)")
    set_parser.add_argument("evidence", type=str, help="The evidence or reason for change")

    # Study command (New)
    study_parser = subparsers.add_parser("study", help="Track your learning progress")
    study_parser.add_argument("action", choices=["log", "start", "stop"], help="Action to perform")
    study_parser.add_argument("course", type=str, help="Course name (e.g., 'Thinking Models')", nargs='?')
    study_parser.add_argument("--editor", type=str, help="Preferred editor command (e.g., 'cursor', 'code')", default=None)
    study_parser.add_argument("duration", type=float, help="Duration in minutes", nargs='?')
    study_parser.add_argument("notes", type=str, help="What did you learn?", nargs='?')

    read_parser = subparsers.add_parser("read", help="Read a file aloud (TTS)")
    read_parser.add_argument("file", type=str, help="Path to markdown file or 'stop' to end playback")

    # Remote command (New)
    subparsers.add_parser("remote", help="Launch the floating voice control remote")

    # Blackboard commands (New)
    board_parser = subparsers.add_parser("board", help="学习黑板 - 与AI对话学习")
    board_parser.add_argument("action", choices=["start", "reply", "show", "archive", "clear"], 
                              help="start=开始会话, reply=回复, show=查看, archive=归档, clear=清空")
    board_parser.add_argument("content", type=str, nargs="*", help="内容或主题")

    # AI teach command
    teach_parser = subparsers.add_parser("teach", help="AI在黑板上写教学内容")
    teach_parser.add_argument("content", type=str, help="教学内容")
    teach_parser.add_argument("--type", type=str, default="teach", 
                              choices=["question", "teach", "insight", "task", "feedback"],
                              help="内容类型")

    # Flomo commands
    flomo_parser = subparsers.add_parser("flomo", help="同步内容到 flomo 笔记")
    flomo_parser.add_argument("action", choices=["note", "insight", "retry", "status", "test"], 
                              help="note=快速笔记, insight=洞察, retry=重试队列, status=查看状态, test=测试")
    flomo_parser.add_argument("content", type=str, nargs="*", help="内容")

    args = parser.parse_args()

    if args.command == "audit":
        from scripts.consistency_check import scan_system
        scan_system(".")
    elif args.command == "viz":
        from scripts.radar_gen import create_radar_chart
        from scripts.growth_engine import get_growth_data
        create_radar_chart()
        growth = get_growth_data()
        if growth and "deltas" in growth:
            print("\n📈 今日成长摘要 (Growth Summary):")
            for dim, val in growth["deltas"].items():
                symbol = "↑" if val >= 0 else "↓"
                print(f"  - {dim}: {symbol} {abs(val)}%")
            print(f"📅 对比基准: {growth['dates'][0]} -> {growth['dates'][1]}")
    elif args.command == "ui":
        import subprocess
        print("🌐 Launching Mind-OS Dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "scripts/dashboard.py"])
    elif args.command == "sync":
        from scripts.memory_engine import sync_memory
        sync_memory()
    elif args.command == "query":
        from scripts.memory_engine import query_memory
        query_memory(args.text)
    elif args.command == "report":
        generate_narrative_report()
    elif args.command == "capture":
        from scripts.memory_engine import semantic_route
        semantic_route(args.message)
    elif args.command == "set":
        update_stat(args.dimension, args.score, args.evidence)
    elif args.command == "study":
        if args.action == "log":
            from scripts.study_tracker import log_study_session
            # If duration is missing, maybe we should warn or try a default
            duration = args.duration if args.duration is not None else 0
            log_study_session(args.course, duration, args.notes)
        elif args.action == "start":
            from scripts.study_tracker import start_session
            start_session(args.course or "General Thinking")
            
            # AUTO-START logic
            import glob
            import os
            import subprocess
            
            # ... existing file opening logic ...
            search_pattern = f"知识画像/*{args.course.replace(' ', '_')}*" if args.course else "知识画像/Thinking_Models"
            potential_dirs = glob.glob(search_pattern)
            if potential_dirs:
                md_files = glob.glob(os.path.join(potential_dirs[0], "*.md"))
                if md_files:
                    latest_file = max(md_files, key=os.path.getmtime)
                    print(f"🕯️ Entering Deep Reflection on: {os.path.basename(latest_file)}")
                    
                    # 1. Start Reading (Background)
                    from scripts.tts_engine import read_file
                    read_file(latest_file)
                    
                    # 2. Open file for user
                    if args.editor:
                        try:
                            # Use Popen to avoid blocking
                            subprocess.Popen([args.editor, latest_file], shell=True)
                        except Exception as e:
                            print(f"❌ Failed to open with {args.editor}: {e}")
                            if os.name == 'nt': os.startfile(latest_file)
                    elif os.name == 'nt':
                        os.startfile(latest_file)
                    else:
                        subprocess.run(['open', latest_file])
        elif args.action == "stop":
            from scripts.study_tracker import stop_and_log_session
            from scripts.tts_engine import stop_playback
            # Stop audio too
            stop_playback()
            # Stop timing and log
            notes = args.notes if args.notes else "学习归档"
            stop_and_log_session(notes)
    elif args.command == "read":
        from scripts.tts_engine import read_file
        read_file(args.file)
    elif args.command == "remote":
        import subprocess
        import os
        print("🚀 Launching Floating Remote...")
        # Use Popen to launch it as a separate persistent process
        subprocess.Popen([sys.executable, "scripts/voice_remote.py"], 
                         creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0,
                         close_fds=True)
    elif args.command == "board":
        from scripts.blackboard import start_session, user_reply, show_blackboard, archive_blackboard, clear_blackboard
        content = " ".join(args.content) if args.content else None
        if args.action == "start":
            start_session(content)
        elif args.action == "reply":
            if content:
                user_reply(content)
            else:
                print("❌ 请输入回复内容")
        elif args.action == "show":
            show_blackboard()
        elif args.action == "archive":
            archive_blackboard(content)
        elif args.action == "clear":
            clear_blackboard()
    elif args.command == "teach":
        from scripts.blackboard import ai_write
        ai_write(args.content, args.type)
    elif args.command == "flomo":
        from scripts.flomo_sync import quick_note, sync_insight, send_to_flomo, retry_queue, show_queue
        content = " ".join(args.content) if args.content else ""
        if args.action == "test":
            send_to_flomo("🧠 Mind-OS 连接测试", tags=["MindOS", "测试"])
        elif args.action == "note":
            quick_note(content)
        elif args.action == "insight":
            sync_insight(content)
        elif args.action == "retry":
            retry_queue()
        elif args.action == "status":
            show_queue()
    else:
        parser.print_help()

def update_stat(dimension, score, evidence):
    """Update a specific dimension score and append evidence."""
    import os
    import re
    import datetime
    
    print(f"⚡ Updating {dimension} to {score}...")
    
    # Mapping table to internal YAML keys
    key_map = {
        "认知力": "cognitive_score",
        "执行力": "execution_score",
        "情感力": "emotional_score",
        "社交力": "social_score",
        "创造力": "creativity_score"
    }
    
    if dimension not in key_map:
        print(f"❌ Error: Unknown dimension '{dimension}'. Please use one of: {list(key_map.keys())}")
        return

    # For now, we update the master file: 知识画像/综合画像.md
    target_file = "知识画像/综合画像.md"
    if not os.path.exists(target_file):
        print(f"❌ Error: {target_file} not found.")
        return

    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update YAML score
    yaml_key = key_map[dimension]
    pattern = rf"({yaml_key}:\s*)\d+"
    if re.search(pattern, content):
        new_content = re.sub(pattern, rf"\g<1>{score}", content)
    else:
        # If key not found, insert it before 'last_updated' or at the end of frontmatter
        if "---" in content:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                parts[1] = parts[1].strip() + f"\n{yaml_key}: {score}\n"
                new_content = "---" + parts[1] + "---" + parts[2]
            else:
                new_content = content + f"\n{yaml_key}: {score}"
        else:
            new_content = content + f"\n{yaml_key}: {score}"
    
    # 2. Append Evidence
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    evidence_block = f"\n\n### 📈 {dimension} 变动记录 ({timestamp})\n"
    evidence_block += f"- **新分值**: {score}\n"
    evidence_block += f"- **原因/证据**: {evidence}\n"
    
    new_content += evidence_block
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ {target_file} updated. Re-generating radar chart...")
    from scripts.radar_gen import create_radar_chart
    create_radar_chart()

def generate_narrative_report():
    """Synthesize a deep AI narrative report based on semantic memory."""
    import datetime
    import os
    from scripts.radar_gen import get_dynamic_scores, load_config
    
    print("📜 Generating Deep AI Growth Report...")
    config = load_config()
    scores = get_dynamic_scores(config)
    dims = [d.get('key', d['name']) for d in config.get('radar', {}).get('dimensions', [])]
    score_dict = dict(zip(dims, scores))
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# 🧠 Mind-OS 深度审计报告 ({timestamp})

## 1. 📊 现状快照
{pd.DataFrame([score_dict]).T.to_markdown()}

## 2. 🔍 核心洞察 (Semantic Synthesis)
"""
    # Use retrieval to find recent "captured thoughts" to synthesize themes
    from scripts.memory_engine import query_memory
    recent_thoughts = query_memory("近期发现的潜意识模式与执行瓶颈")
    
    if recent_thoughts:
        report += "\n### 🧊 潜意识冰山之下\n"
        for i, node in enumerate(recent_thoughts[:3]):
            report += f"- **核心片段 {i+1}**: {node.text[:150]}... (来源: {os.path.basename(node.metadata.get('file_path'))})\n"
    
    report += "\n## 3. ⚖️ 世界观冲突检查 (Worldview Audit)\n"
    
    # WORLDVIEW CONFLICT LOGIC
    # Hypothesis: Search for contradictions between 'Finance' (Logic/Asset) and 'Awareness' (Internal)
    conflicts = query_memory("冲突、矛盾、知行不一、防御机制")
    if conflicts:
        report += "> [!WARNING]\n"
        report += "> 检测到以下深层语义冲突：\n"
        for c in conflicts[:2]:
            report += f"> - **潜在线索**: {c.text[:200]}...\n"

    report += "\n## 4. 🚀 优先级行动建议\n"
    if score_dict.get('执行力', 0) > score_dict.get('认知力', 0) + 10:
        report += "- **停止盲目行动**：您的执行力远超认知，建议回流至少 10 小时进入《思维模型》练习，防止方向性偏航。\n"
    if score_dict.get('社交力', 0) < 30:
        report += "- **激活外部链接**：社交分值过低。尝试将本周的一个认知难题主动分享给一位在该领域有建树的朋友，打破孤狼闭环。\n"

    report_path = "分析报告/AI深度审计报告.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"✅ Report generated: {report_path}")
    print("---------------------------------")
    print(report)
    print("---------------------------------")

if __name__ == "__main__":
    main()
