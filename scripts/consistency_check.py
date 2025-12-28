import os
import re
import yaml

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'mind_os_config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        # Fallback to defaults
        return {
            'directories': {'knowledge': '知识画像', 'psychology': '心理画像', 'algorithms': '量化算法', 'awareness': '深度觉察'}
        }

def check_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # More flexible check for YAML block
    yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not yaml_match:
        return False, "Missing or Malformed YAML Frontmatter"
    
    try:
        metadata = yaml.safe_load(yaml_match.group(1))
        if not metadata:
            return False, "Empty YAML Frontmatter"
        return True, metadata
    except Exception as e:
        return False, f"YAML Syntax Error: {e}"

def scan_system(root_dir="."):
    config = load_config()
    target_dirs = config.get('directories', {}).values()
    
    print(f"🔍 Scanning Mind-OS at: {os.path.abspath(root_dir)}\n")
    
    issues = []
    for doc_dir in target_dirs:
        full_path = os.path.join(root_dir, doc_dir)
        if not os.path.exists(full_path):
            print(f"⚠️ Warning: Directory '{doc_dir}' not found. Skipping.")
            continue
            
        for file in os.listdir(full_path):
            if file.endswith('.md'):
                fpath = os.path.join(full_path, file)
                valid, result = check_metadata(fpath)
                if not valid:
                    issues.append(f"❌ {doc_dir}/{file}: {result}")
                else:
                    print(f"✅ {doc_dir}/{file}: Verified")
                    
    if issues:
        print("\n⚠️ Found Metadata Issues:")
        for issue in issues:
            print(issue)
    else:
        print("\n✨ All files follow the standard schema.")

if __name__ == "__main__":
    scan_system()
