import os
import yaml
import datetime

def get_default_metadata(file_path, root_dir):
    """Infer metadata based on directory structure."""
    rel_path = os.path.relpath(file_path, root_dir)
    parts = rel_path.split(os.sep)
    
    top_dir = parts[0] if len(parts) > 1 else "root"
    basename = os.path.basename(file_path)
    title = os.path.splitext(basename)[0]
    
    metadata = {
        "title": title,
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "tags": [],
        "last_modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # Context-aware defaults
    if top_dir == "知识画像":
        metadata["type"] = "knowledge_node"
        metadata["proficiency"] = "L1" # Default to Novice
    elif top_dir == "量化算法":
        metadata["type"] = "algorithm"
    elif top_dir == "深度觉察":
        metadata["type"] = "reflection"
    elif top_dir == "分析报告":
        metadata["type"] = "report"
        metadata["status"] = "draft"
    elif top_dir == "无知地图":
        metadata["type"] = "gap_analysis"
    elif top_dir == "思维模型":
        metadata["type"] = "mental_model"
    elif top_dir == "心理画像":
        metadata["type"] = "profile"
    
    return metadata

def add_frontmatter(root_dir):
    print(f"🛠️ Starting Metadata Auto-Fix in: {root_dir}")
    count = 0
    
    for root, _, files in os.walk(root_dir):
        # Skip system directories
        if ".mind_os" in root or ".git" in root or ".venv" in root:
            continue
            
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if YAML exists
                    if content.strip().startswith('---'):
                        continue
                    
                    # Generate Metadata
                    metadata = get_default_metadata(file_path, root_dir)
                    yaml_str = yaml.dump(metadata, allow_unicode=True, default_flow_style=False)
                    
                    new_content = f"---\n{yaml_str}---\n\n{content}"
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
                    print(f"✅ Fixed: {os.path.relpath(file_path, root_dir)}")
                    count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to process {file}: {e}")

    print(f"\n🎉 Done! Added metadata to {count} files.")

if __name__ == "__main__":
    # Assume script is in /scripts, run on parent dir
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    add_frontmatter(root)
