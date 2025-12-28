import streamlit as st
import os
import yaml
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
from scripts.radar_gen import get_dynamic_scores, load_config
from scripts.consistency_check import check_logical_dissonance
from scripts.memory_engine import query_memory

# Page Config
st.set_page_config(page_title="Mind-OS Dashboard", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
        color: #f1f5f9;
    }
    .stMetric {
        background: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# sidebar
st.sidebar.title("Mind-OS Control")
st.sidebar.info("🧠 Status: Active & Synced")

# Load Data
config = load_config()
root_dir = os.path.join(os.path.dirname(__file__), '..')

st.title("🧠 Mind-OS 实时成长仪表盘")
st.write("---")

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📊 五维能力实时雷达")
    scores = get_dynamic_scores(config)
    dims = [d.get('key', d['name']) for d in config.get('radar', {}).get('dimensions', [])]
    
    # Matplotlib Radar (reusing logic but for streamlit)
    num_vars = len(dims)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    stats_closed = scores + [scores[0]]
    angles_closed = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True), facecolor='#0f172a')
    ax.set_facecolor('#1e293b')
    plt.xticks(angles, dims, color='#94a3b8', size=12)
    ax.set_rlabel_position(0)
    plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="#475569", size=8)
    plt.ylim(0, 100)
    ax.plot(angles_closed, stats_closed, color='#1aafad', linewidth=3)
    ax.fill(angles_closed, stats_closed, color='#1aafad', alpha=0.3)
    ax.grid(color='#334155')
    
    st.pyplot(fig)

with col2:
    st.subheader("⚖️ 系统审计与逻辑预警")
    dissonance = check_logical_dissonance(root_dir)
    
    if not dissonance:
        st.success("✅ 目前系统逻辑一致，知行合一。")
    else:
        for item in dissonance:
            st.error(item)
            
    st.write("---")
    st.subheader("🔎 语义记忆检索")
    q = st.text_input("想不起来某个灵感？输入关键词搜索记忆库：", placeholder="例如：社交回避、执行力...")
    if q:
        results = query_memory(q)
        if results:
            for r in results:
                with st.expander(f"📄 {os.path.basename(r.metadata.get('file_path'))}"):
                    st.write(r.text)
        else:
            st.warning("未找到相关记忆。")

st.write("---")
st.subheader("📈 认知与执行进化曲线 (Growth Timeline)")

history_file = os.path.join(root_dir, "量化算法", "history_log.json")
if os.path.exists(history_file):
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        
        if history_data:
            # Convert to DataFrame for plotting
            rows = []
            for entry in history_data:
                row = entry["scores"].copy()
                row["时间"] = entry["timestamp"]
                rows.append(row)
            
            df = pd.DataFrame(rows).set_index("时间")
            st.line_chart(df)
        else:
            st.info("尚未发现历史轨迹数据，请通过 `viz` 命令更新评分。")
    except Exception as e:
        st.error(f"加载历史日志失败: {e}")
else:
    st.info("尚未生成历史轨迹，请运行一次 `mind-os.py viz`。")

st.write("---")
st.subheader("🧭 快速洞察分类器")
msg = st.text_area("输入新的思考片段：", placeholder="系统会自动为您分拣到对应的文件...")
if st.button("提交到系统"):
    if msg:
        from scripts.memory_engine import semantic_route
        target_file = semantic_route(msg)
        st.success(f"✅ 已成功分拣至：{os.path.basename(target_file)}")
    else:
        st.warning("请输入内容。")

st.markdown("---")
st.caption("Mind-OS v1.1.0 | Offline First | Powered by LlamaIndex & Streamlit")
