import os
import yaml
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

# Set font for Chinese support
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False # Fix for minus sign display

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'mind_os_config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        return None

def create_radar_chart():
    config = load_config()
    if not config:
        print("❌ Error: Could not load config.")
        return

    radar_cfg = config.get('radar', {})
    
    # Use Chinese keys for labels if possible
    dimensions = [d.get('key', d['name']) for d in radar_cfg.get('dimensions', [])]
    
    # Simulated current scores (will be dynamic in future)
    stats = [75, 85, 60, 20, 70] 
    
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    plt.xticks(angles[:-1], dimensions, color='grey', size=12)
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="grey", size=7)
    plt.ylim(0, 100)

    ax.plot(angles, stats, color='#1aafad', linewidth=2, linestyle='solid')
    ax.fill(angles, stats, color='#1aafad', alpha=0.25)
    plt.title('Mind-OS 五维能力雷达图', size=15, color='#1aafad', y=1.1)
    
    output_path = radar_cfg.get('output_file', '分析报告/latest_radar.png')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path)
    print(f"📊 Radar chart generated at: {output_path}")

if __name__ == "__main__":
    create_radar_chart()
