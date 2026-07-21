import os
import sys
import time
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from utils.auth import get_current_user
from utils.database import (
    get_students, add_student, update_student, delete_student
)

# Authentication check
user = get_current_user()
if not user:
    st.warning("Please login first.")
    st.stop()

st.title("👥 Student Management")
st.markdown("---")

# Load existing students
students = get_students()
df_students = pd.DataFrame(students)

# Ensure database is not empty of columns for rendering
if df_students.empty:
    df_students = pd.DataFrame(columns=[
        "student_id", "name", "department", "year", "section", "email", "phone"
    ])

# Rename columns for cleaner display
df_display = df_students.rename(columns={
    "student_id": "Student ID",
    "name": "Name",
    "department": "Department",
    "year": "Year",
    "section": "Section",
    "email": "Email",
    "phone": "Phone"
})

# Sidebar/Top layout tabs
tab_view, tab_add, tab_edit = st.tabs(["🔍 View Students", "➕ Add Student", "✏️ Edit Student"])

# ----------------------------------------------------
# TAB 1: VIEW STUDENTS
# ----------------------------------------------------
with tab_view:
    st.subheader("Student Directory")
    
    if len(students) == 0:
        st.info("No students found. Use the 'Add Student' tab to add records.")
    else:
        # Search and filter options
        col_search, col_dept, col_sort = st.columns([2, 1, 1])
        
        with col_search:
            search_query = st.text_input("Search Student", placeholder="Search by Name or ID...").strip()
            
        with col_dept:
            depts = ["All"] + sorted(list(df_display["Department"].unique()))
            dept_filter = st.selectbox("Filter Department", depts)
            
        with col_sort:
            sort_by = st.selectbox("Sort By", ["Student ID", "Name", "Department"])
            
        # Apply filters
        filtered_df = df_display.copy()
        
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Name"].str.contains(search_query, case=False, na=False) |
                filtered_df["Student ID"].str.contains(search_query, case=False, na=False)
            ]
            
        if dept_filter != "All":
            filtered_df = filtered_df[filtered_df["Department"] == dept_filter]
            
        # Apply sorting
        filtered_df = filtered_df.sort_values(by=sort_by)
        
        # Display Table with row selection
        st.write("💡 *Tip: Select a row in the table to Edit or Delete that student.*")
        
        # Streamlit table rendering with selection
        select_event = st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single_row"
        )
        
        selected_rows = select_event.get("selection", {}).get("rows", [])
        
        if selected_rows:
            selected_idx = selected_rows[0]
            selected_student_id = filtered_df.iloc[selected_idx]["Student ID"]
            selected_student_name = filtered_df.iloc[selected_idx]["Name"]
            
            st.markdown(f"""
            <div style="background-color: #f1f5f9; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #1d4ed8;">
                Selected Student: <strong>{selected_student_name} (ID: {selected_student_id})</strong>
            </div>
            """, unsafe_allow_html=True)
            
            col_actions_edit, col_actions_del, _ = st.columns([1, 1, 3])
            
            with col_actions_edit:
                if st.button("Edit Details", use_container_width=True):
                    st.session_state["edit_student_id"] = selected_student_id
                    st.info("Navigate to the 'Edit Student' tab to modify details.")
                    st.toast(f"Editing {selected_student_name}")
                    
            with col_actions_del:
                # Custom confirmation dialog inside page
                confirm_delete = st.checkbox("Confirm Delete", key="delete_chk")
                if confirm_delete:
                    if st.button("Delete Student Now", type="primary", use_container_width=True):
                        if delete_student(selected_student_id):
                            st.success(f"Deleted student {selected_student_name} successfully.")
                            st.toast("Student deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete student.")

# ----------------------------------------------------
# TAB 2: ADD STUDENT
# ----------------------------------------------------
with tab_add:
    st.subheader("Add New Student")
    
    with st.form("add_student_form", clear_on_submit=True):
        col_id, col_name = st.columns(2)
        with col_id:
            s_id = st.text_input("Student ID (Unique)", placeholder="e.g. STU1001").strip()
        with col_name:
            s_name = st.text_input("Full Name", placeholder="e.g. Alice Smith").strip()
            
        col_dept_input, col_year, col_sec = st.columns([2, 1, 1])
        with col_dept_input:
            s_dept = st.selectbox("Department", [
                "Computer Science", "Information Technology", 
                "Electrical Engineering", "Electronics & Comm",
                "Mechanical Engineering", "Civil Engineering", 
                "Business Administration"
            ])
        with col_year:
            s_year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        with col_sec:
            s_sec = st.selectbox("Section", ["A", "B", "C", "D"])
            
        col_email, col_phone = st.columns(2)
        with col_email:
            s_email = st.text_input("Email Address", placeholder="e.g. alice@school.edu").strip()
        with col_phone:
            s_phone = st.text_input("Phone Number", placeholder="e.g. +1234567890").strip()
            
        submit_add = st.form_submit_button("Save Student")
        
        if submit_add:
            if not s_id or not s_name or not s_email or not s_phone:
                st.error("All fields are required.")
            else:
                student_data = {
                    "student_id": s_id,
                    "name": s_name,
                    "department": s_dept,
                    "year": s_year,
                    "section": s_sec,
                    "email": s_email,
                    "phone": s_phone
                }
                
                success = add_student(student_data)
                if success:
                    st.success(f"Student {s_name} added successfully!")
                    st.toast(f"Added {s_name}")
                    st.rerun()
                else:
                    st.error("Duplicate Student ID. Student ID must be unique.")

# ----------------------------------------------------
# TAB 3: EDIT STUDENT
# ----------------------------------------------------
with tab_edit:
    st.subheader("Edit Student Details")
    
    # Check if student selected in session state
    edit_student_id = st.session_state.get("edit_student_id")
    
    if not edit_student_id:
        st.info("Please select a student row from the 'View Students' tab, click 'Edit Details', and then update details here.")
    else:
        # Load specific student
        students_current = get_students()
        student_to_edit = None
        for s in students_current:
            if s.get("student_id") == edit_student_id:
                student_to_edit = s
                break
                
        if not student_to_edit:
            st.error("Selected student not found in database.")
        else:
            st.markdown(f"Editing Student ID: **{edit_student_id}**")
            
            with st.form("edit_student_form"):
                # Student ID is read-only during edit to maintain references
                st.text_input("Student ID (Read-only)", value=student_to_edit["student_id"], disabled=True)
                
                edit_name = st.text_input("Full Name", value=student_to_edit["name"]).strip()
                
                col_edit_dept, col_edit_yr, col_edit_sec = st.columns([2, 1, 1])
                
                depts_list = [
                    "Computer Science", "Information Technology", 
                    "Electrical Engineering", "Electronics & Comm",
                    "Mechanical Engineering", "Civil Engineering", 
                    "Business Administration"
                ]
                dept_index = depts_list.index(student_to_edit["department"]) if student_to_edit["department"] in depts_list else 0
                
                with col_edit_dept:
                    edit_dept = st.selectbox("Department", depts_list, index=dept_index)
                    
                years_list = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
                yr_index = years_list.index(student_to_edit["year"]) if student_to_edit["year"] in years_list else 0
                
                with col_edit_yr:
                    edit_year = st.selectbox("Year", years_list, index=yr_index)
                    
                sections_list = ["A", "B", "C", "D"]
                sec_index = sections_list.index(student_to_edit["section"]) if student_to_edit["section"] in sections_list else 0
                
                with col_edit_sec:
                    edit_section = st.selectbox("Section", sections_list, index=sec_index)
                    
                col_edit_email, col_edit_phone = st.columns(2)
                with col_edit_email:
                    edit_email = st.text_input("Email Address", value=student_to_edit["email"]).strip()
                with col_edit_phone:
                    edit_phone = st.text_input("Phone Number", value=student_to_edit["phone"]).strip()
                    
                col_edit_btns = st.columns(2)
                with col_edit_btns[0]:
                    save_changes = st.form_submit_button("Save Changes", use_container_width=True)
                with col_edit_btns[1]:
                    cancel_edit = st.form_submit_button("Cancel", use_container_width=True)
                    
                if save_changes:
                    if not edit_name or not edit_email or not edit_phone:
                        st.error("Name, email, and phone number fields cannot be empty.")
                    else:
                        updated_student = {
                            "student_id": edit_student_id,
                            "name": edit_name,
                            "department": edit_dept,
                            "year": edit_year,
                            "section": edit_section,
                            "email": edit_email,
                            "phone": edit_phone
                        }
                        if update_student(edit_student_id, updated_student):
                            st.success(f"Updated {edit_name} successfully!")
                            st.toast("Student details updated")
                            # Reset selection state
                            st.session_state["edit_student_id"] = None
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error("Failed to update student details.")
                            
                if cancel_edit:
                    st.session_state["edit_student_id"] = None
                    st.info("Edit cancelled.")
                    st.rerun()
