import sys
import argparse
import pandas as pd
from scripts.consistency_check import scan_system
from scripts.radar_gen import create_radar_chart
from scripts.memory_engine import sync_memory, query_memory, semantic_route

def main():
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

    args = parser.parse_args()

    if args.command == "audit":
        scan_system(".")
    elif args.command == "viz":
        create_radar_chart()
    elif args.command == "ui":
        import subprocess
        print("🌐 Launching Mind-OS Dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "scripts/dashboard.py"])
    elif args.command == "sync":
        sync_memory()
    elif args.command == "query":
        query_memory(args.text)
    elif args.command == "report":
        generate_narrative_report()
    elif args.command == "capture":
        semantic_route(args.message)
    elif args.command == "set":
        update_stat(args.dimension, args.score, args.evidence)
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
