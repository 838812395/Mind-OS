try:
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
    from scripts.study_tracker import get_time_stats, get_granular_progress
    from scripts.growth_engine import get_growth_data, generate_1_percent_advice
except ImportError as e:
    import sys
    print(f"❌ Mind-OS Dashboard Error: Missing dependency ({e})")
    print("   Please install required libraries: pip install streamlit matplotlib pandas")
    sys.exit(1)

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
    
    # --- GROWTH DELTAS ---
    growth = get_growth_data()
    if growth and growth.get("deltas"):
        st.caption("📈 每日增量 (Relative to Yesterday)")
        delta_cols = st.columns(len(growth["deltas"]))
        for i, (dim, val) in enumerate(growth["deltas"].items()):
            color = "#10b981" if val >= 0 else "#ef4444"
            with delta_cols[i]:
                st.markdown(f"<p style='color:{color}; font-size:14px; font-weight:bold;'>{dim}<br>{'↑' if val >= 0 else '↓'} {abs(val)}%</p>", unsafe_allow_html=True)
    
    # --- 1% ADVICE ---
    advice = generate_1_percent_advice()
    st.info(advice["advice"] if isinstance(advice, dict) else advice)

with col2:
    st.subheader("⚖️ 系统审计与逻辑预警")
    dissonance = check_logical_dissonance(root_dir)
    
    if not dissonance:
        st.success("✅ 目前系统逻辑一致，知行合一。")
    else:
        for item in dissonance:
            st.error(item)
            
    st.write("---")
    
    # --- GLOBAL VOICE CONTROL ---
    v_ctrl1, v_ctrl2 = st.columns([1, 5])
    with v_ctrl1:
        if st.button("🛑 全局停止朗读", use_container_width=True):
            from scripts.tts_engine import stop_playback
            stop_playback()
            st.toast("已停止所有背景朗读")
    
    # --- LEARNING CENTER ---
    st.subheader("🎓 全栈学习中心 (AI Fullstack Tracker)")
    
    # 1. Time Stats
    time_stats = get_time_stats()
    granular_stats = get_granular_progress()
    
    if time_stats:
        st.caption("⏱️ 累计投入时间 (Hours)")
        cols = st.columns(len(time_stats))
        for i, (course, mins) in enumerate(time_stats.items()):
            with cols[i % 4]: # Wrap every 4
                st.metric(course, f"{mins/60:.1f} h")
    else:
        st.info("尚未开始记录学习时间。使用 `python mind-os.py study log ...` 开始打卡！")

    # 2. Granular Progress (Checklists)
    st.caption("✅ 知识点亮进度 (Knowledge Points)")
    if granular_stats:
        for course, data in granular_stats.items():
            total = data['total']
            done = data['done']
            percent = done / total if total > 0 else 0
            
            st.write(f"**{course}**")
            st.progress(percent)
            st.code(f"已点亮: {done} / {total} 个知识点 ({int(percent*100)}%) | 涉及文件数: {data['files']}")
            
            # --- VOICE CONTROL BUTTONS ---
            v_col1, v_col2 = st.columns([1, 4])
            with v_col1:
                if st.button(f"🔊 朗读记录", key=f"read_{course}"):
                    # Find any .md files in knowledge base subfolders
                    import glob
                    # Search pattern: 知识画像/AI_Fullstack/**/01_*.md etc.
                    # For simplicity, search the course subfolder if we can find it
                    potential_dirs = glob.glob(f"知识画像/AI_Fullstack/*{course.replace(' ', '_')}*")
                    if potential_dirs:
                        md_files = glob.glob(os.path.join(potential_dirs[0], "*.md"))
                        if md_files:
                            latest_file = max(md_files, key=os.path.getmtime)
                            st.info(f"正在准备朗读: {os.path.basename(latest_file)}...")
                            from scripts.tts_engine import read_file
                            read_file(latest_file)
                            st.success("开始后台朗读。")
                        else:
                            st.warning("该目录下没有发现 Markdown 笔记。")
                    else:
                        st.warning(f"找不到对应的课程目录: {course}")
            with v_col2:

                if st.button(f"⏹️ 停止", key=f"stop_{course}"):
                    from scripts.tts_engine import stop_playback
                    stop_playback()
                    st.toast("朗读已停止")

    else:
        st.info("未检测到包含 Checklist 的学习笔记。")

    # --- STUDY HISTORY TABLE ---
    st.write("---")
    st.subheader("📜 历史学习记录 (Study History)")
    
    log_file = os.path.join(root_dir, '量化算法', 'learning_log.json')
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        if log_data:
            # Create a DataFrame for nice display, reversed so latest is on top
            df = pd.DataFrame(log_data)
            df = df.iloc[::-1] # Reverse
            
            # Format display
            df.columns = ["时间", "课程/科目", "时长(分钟)", "学习感悟"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("尚无历史记录。")
    else:
        st.info("尚未发现学习日志文件。")

    st.write("---")
    
    # --- TREND CHART ---
    st.subheader("📈 成长演进趋势 (Growth Trend)")
    if os.path.exists(log_file.replace('learning_log.json', 'history_log.json')):
        with open(log_file.replace('learning_log.json', 'history_log.json'), 'r', encoding='utf-8') as f:
            hist_data = json.load(f)
        if hist_data:
            trend_df = pd.DataFrame([{"时间": e["timestamp"], **e["scores"]} for e in hist_data])
            st.line_chart(trend_df.set_index("时间"))
        else:
            st.info("趋势数据生成中...")

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
