import os
import sys
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import time
from datetime import date as dt_date, datetime
from utils.auth import get_current_user
from utils.database import (
    get_announcements, add_announcement, update_announcement, delete_announcement
)
from utils.styles import render_announcement_item

# Authentication check
user = get_current_user()
if not user:
    st.warning("Please login first.")
    st.stop()

st.title("📢 Announcements")
st.markdown("---")

role = user.get("role", "Faculty")
announcements = get_announcements()

# Set up tabs depending on role
if role == "Admin":
    tab_view, tab_create, tab_edit = st.tabs(["🔍 View Announcements", "➕ Create Announcement", "✏️ Edit Announcement"])
else:
    tab_view = st.tabs(["🔍 View Announcements"])[0]

# ----------------------------------------------------
# TAB 1: VIEW ANNOUNCEMENTS
# ----------------------------------------------------
with tab_view:
    st.subheader("All Announcements")
    
    if not announcements:
        st.info("No announcements posted yet.")
    else:
        for a in announcements:
            a_id = a.get("id")
            a_title = a.get("title")
            a_desc = a.get("description")
            a_date = a.get("date")
            a_priority = a.get("priority", "Medium")
            a_author = a.get("author", "Admin")
            
            render_announcement_item(
                title=a_title,
                description=a_desc,
                date_str=a_date,
                priority=a_priority,
                author=a_author
            )
            
            if role == "Admin":
                col_btn1, col_btn2, _ = st.columns([1, 1, 6])
                with col_btn1:
                    if st.button("Edit", key=f"edit_ann_{a_id}"):
                        st.session_state["edit_announcement_id"] = a_id
                        st.info("Navigate to the 'Edit Announcement' tab to modify details.")
                        st.toast(f"Editing: {a_title}")
                with col_btn2:
                    confirm_del = st.checkbox("Confirm Delete", key=f"del_chk_ann_{a_id}")
                    if confirm_del:
                        if st.button("Delete Now", key=f"del_btn_ann_{a_id}", type="primary"):
                            if delete_announcement(a_id):
                                st.success("Announcement deleted successfully.")
                                st.toast("Announcement deleted")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Failed to delete.")
            st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# ADMIN ONLY: CREATE ANNOUNCEMENT
# ----------------------------------------------------
if role == "Admin":
    with tab_create:
        st.subheader("Create Announcement")
        
        with st.form("create_announcement_form", clear_on_submit=True):
            title = st.text_input("Title", placeholder="e.g. Midterm Exams Schedule").strip()
            description = st.text_area("Description/Body", placeholder="Enter announcement content...").strip()
            
            col_date, col_priority = st.columns(2)
            with col_date:
                # st.date_input returns a datetime.date object
                ann_date = st.date_input("Date", value=dt_date.today())
                ann_date_str = ann_date.strftime("%Y-%m-%d")
            with col_priority:
                priority = st.selectbox("Priority Level", ["Low", "Medium", "High"])
                
            submit_btn = st.form_submit_button("Post Announcement")
            
            if submit_btn:
                if not title or not description:
                    st.error("Title and Description are required.")
                else:
                    new_ann = {
                        "title": title,
                        "description": description,
                        "date": ann_date_str,
                        "priority": priority,
                        "author": user["username"]
                    }
                    if add_announcement(new_ann):
                        st.success("Announcement posted successfully!")
                        st.toast("Announcement Posted")
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error("Failed to post announcement.")

    # ----------------------------------------------------
    # ADMIN ONLY: EDIT ANNOUNCEMENT
    # ----------------------------------------------------
    with tab_edit:
        st.subheader("Edit Announcement Details")
        
        edit_ann_id = st.session_state.get("edit_announcement_id")
        
        if not edit_ann_id:
            st.info("Please select an announcement to edit from the 'View Announcements' tab and click 'Edit'.")
        else:
            announcement_to_edit = None
            for a in announcements:
                if a.get("id") == edit_ann_id:
                    announcement_to_edit = a
                    break
                    
            if not announcement_to_edit:
                st.error("Announcement not found.")
            else:
                with st.form("edit_announcement_form"):
                    edit_title = st.text_input("Title", value=announcement_to_edit["title"]).strip()
                    edit_desc = st.text_area("Description/Body", value=announcement_to_edit["description"]).strip()
                    
                    col_edit_date, col_edit_prio = st.columns(2)
                    with col_edit_date:
                        try:
                            # Parse stored date string to datetime.date
                            parsed_date = datetime.strptime(announcement_to_edit["date"], "%Y-%m-%d").date()
                        except Exception:
                            parsed_date = dt_date.today()
                        
                        edit_date = st.date_input("Date", value=parsed_date)
                        edit_date_str = edit_date.strftime("%Y-%m-%d")
                        
                    with col_edit_prio:
                        prio_list = ["Low", "Medium", "High"]
                        prio_idx = prio_list.index(announcement_to_edit["priority"]) if announcement_to_edit["priority"] in prio_list else 0
                        edit_priority = st.selectbox("Priority Level", prio_list, index=prio_idx)
                        
                    col_edit_btns = st.columns(2)
                    with col_edit_btns[0]:
                        save_btn = st.form_submit_button("Save Changes", use_container_width=True)
                    with col_edit_btns[1]:
                        cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
                        
                    if save_btn:
                        if not edit_title or not edit_desc:
                            st.error("Title and Description fields are required.")
                        else:
                            updated_ann = {
                                "id": edit_ann_id,
                                "title": edit_title,
                                "description": edit_desc,
                                "date": edit_date_str,
                                "priority": edit_priority,
                                "author": announcement_to_edit.get("author", user["username"])
                            }
                            if update_announcement(edit_ann_id, updated_ann):
                                st.success("Announcement updated successfully!")
                                st.toast("Announcement updated")
                                st.session_state["edit_announcement_id"] = None
                                time.sleep(1.0)
                                st.rerun()
                            else:
                                st.error("Failed to update announcement.")
                                
                    if cancel_btn:
                        st.session_state["edit_announcement_id"] = None
                        st.info("Edit cancelled.")
                        st.rerun()
