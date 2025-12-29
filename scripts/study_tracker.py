import os
import json
import datetime
import re
import yaml

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', '量化算法', 'learning_log.json')
SESSION_FILE = os.path.join(os.path.dirname(__file__), 'session.json')
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')

def start_session(course):
    """Start a new timed study session."""
    session = {
        "course": course,
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(session, f, indent=2)
    print(f"⏱️ Session STARTED for '{course}' at {session['start_time']}.")

def stop_and_log_session(notes):
    """Calculate duration from session.json and log to learning_log.json."""
    if not os.path.exists(SESSION_FILE):
        print("❌ No active session found to stop.")
        return None

    try:
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        start_dt = datetime.datetime.strptime(session['start_time'], "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.datetime.now()
        duration_delta = end_dt - start_dt
        duration_minutes = round(duration_delta.total_seconds() / 60.0, 1)
        
        course = session['course']
        log_study_session(course, duration_minutes, notes)
        
        # Clean up session file
        os.remove(SESSION_FILE)
        print(f"🏁 Session STOPPED. Duration: {duration_minutes} minutes.")
        return duration_minutes
    except Exception as e:
        print(f"❌ Error结算 session: {e}")
        return None

def log_study_session(course, duration_minutes, notes):
    """Append a study session to the persistent log."""
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "course": course,
        "duration_minutes": float(duration_minutes),
        "notes": notes
    }
    
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    data = json.loads(content)
        except json.JSONDecodeError:
            data = []
            
    data.append(entry)
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Logged: {duration_minutes} mins for '{course}'.")

def get_time_stats():
    """Aggregate total time spent per course."""
    if not os.path.exists(LOG_FILE):
        return {}
        
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        return {}
        
    stats = {}
    for entry in data:
        course = entry.get('course', 'Uncategorized')
        duration = entry.get('duration_minutes', 0)
        stats[course] = stats.get(course, 0) + duration
        
    return stats

def get_granular_progress(target_dir_name="知识画像"):
    """Scan markdown files for - [x] checklists."""
    target_path = os.path.join(ROOT_DIR, target_dir_name)
    
    course_stats = {} 
    # Structure: { "Python Base": { "total_points": 10, "completed_points": 3, "files": [...] } }

    for root, _, files in os.walk(target_path):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract Course from Frontmatter or Directory Name
                course = "General"
                match = re.search(r'^course:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
                if match:
                    course = match.group(1)
                else:
                    # Fallback to parent dir name
                    parent_dir = os.path.basename(os.path.dirname(file_path))
                    if "AI_Fullstack" not in parent_dir:
                         course = parent_dir

                # Count Checkboxes
                total_checks = len(re.findall(r'^\s*-\s*\[\s?\]', content, re.MULTILINE)) + \
                               len(re.findall(r'^\s*-\s*\[x\]', content, re.MULTILINE))
                completed_checks = len(re.findall(r'^\s*-\s*\[x\]', content, re.MULTILINE))
                
                if total_checks > 0:
                    if course not in course_stats:
                        course_stats[course] = {"total": 0, "done": 0, "files": 0}
                    
                    course_stats[course]["total"] += total_checks
                    course_stats[course]["done"] += completed_checks
                    course_stats[course]["files"] += 1
                    
                    # Update file metadata 'progress' if needed (optional, implemented for consistency)
                    # We won't write back to file to avoid IO overhead, but we calculate it.
                    
    return course_stats

if __name__ == "__main__":
    # Test
    print(get_granular_progress())
