import os
import sys
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import date
from utils.auth import get_current_user
from utils.database import get_students, get_attendance_record, save_or_update_attendance

# Authentication check
user = get_current_user()
if not user:
    st.warning("Please login first.")
    st.stop()

st.title("✅ Record Attendance")
st.markdown("---")

# Selection Filters
col_date, col_dept, col_sec = st.columns(3)

with col_date:
    selected_date = st.date_input("Attendance Date", value=date.today())
    date_str = selected_date.strftime("%Y-%m-%d")
    
with col_dept:
    departments = [
        "Computer Science", "Information Technology", 
        "Electrical Engineering", "Electronics & Comm",
        "Mechanical Engineering", "Civil Engineering", 
        "Business Administration"
    ]
    selected_dept = st.selectbox("Department", departments)
    
with col_sec:
    sections = ["A", "B", "C", "D"]
    selected_sec = st.selectbox("Section", sections)

st.markdown("<br>", unsafe_allow_html=True)

# Fetch students for selected department and section
all_students = get_students()
filtered_students = [
    s for s in all_students 
    if s.get("department") == selected_dept and s.get("section") == selected_sec
]

if not filtered_students:
    st.info(f"No students found in {selected_dept} - Section {selected_sec}. Please add students to this section first.")
else:
    # Check if attendance is already recorded
    existing_record = get_attendance_record(date_str, selected_dept, selected_sec)
    
    if existing_record:
        st.warning(f"⚠️ Attendance has already been recorded for this date. Saving changes will overwrite the existing records.")
        existing_statuses = existing_record.get("records", {})
    else:
        st.info("💡 Recording new attendance for this class.")
        existing_statuses = {}
        
    st.subheader(f"Student List ({len(filtered_students)} Students)")
    
    # Bulk actions row
    col_bulk_p, col_bulk_a, _ = st.columns([1, 1, 3])
    
    # Initialize bulk toggle in session state if not set
    bulk_key = f"bulk_state_{selected_dept}_{selected_sec}_{date_str}"
    if bulk_key not in st.session_state:
        st.session_state[bulk_key] = None
        
    with col_bulk_p:
        if st.button("Mark All Present", use_container_width=True):
            st.session_state[bulk_key] = "Present"
            st.toast("Marked all as Present")
            
    with col_bulk_a:
        if st.button("Mark All Absent", use_container_width=True):
            st.session_state[bulk_key] = "Absent"
            st.toast("Marked all as Absent")
            
    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
    
    # Header Row
    col_h_id, col_h_name, col_h_status = st.columns([1, 2, 1])
    with col_h_id:
        st.markdown("**Student ID**")
    with col_h_name:
        st.markdown("**Name**")
    with col_h_status:
        st.markdown("**Attendance Status**")
        
    st.markdown("<hr style='margin: 0.25rem 0; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
    
    # Attendance selection records dictionary
    attendance_selections = {}
    
    # Render student rows
    for index, student in enumerate(filtered_students):
        s_id = student["student_id"]
        s_name = student["name"]
        
        # Decide default check status
        # 1. Bulk toggle overrides
        if st.session_state[bulk_key] == "Present":
            default_val = True
        elif st.session_state[bulk_key] == "Absent":
            default_val = False
        # 2. Existing record load
        elif s_id in existing_statuses:
            default_val = (existing_statuses[s_id] == "Present")
        # 3. Default to Present
        else:
            default_val = True
            
        col_id, col_name, col_status = st.columns([1, 2, 1])
        
        with col_id:
            st.write(s_id)
        with col_name:
            st.write(s_name)
        with col_status:
            # Checkbox key must be unique per date/class/student
            cb_key = f"chk_{s_id}_{date_str}_{selected_dept}_{selected_sec}_{index}"
            is_present = st.checkbox("Present", value=default_val, key=cb_key)
            attendance_selections[s_id] = "Present" if is_present else "Absent"
            
        st.markdown("<hr style='margin: 0.1rem 0; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Save button
    if st.button("Save Attendance Record", type="primary", use_container_width=True):
        success = save_or_update_attendance(
            date_str=date_str,
            dept=selected_dept,
            sec=selected_sec,
            records=attendance_selections,
            recorded_by=user["username"]
        )
        if success:
            st.success("Attendance saved successfully!")
            st.toast("Attendance Saved", icon="✅")
            # Clear bulk state
            if bulk_key in st.session_state:
                del st.session_state[bulk_key]
        else:
            st.error("Failed to save attendance record.")
