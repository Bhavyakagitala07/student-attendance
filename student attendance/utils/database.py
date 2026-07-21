import os
import json
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

# Define file paths
FILES = {
    "users": os.path.join(DATA_DIR, "users.json"),
    "students": os.path.join(DATA_DIR, "students.json"),
    "attendance": os.path.join(DATA_DIR, "attendance.json"),
    "announcements": os.path.join(DATA_DIR, "announcements.json"),
    "notices": os.path.join(DATA_DIR, "notices.json")
}

def init_db() -> None:
    """
    Initializes the database directory and files if they do not exist.
    """
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        for name, filepath in FILES.items():
            if not os.path.exists(filepath):
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4)
            else:
                # If file exists but is empty or malformed, reset to empty list
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if not content:
                            raise ValueError("Empty file")
                        json.loads(content)
                except Exception:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump([], f, indent=4)
    except Exception as e:
        print(f"Error initializing database: {e}")

def _load_data(key: str) -> List[Dict[str, Any]]:
    """
    Helper to load list data from a specific JSON file.
    """
    init_db()
    filepath = FILES.get(key)
    if not filepath:
        return []
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data for {key}: {e}")
        return []

def _save_data(key: str, data: List[Dict[str, Any]]) -> bool:
    """
    Helper to save list data to a specific JSON file.
    """
    init_db()
    filepath = FILES.get(key)
    if not filepath:
        return False
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving data for {key}: {e}")
        return False

# ==========================================
# USER OPERATIONS
# ==========================================
def get_users() -> List[Dict[str, Any]]:
    return _load_data("users")

def save_users(users: List[Dict[str, Any]]) -> bool:
    return _save_data("users", users)

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    users = get_users()
    for user in users:
        if user.get("username") == username:
            return user
    return None

def add_user(user_data: Dict[str, Any]) -> bool:
    users = get_users()
    # Check if duplicate username
    if get_user_by_username(user_data["username"]):
        return False
    users.append(user_data)
    return save_users(users)

# ==========================================
# STUDENT OPERATIONS
# ==========================================
def get_students() -> List[Dict[str, Any]]:
    return _load_data("students")

def save_students(students: List[Dict[str, Any]]) -> bool:
    return _save_data("students", students)

def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    students = get_students()
    for student in students:
        if student.get("student_id") == student_id:
            return student
    return None

def add_student(student_data: Dict[str, Any]) -> bool:
    students = get_students()
    if get_student_by_id(student_data["student_id"]):
        return False
    students.append(student_data)
    return save_students(students)

def update_student(student_id: str, updated_data: Dict[str, Any]) -> bool:
    students = get_students()
    for i, student in enumerate(students):
        if student.get("student_id") == student_id:
            # Maintain the original student ID just in case
            updated_data["student_id"] = student_id
            students[i] = updated_data
            return save_students(students)
    return False

def delete_student(student_id: str) -> bool:
    students = get_students()
    new_students = [s for s in students if s.get("student_id") != student_id]
    if len(new_students) == len(students):
        return False
    return save_students(new_students)

# ==========================================
# ATTENDANCE OPERATIONS
# ==========================================
def get_attendance() -> List[Dict[str, Any]]:
    return _load_data("attendance")

def save_attendance(attendance_list: List[Dict[str, Any]]) -> bool:
    return _save_data("attendance", attendance_list)

def get_attendance_record(date_str: str, dept: str, sec: str) -> Optional[Dict[str, Any]]:
    records = get_attendance()
    for rec in records:
        if rec.get("date") == date_str and rec.get("department") == dept and rec.get("section") == sec:
            return rec
    return None

def save_or_update_attendance(date_str: str, dept: str, sec: str, records: Dict[str, str], recorded_by: str) -> bool:
    """
    Saves or updates attendance for a specific date, department, and section.
    """
    attendance_list = get_attendance()
    existing_index = -1
    for i, rec in enumerate(attendance_list):
        if rec.get("date") == date_str and rec.get("department") == dept and rec.get("section") == sec:
            existing_index = i
            break
            
    new_record = {
        "date": date_str,
        "department": dept,
        "section": sec,
        "records": records,  # format: {student_id: status}
        "recorded_by": recorded_by
    }
    
    if existing_index != -1:
        attendance_list[existing_index] = new_record
    else:
        attendance_list.append(new_record)
        
    return save_attendance(attendance_list)

# ==========================================
# ANNOUNCEMENT OPERATIONS
# ==========================================
def get_announcements() -> List[Dict[str, Any]]:
    # Return sorted by date descending
    data = _load_data("announcements")
    try:
        return sorted(data, key=lambda x: x.get("date", ""), reverse=True)
    except Exception:
        return data

def save_announcements(announcements: List[Dict[str, Any]]) -> bool:
    return _save_data("announcements", announcements)

def add_announcement(announcement_data: Dict[str, Any]) -> bool:
    announcements = _load_data("announcements")
    # Generate auto-incrementing ID
    max_id = 0
    for a in announcements:
        try:
            val = int(a.get("id", 0))
            if val > max_id:
                max_id = val
        except Exception:
            pass
    announcement_data["id"] = str(max_id + 1)
    announcements.append(announcement_data)
    return save_announcements(announcements)

def update_announcement(announcement_id: str, updated_data: Dict[str, Any]) -> bool:
    announcements = _load_data("announcements")
    for i, a in enumerate(announcements):
        if a.get("id") == announcement_id:
            updated_data["id"] = announcement_id
            announcements[i] = updated_data
            return save_announcements(announcements)
    return False

def delete_announcement(announcement_id: str) -> bool:
    announcements = _load_data("announcements")
    new_ann = [a for a in announcements if a.get("id") != announcement_id]
    if len(new_ann) == len(announcements):
        return False
    return save_announcements(new_ann)

# ==========================================
# NOTICE BOARD OPERATIONS
# ==========================================
def get_notices() -> List[Dict[str, Any]]:
    # Return sorted by date descending
    data = _load_data("notices")
    try:
        return sorted(data, key=lambda x: x.get("date", ""), reverse=True)
    except Exception:
        return data

def save_notices(notices: List[Dict[str, Any]]) -> bool:
    return _save_data("notices", notices)

def add_notice(notice_data: Dict[str, Any]) -> bool:
    notices = _load_data("notices")
    # Generate auto-incrementing ID
    max_id = 0
    for n in notices:
        try:
            val = int(n.get("id", 0))
            if val > max_id:
                max_id = val
        except Exception:
            pass
    notice_data["id"] = str(max_id + 1)
    notices.append(notice_data)
    return save_notices(notices)

def update_notice(notice_id: str, updated_data: Dict[str, Any]) -> bool:
    notices = _load_data("notices")
    for i, n in enumerate(notices):
        if n.get("id") == notice_id:
            updated_data["id"] = notice_id
            notices[i] = updated_data
            return save_notices(notices)
    return False

def delete_notice(notice_id: str) -> bool:
    notices = _load_data("notices")
    new_notices = [n for n in notices if n.get("id") != notice_id]
    if len(new_notices) == len(notices):
        return False
    return save_notices(new_notices)

# Run initialization when module loaded
init_db()
