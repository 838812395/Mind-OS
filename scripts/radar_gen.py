import os
import yaml
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import re
import json
import datetime

# Set font for Chinese support
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False 

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'mind_os_config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        return None

def extract_yaml(content):
    """Robust extraction of YAML frontmatter using index search."""
    content = content.strip()
    if not content.startswith('---'):
        return None
    end = content.find('---', 3)
    if end == -1:
        return None
    yaml_str = content[3:end].strip()
    try:
        return yaml.safe_load(yaml_str)
    except Exception as e:
        return None

def get_dynamic_scores(config):
    """Scan directories and extract scores from YAML metadata."""
    target_dirs = config.get('directories', {})
    root_dir = os.path.join(os.path.dirname(__file__), '..')
    
    # Mapping of technical keys to display dimensions
    # We want to match: 认知力, 执行力, 情感力, 社交力, 创造力
    score_map = {
        "认知力": [],
        "执行力": [],
        "情感力": [],
        "社交力": [],
        "创造力": []
    }
    
    # Search keys in YAML
    key_aliases = {
        "cognitive_score": "认知力",
        "execution_score": "执行力",
        "emotional_score": "情感力",
        "social_score": "社交力",
        "creativity_score": "创造力",
        # Support schema proposed in 元数据Schema.md
        "current_score": None # Will handle separately based on 'dimension' key
    }

    for dir_name in target_dirs.values():
        full_path = os.path.join(root_dir, dir_name)
        if not os.path.exists(full_path):
            continue
        
        for root, _, files in os.walk(full_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            data = extract_yaml(content)
                            if not data:
                                continue
                            
                            # Type 1: Explicit mapping (e.g. cognitive_score: 75)
                            for k, dim in key_aliases.items():
                                if k in data and dim:
                                    score_map[dim].append(data[k])
                                elif k == "current_score" and "current_score" in data and "dimension" in data:
                                    dim_raw = data["dimension"]
                                    if dim_raw in score_map:
                                        score_map[dim_raw].append(data["current_score"])
                    except:
                        continue

    # Aggregate scores (simple average for now)
    final_stats = []
    dimensions_cfg = config.get('radar', {}).get('dimensions', [])
    
    for d in dimensions_cfg:
        dim_key = d.get('key')
        scores = score_map.get(dim_key, [])
        if scores:
            final_stats.append(sum(scores) / len(scores))
        else:
            # Fallback to a baseline if no data found
            final_stats.append(50) 
            
    return final_stats

def create_radar_chart():
    config = load_config()
    if not config:
        print("❌ Error: Could not load config.")
        return

    radar_cfg = config.get('radar', {})
    dimensions = [d.get('key', d['name']) for d in radar_cfg.get('dimensions', [])]
    
    # FETCH DYNAMIC SCORES
    print("📈 Extracting real-time scores from system metadata...")
    stats = get_dynamic_scores(config)
    
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    # Close the circle
    stats_closed = stats + [stats[0]]
    angles_closed = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    plt.xticks(angles, dimensions, color='grey', size=12)
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="grey", size=7)
    plt.ylim(0, 100)

    ax.plot(angles_closed, stats_closed, color='#1aafad', linewidth=2, linestyle='solid')
    ax.fill(angles_closed, stats_closed, color='#1aafad', alpha=0.25)
    
    # Add data labels
    for angle, stat, label in zip(angles, stats, dimensions):
        ax.text(angle, stat+5, f"{int(stat)}", ha='center', va='center', size=10, color='#0a6b6a')

    plt.title('Mind-OS 五维能力实时动态图', size=15, color='#1aafad', y=1.1)
    
    output_path = radar_cfg.get('output_file', '分析报告/latest_radar.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path)
    print(f"✅ Dynamic Radar generated successfully at: {output_path}")
    print(f"📊 Current Scores: {dict(zip(dimensions, [int(s) for s in stats]))}")

    # LOG HISTORY
    log_history(config, dimensions, stats)

def log_history(config, dimensions, stats):
    """Save scores to history_log.json."""
    root_dir = os.path.join(os.path.dirname(__file__), '..')
    history_file = os.path.join(root_dir, "量化算法", "history_log.json")
    
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "scores": dict(zip(dimensions, [round(s, 2) for s in stats]))
    }
    
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
            
    # Avoid duplicate logs for the same minute
    if history and history[-1]["timestamp"] == entry["timestamp"]:
        history[-1] = entry
    else:
        history.append(entry)
        
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"🕰️ History logged to: {os.path.basename(history_file)}")

if __name__ == "__main__":
    create_radar_chart()
