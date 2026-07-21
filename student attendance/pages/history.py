import os
import sys
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from utils.auth import get_current_user
from utils.database import get_students
from utils.attendance_utils import generate_attendance_report

# Authentication check
user = get_current_user()
if not user:
    st.warning("Please login first.")
    st.stop()

st.title("📅 Attendance History")
st.markdown("---")

# Filter Section
st.subheader("Filter Attendance Records")
col_date_enable, col_date_picker, col_dept, col_student = st.columns([1, 2, 2, 3])

with col_date_enable:
    st.write("")  # spacing
    st.write("")
    use_date_filter = st.checkbox("Filter Date", value=False)
    
with col_date_picker:
    selected_date = st.date_input("Date", value=date.today(), disabled=not use_date_filter)
    
with col_dept:
    departments = [
        "All", "Computer Science", "Information Technology", 
        "Electrical Engineering", "Electronics & Comm",
        "Mechanical Engineering", "Civil Engineering", 
        "Business Administration"
    ]
    selected_dept = st.selectbox("Department", departments)
    
with col_student:
    students_list = get_students()
    student_opts = ["All"] + [f"{s['student_id']} - {s['name']}" for s in students_list]
    selected_student_raw = st.selectbox("Student", student_opts)
    selected_student_id = selected_student_raw.split(" - ")[0] if selected_student_raw != "All" else "All"

# Search Query Box
search_query = st.text_input("Search student name", placeholder="Enter name...").strip()

# Generate Report based on filters
report_data = generate_attendance_report(
    date_filter=selected_date if use_date_filter else None,
    dept_filter=selected_dept,
    student_id_filter=selected_student_id
)

df_report = pd.DataFrame(report_data)

# Apply Text Search Filter locally on Name column if requested
if not df_report.empty and search_query:
    df_report = df_report[df_report["Name"].str.contains(search_query, case=False, na=False)]

st.markdown("<br>", unsafe_allow_html=True)

if df_report.empty:
    st.info("No attendance records found matching the active filters.")
else:
    # Calculations
    total_records = len(df_report)
    present_records = len(df_report[df_report["Status"] == "Present"])
    absent_records = len(df_report[df_report["Status"] == "Absent"])
    
    attendance_percentage = 0.0
    if total_records > 0:
        attendance_percentage = round((present_records / total_records) * 100, 1)
        
    # Render Stats Cards
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Total Records", total_records)
    with col_stat2:
        st.metric("Present Count", present_records)
    with col_stat3:
        st.metric("Absent Count", absent_records)
    with col_stat4:
        st.metric("Attendance Rate", f"{attendance_percentage}%")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Export Button & Chart Column Split
    col_table, col_chart = st.columns([5, 3], gap="medium")
    
    with col_table:
        st.subheader("Attendance Log Table")
        
        # Display DataFrame
        st.dataframe(df_report, use_container_width=True, hide_index=True)
        
        # CSV Export Trigger
        csv_bytes = df_report.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Report to CSV",
            data=csv_bytes,
            file_name=f"attendance_report_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_chart:
        st.subheader("Attendance Distribution")
        
        # Pie Chart showing present vs absent ratio in the filtered set
        chart_df = pd.DataFrame({
            "Status": ["Present", "Absent"],
            "Count": [present_records, absent_records]
        })
        
        fig = px.pie(
            chart_df,
            values="Count",
            names="Status",
            color="Status",
            color_discrete_map={"Present": "#16a34a", "Absent": "#dc2626"},
            hole=0.4
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
