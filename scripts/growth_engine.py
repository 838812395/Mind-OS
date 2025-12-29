import os
import json
import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', '量化算法', 'history_log.json')

def get_growth_data():
    """Load history and calculate deltas between last two significantly different days."""
    if not os.path.exists(HISTORY_FILE):
        return None
        
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        return None
        
    if len(history) < 2:
        return {"current": history[-1]["scores"] if history else {}, "previous": {}, "deltas": {}}

    # Group by date to find "Yesterday's last record" and "Today's last record"
    daily_records = {}
    for entry in history:
        date = entry["timestamp"].split(" ")[0]
        daily_records[date] = entry["scores"]
        
    dates = sorted(daily_records.keys())
    
    current_date = dates[-1]
    previous_date = dates[-2] if len(dates) > 1 else dates[-1]
    
    current_scores = daily_records[current_date]
    previous_scores = daily_records[previous_date]
    
    deltas = {}
    for dim, score in current_scores.items():
        prev = previous_scores.get(dim, 50)
        # Avoid division by zero
        if prev == 0: prev = 1
        delta_pct = ((score - prev) / prev) * 100
        deltas[dim] = round(delta_pct, 2)
        
    return {
        "current": current_scores,
        "previous": previous_scores,
        "deltas": deltas,
        "dates": (previous_date, current_date)
    }

def generate_1_percent_advice():
    """Analyze current state and suggest a 1% improvement task."""
    data = get_growth_data()
    if not data:
        return "🌱 系统还在观察期，请继续保持记录。"
        
    current = data["current"]
    deltas = data["deltas"]
    
    # Logic: Prioritize dimensions that are regressing or simply low
    worst_dim = min(current, key=current.get)
    regressing_dim = min(deltas, key=deltas.get) if deltas else None
    
    target_dim = regressing_dim if (regressing_dim and deltas[regressing_dim] < 0) else worst_dim
    
    advice_map = {
        "认知力": "阅读一篇新的思维模型笔记并写下感悟 (证据分 +5)",
        "执行力": "完成一个 Java 知识点的操作清单 (证据分 +5)",
        "情感力": "进行一次 10 分钟的冥想或深度情绪笔记 (证据分 +5)",
        "社交力": "向 AI 或他人清晰表达一个复杂观点 (证据分 +5)",
        "创造力": "结合第一性原理为系统设计一个新功能 (证据分 +5)"
    }
    
    task = advice_map.get(target_dim, "继续保持记录")
    
    return {
        "target": target_dim,
        "advice": f"今日 1% 挑战：在 **{target_dim}** 维度发力，{task}。",
        "status": "falling" if deltas and deltas.get(target_dim, 0) < 0 else "maintaining"
    }

if __name__ == "__main__":
    print(json.dumps(get_growth_data(), indent=2, ensure_ascii=False))
    print(generate_1_percent_advice())
