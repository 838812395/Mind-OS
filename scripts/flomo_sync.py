"""
Mind-OS Flomo 同步模块 - 带离线队列和去重机制
"""
import os
import sys
import json
import hashlib
import requests
import yaml
from datetime import datetime

CONFIG_FILE = "config/mind_os_config.yaml"
QUEUE_FILE = ".mind_os/flomo_queue.json"
HISTORY_FILE = ".mind_os/flomo_history.json"
LOCAL_BACKUP_DIR = "增量引擎/flomo备份"

def ensure_dirs():
    """确保必要目录存在"""
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    os.makedirs(LOCAL_BACKUP_DIR, exist_ok=True)

def load_flomo_api():
    """从配置文件加载 flomo API"""
    config_path = os.path.join(os.path.dirname(__file__), '..', CONFIG_FILE)
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('flomo', {}).get('api_url')
    return None

def content_hash(content):
    """生成内容哈希，用于去重"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]

def load_history():
    """加载已上传历史"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"uploaded": []}

def save_history(history):
    """保存上传历史"""
    ensure_dirs()
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def is_duplicate(content):
    """检查是否重复"""
    history = load_history()
    h = content_hash(content)
    return h in history.get("uploaded", [])

def mark_uploaded(content):
    """标记为已上传"""
    history = load_history()
    h = content_hash(content)
    if h not in history["uploaded"]:
        history["uploaded"].append(h)
        # 只保留最近1000条记录
        if len(history["uploaded"]) > 1000:
            history["uploaded"] = history["uploaded"][-1000:]
        save_history(history)

def load_queue():
    """加载待上传队列"""
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"pending": []}

def save_queue(queue):
    """保存队列"""
    ensure_dirs()
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

def add_to_queue(content, tags=None):
    """添加到待上传队列"""
    queue = load_queue()
    item = {
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hash": content_hash(content)
    }
    # 检查队列中是否已存在
    existing_hashes = [i.get("hash") for i in queue["pending"]]
    if item["hash"] not in existing_hashes:
        queue["pending"].append(item)
        save_queue(queue)
        print(f"📥 已加入待上传队列 (共 {len(queue['pending'])} 条待传)")
    else:
        print("⚠️ 该内容已在队列中")

def save_local_backup(content, tags=None):
    """本地备份"""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"flomo_{timestamp}.md"
    filepath = os.path.join(LOCAL_BACKUP_DIR, filename)
    
    tag_str = " ".join([f"#{t}" for t in (tags or [])]) if tags else ""
    backup_content = f"""---
date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
tags: {tags or []}
synced: false
---

{content}

{tag_str}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(backup_content)
    
    return filepath

def do_upload(content, tags=None):
    """执行实际上传"""
    api_url = load_flomo_api()
    if not api_url:
        return False, "未配置 flomo API"
    
    # 添加标签到内容
    if tags:
        tag_str = " ".join([f"#{tag}" for tag in tags])
        full_content = f"{content}\n\n{tag_str}"
    else:
        full_content = content
    
    try:
        response = requests.post(
            api_url,
            json={"content": full_content},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                return True, "成功"
            else:
                return False, result.get("message", "未知错误")
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, str(e)

def send_to_flomo(content, tags=None):
    """
    发送内容到 flomo（带队列和去重）
    
    流程：
    1. 检查是否重复
    2. 本地备份
    3. 尝试上传
    4. 失败则加入队列
    """
    # 去重检查
    if is_duplicate(content):
        print("⚠️ 该内容已上传过，跳过")
        return True
    
    # 本地备份
    backup_path = save_local_backup(content, tags)
    print(f"💾 本地备份: {backup_path}")
    
    # 尝试上传
    success, msg = do_upload(content, tags)
    
    if success:
        print(f"✅ 已同步到 flomo")
        mark_uploaded(content)
        return True
    else:
        print(f"❌ 上传失败: {msg}")
        add_to_queue(content, tags)
        return False

def retry_queue():
    """重试队列中的待上传内容"""
    queue = load_queue()
    if not queue["pending"]:
        print("📭 队列为空，无待上传内容")
        return
    
    print(f"🔄 开始重试上传 ({len(queue['pending'])} 条)...")
    
    success_count = 0
    failed = []
    
    for item in queue["pending"]:
        content = item["content"]
        tags = item.get("tags", [])
        
        # 再次检查去重
        if is_duplicate(content):
            print(f"  ⏭️ 跳过已上传: {content[:20]}...")
            continue
        
        success, msg = do_upload(content, tags)
        if success:
            print(f"  ✅ 上传成功: {content[:30]}...")
            mark_uploaded(content)
            success_count += 1
        else:
            print(f"  ❌ 仍然失败: {msg}")
            failed.append(item)
    
    # 更新队列，只保留失败的
    queue["pending"] = failed
    save_queue(queue)
    
    print(f"\n📊 结果: 成功 {success_count}, 仍待传 {len(failed)}")

def show_queue():
    """显示队列状态"""
    queue = load_queue()
    history = load_history()
    
    print(f"📊 Flomo 同步状态")
    print(f"   待上传: {len(queue['pending'])} 条")
    print(f"   已上传: {len(history.get('uploaded', []))} 条")
    
    if queue["pending"]:
        print("\n📋 待上传内容:")
        for i, item in enumerate(queue["pending"][:5], 1):
            preview = item["content"][:40].replace("\n", " ")
            print(f"   {i}. [{item['created_at']}] {preview}...")
        if len(queue["pending"]) > 5:
            print(f"   ... 还有 {len(queue['pending']) - 5} 条")

# 便捷函数
def quick_note(note):
    """快速笔记"""
    return send_to_flomo(note, tags=["MindOS"])

def sync_insight(insight, source=None):
    """同步洞察"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"💡 {insight}"
    if source:
        content += f"\n\n📍 来源: {source}"
    content += f"\n⏰ {timestamp}"
    return send_to_flomo(content, tags=["MindOS", "洞察"])

def sync_learning(topic, summary):
    """同步学习总结"""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    content = f"📚 学习笔记: {topic}\n\n{summary}\n\n📅 {timestamp}"
    return send_to_flomo(content, tags=["MindOS", "学习", topic.replace(" ", "")])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python flomo_sync.py note <内容>     - 快速笔记")
        print("  python flomo_sync.py insight <洞察>  - 同步洞察")
        print("  python flomo_sync.py retry           - 重试待上传队列")
        print("  python flomo_sync.py status          - 查看队列状态")
        print("  python flomo_sync.py test            - 测试连接")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "test":
        send_to_flomo("🧠 Mind-OS 连接测试", tags=["MindOS", "测试"])
    elif cmd == "note":
        content = " ".join(sys.argv[2:])
        quick_note(content)
    elif cmd == "insight":
        content = " ".join(sys.argv[2:])
        sync_insight(content)
    elif cmd == "retry":
        retry_queue()
    elif cmd == "status":
        show_queue()
    else:
        print(f"未知命令: {cmd}")
