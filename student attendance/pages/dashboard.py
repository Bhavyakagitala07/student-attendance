import os
import sys
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import get_current_user
from utils.styles import render_kpi_card, render_announcement_item, render_notice_item
from utils.database import get_announcements, get_notices
from utils.attendance_utils import (
    calculate_dashboard_stats,
    get_attendance_pie_data,
    get_dept_attendance_bar_data,
    get_attendance_line_trend_data,
    get_recent_activities
)

# Authentication check
user = get_current_user()
if not user:
    st.warning("Please login first.")
    st.stop()

st.title(f"📊 Dashboard")
st.write(f"Welcome back, **{user['fullname']}** ({user['role']})")
st.markdown("---")

# 1. KPI CARDS SECTION
stats = calculate_dashboard_stats()

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    render_kpi_card(
        title="Total Students",
        value=str(stats["total_students"]),
        icon="👥",
        color_type="blue"
    )
    
with col_kpi2:
    status_label = "Present Today"
    value_label = str(stats["today_present"])
    render_kpi_card(
        title=status_label,
        value=value_label,
        icon="✅",
        color_type="green"
    )
    
with col_kpi3:
    status_label = "Absent Today"
    value_label = str(stats["today_absent"])
    render_kpi_card(
        title=status_label,
        value=value_label,
        icon="❌",
        color_type="red"
    )
    
with col_kpi4:
    rate_val = f"{stats['today_percentage']}%" if stats["has_attendance_today"] else "N/A"
    render_kpi_card(
        title="Today's Attendance Rate",
        value=rate_val,
        icon="📈",
        color_type="purple"
    )

st.markdown("<br>", unsafe_allow_html=True)

# 2. MAIN LAYOUT
# Left side: Charts, Right side: Quick actions & Feeds
col_left, col_right = st.columns([5, 3], gap="large")

with col_left:
    st.subheader("Attendance Analytics")
    
    # Render Plotly Charts
    chart_tabs = st.tabs(["Daily Distribution", "Performance by Dept", "Attendance Trend"])
    
    with chart_tabs[0]:
        pie_labels, pie_values = get_attendance_pie_data()
        if sum(pie_values) == 0:
            st.info("No attendance data available to display pie chart.")
        else:
            pie_df = pd.DataFrame({"Status": pie_labels, "Students": pie_values})
            fig_pie = px.pie(
                pie_df,
                values="Students",
                names="Status",
                color="Status",
                color_discrete_map={"Present": "#16a34a", "Absent": "#dc2626"},
                hole=0.4,
                title="Status Breakdown"
            )
            fig_pie.update_layout(height=350, margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with chart_tabs[1]:
        bar_df = get_dept_attendance_bar_data()
        if bar_df.empty:
            st.info("No attendance data available to display department chart.")
        else:
            fig_bar = px.bar(
                bar_df,
                x="Department",
                y="Attendance %",
                color="Department",
                title="Attendance % by Department",
                text="Attendance %"
            )
            fig_bar.update_layout(showlegend=False, height=350, yaxis_range=[0, 105])
            fig_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)
            
    with chart_tabs[2]:
        line_df = get_attendance_line_trend_data()
        if line_df.empty:
            st.info("No historical trends to show.")
        else:
            fig_line = px.line(
                line_df,
                x="Date",
                y="Attendance %",
                markers=True,
                title="Daily Attendance Trend"
            )
            fig_line.update_layout(height=350, yaxis_range=[0, 105])
            st.plotly_chart(fig_line, use_container_width=True)
            
    # Recent Activities Feed
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Recent System Activities")
    activities = get_recent_activities(limit=4)
    if not activities:
        st.info("No recent activities recorded.")
    else:
        for act in activities:
            st.markdown(f"""
            <div style="background-color: white; padding: 0.8rem 1rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 1.1rem; margin-right: 0.5rem;">📝</span>
                    <span style="color: #334155; font-weight: 500;">{act['message']}</span>
                </div>
                <div style="font-size: 0.8rem; color: #94a3b8;">
                    <span>{act['date']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("Quick Actions")
    
    # Layout action grid
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("👥 Add Student", use_container_width=True):
            st.switch_page("pages/students.py")
        if st.button("📅 Attendance History", use_container_width=True):
            st.switch_page("pages/history.py")
    with col_act2:
        if st.button("✅ Take Attendance", use_container_width=True):
            st.switch_page("pages/attendance.py")
        if st.button("👤 View Profile", use_container_width=True):
            st.switch_page("pages/profile.py")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Latest notices card panel
    st.subheader("Latest Notices")
    notices = get_notices()
    if not notices:
        st.info("No notices posted.")
    else:
        for n in notices[:2]:
            render_notice_item(
                title=n.get("title"),
                content=n.get("content")[:80] + "..." if len(n.get("content", "")) > 80 else n.get("content"),
                date_str=n.get("date"),
                author=n.get("author", "System")
            )
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Latest Announcements
    st.subheader("Recent Announcements")
    anns = get_announcements()
    if not anns:
        st.info("No announcements.")
    else:
        for a in anns[:2]:
            render_announcement_item(
                title=a.get("title"),
                description=a.get("description")[:80] + "..." if len(a.get("description", "")) > 80 else a.get("description"),
                date_str=a.get("date"),
                priority=a.get("priority", "Medium"),
                author=a.get("author", "Admin")
            )
