import os
import yaml
import re

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'mind_os_config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        return None

def extract_yaml(content):
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except:
            return None
    return None

def check_logical_dissonance(root_dir):
    """Detect gap between Goals and Behaviors."""
    results = []
    
    skill_tree_path = os.path.join(root_dir, "量化算法", "技能树.md")
    growth_log_path = os.path.join(root_dir, "无知地图", "成长日志.md")
    
    if not os.path.exists(skill_tree_path):
        return results

    # 1. Extract Goals
    goals = []
    with open(skill_tree_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Look for table entries in Bridge Plan
        table_match = re.search(r'## 🌉 差距缩减计划.*?\n(.*?)\n\n', content, re.DOTALL)
        if table_match:
            rows = table_match.group(1).strip().split('\n')
            for row in rows[2:]: # skip header and separator
                cols = [c.strip() for c in row.split('|')]
                if len(cols) > 2 and cols[2] != '-':
                    goals.append(cols[2])

    if not goals:
        return results

    # 2. Check Logs
    if not os.path.exists(growth_log_path):
        results.append("⚠️ Logical Gap: Goals defined in '技能树.md' but no '成长日志.md' found to track behaviors.")
        return results

    with open(growth_log_path, 'r', encoding='utf-8') as f:
        log_content = f.read().lower()
        
    for goal in goals:
        # Simple keyword matching for now, could be upgraded to semantic search
        keywords = re.findall(r'[\u4e00-\u9fa5]{2,}', goal) # Extract Chinese keywords
        match_found = False
        for kw in keywords:
            if kw.lower() in log_content:
                match_found = True
                break
        
        if not match_found:
            results.append(f"❌ Cognitive Dissonance: Action '{goal}' has no corresponding entries in logs.")
            
    return results

def scan_system(root_dir):
    config = load_config()
    if not config:
        print("❌ Error: Could not load config.")
        return

    target_dirs = config.get('directories', {}).values()
    require_frontmatter = config.get('audit', {}).get('require_frontmatter', True)
    
    all_ok = True
    print("🔍 Starting Mind-OS Consistency & Logic Audit...")

    # A. Metadata Integrity
    for d in target_dirs:
        dir_path = os.path.join(root_dir, d)
        if not os.path.exists(dir_path):
            continue
            
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_dir)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        if require_frontmatter:
                            if not content.startswith('---'):
                                print(f"❌ {rel_path}: Missing YAML Frontmatter")
                                all_ok = False
                            elif not extract_yaml(content):
                                print(f"❌ {rel_path}: Malformed YAML Frontmatter")
                                all_ok = False

    # B. Logical Consistency
    dissonance = check_logical_dissonance(root_dir)
    if dissonance:
        all_ok = False
        for item in dissonance:
            print(item)

    if all_ok:
        print("✅ System Audit Passed: All files validated and logic appears consistent.")
    else:
        print("\n🚨 System Audit Failed: Please address the issues above to maintain system integrity.")

if __name__ == "__main__":
    scan_system(".")
