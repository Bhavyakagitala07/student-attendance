import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, List, Tuple, Optional
from utils.database import get_students, get_attendance

def get_today_date_str() -> str:
    """
    Returns today's date in YYYY-MM-DD format.
    """
    return date.today().strftime("%Y-%m-%d")

def calculate_dashboard_stats() -> Dict[str, Any]:
    """
    Calculates key metrics for the dashboard home screen:
    - Total Students
    - Today's Attendance (Present, Absent, Percentage)
    """
    students = get_students()
    total_students = len(students)
    
    today_str = get_today_date_str()
    attendance_records = get_attendance()
    
    # Filter for today's records
    today_records = [r for r in attendance_records if r.get("date") == today_str]
    
    today_present = 0
    today_absent = 0
    
    for record in today_records:
        for status in record.get("records", {}).values():
            if status == "Present":
                today_present += 1
            elif status == "Absent":
                today_absent += 1
                
    total_recorded_today = today_present + today_absent
    percentage_today = 0.0
    if total_recorded_today > 0:
        percentage_today = round((today_present / total_recorded_today) * 100, 1)
        
    return {
        "total_students": total_students,
        "today_present": today_present,
        "today_absent": today_absent,
        "today_percentage": percentage_today,
        "has_attendance_today": total_recorded_today > 0
    }

def get_attendance_pie_data() -> Tuple[List[str], List[int]]:
    """
    Returns data for the attendance status pie chart.
    If no attendance today, it returns overall historical attendance.
    """
    records = get_attendance()
    today_str = get_today_date_str()
    
    # Check if we have today's data
    today_records = [r for r in records if r.get("date") == today_str]
    active_records = today_records if today_records else records
    
    present = 0
    absent = 0
    for r in active_records:
        for status in r.get("records", {}).values():
            if status == "Present":
                present += 1
            elif status == "Absent":
                absent += 1
                
    if present == 0 and absent == 0:
        # Default placeholder data so chart doesn't break
        return ["Present", "Absent"], [0, 0]
        
    return ["Present", "Absent"], [present, absent]

def get_dept_attendance_bar_data() -> pd.DataFrame:
    """
    Calculates attendance percentage grouped by department.
    Returns a pandas DataFrame with columns ['Department', 'Attendance %']
    """
    records = get_attendance()
    if not records:
        return pd.DataFrame(columns=["Department", "Attendance %"])
        
    dept_stats = {}  # {dept: {"present": 0, "total": 0}}
    
    for r in records:
        dept = r.get("department", "Unknown")
        if dept not in dept_stats:
            dept_stats[dept] = {"present": 0, "total": 0}
            
        for status in r.get("records", {}).values():
            dept_stats[dept]["total"] += 1
            if status == "Present":
                dept_stats[dept]["present"] += 1
                
    data = []
    for dept, stats in dept_stats.items():
        percentage = 0.0
        if stats["total"] > 0:
            percentage = round((stats["present"] / stats["total"]) * 100, 1)
        data.append({"Department": dept, "Attendance %": percentage})
        
    return pd.DataFrame(data)

def get_attendance_line_trend_data() -> pd.DataFrame:
    """
    Calculates overall daily attendance percentage trends over time.
    Returns a pandas DataFrame with columns ['Date', 'Attendance %'] sorted by Date.
    """
    records = get_attendance()
    if not records:
        return pd.DataFrame(columns=["Date", "Attendance %"])
        
    daily_stats = {}  # {date_str: {"present": 0, "total": 0}}
    
    for r in records:
        d_str = r.get("date", "")
        if not d_str:
            continue
        if d_str not in daily_stats:
            daily_stats[d_str] = {"present": 0, "total": 0}
            
        for status in r.get("records", {}).values():
            daily_stats[d_str]["total"] += 1
            if status == "Present":
                daily_stats[d_str]["present"] += 1
                
    data = []
    for d_str, stats in daily_stats.items():
        percentage = 0.0
        if stats["total"] > 0:
            percentage = round((stats["present"] / stats["total"]) * 100, 1)
        data.append({"Date": d_str, "Attendance %": percentage})
        
    df = pd.DataFrame(data)
    if not df.empty:
        # Sort by actual date values
        df["Date_Parsed"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date_Parsed").drop(columns=["Date_Parsed"])
    return df

def get_recent_activities(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Gathers recent system activities:
    - New student registrations
    - Attendance records taken
    - Notices posted
    Returns a list of activity items sorted by time.
    """
    activities = []
    
    # 1. Attendance events
    attendance_records = get_attendance()
    for rec in attendance_records:
        activities.append({
            "type": "attendance",
            "message": f"Attendance recorded for {rec['department']} - Section {rec['section']}",
            "date": rec.get("date", ""),
            "author": rec.get("recorded_by", "System"),
            "sort_key": rec.get("date", "")
        })
        
    # Since JSON objects don't store high-resolution creation timestamps,
    # we sort using dates.
    try:
        activities = sorted(activities, key=lambda x: x["sort_key"], reverse=True)
    except Exception:
        pass
        
    return activities[:limit]

def generate_attendance_report(date_filter: Optional[Any] = None, 
                              dept_filter: Optional[str] = None, 
                              student_id_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generates a filtered list of flat attendance records for rendering/export.
    """
    records = get_attendance()
    students_list = get_students()
    
    # Create mapping of student ID to full details
    student_map = {s["student_id"]: s for s in students_list}
    
    report = []
    
    for r in records:
        r_date = r.get("date")
        r_dept = r.get("department")
        r_sec = r.get("section")
        r_recorded_by = r.get("recorded_by", "")
        
        # Apply date filter
        if date_filter:
            date_filter_str = date_filter.strftime("%Y-%m-%d") if isinstance(date_filter, (date, datetime)) else str(date_filter)
            if r_date != date_filter_str:
                continue
                
        # Apply department filter
        if dept_filter and dept_filter != "All":
            if r_dept != dept_filter:
                continue
                
        for s_id, status in r.get("records", {}).items():
            # Apply student filter
            if student_id_filter and student_id_filter != "All":
                if s_id != student_id_filter:
                    continue
                    
            student_info = student_map.get(s_id, {})
            s_name = student_info.get("name", "Unknown Student")
            s_dept = student_info.get("department", r_dept)
            s_sec = student_info.get("section", r_sec)
            
            report.append({
                "Date": r_date,
                "Student ID": s_id,
                "Name": s_name,
                "Department": s_dept,
                "Section": s_sec,
                "Status": status,
                "Recorded By": r_recorded_by
            })
            
    return report
