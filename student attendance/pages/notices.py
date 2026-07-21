import os
import sys
# Resolve local package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import time
from datetime import date as dt_date, datetime
from utils.auth import get_current_user
from utils.database import (
    get_notices, add_notice, update_notice, delete_notice
)
from utils.styles import render_notice_item

# Authentication check
user = get_current_user()
if not user:
    st.warning("Please login first.")
    st.stop()

st.title("📌 Notice Board")
st.markdown("---")

role = user.get("role", "Faculty")
notices = get_notices()

# Set up tabs depending on role
if role == "Admin":
    tab_view, tab_create, tab_edit = st.tabs(["🔍 View Notices", "➕ Create Notice", "✏️ Edit Notice"])
else:
    tab_view = st.tabs(["🔍 View Notices"])[0]

# ----------------------------------------------------
# TAB 1: VIEW NOTICES
# ----------------------------------------------------
with tab_view:
    st.subheader("General Notices")
    
    if not notices:
        st.info("No notices posted on the board yet.")
    else:
        for n in notices:
            n_id = n.get("id")
            n_title = n.get("title")
            n_content = n.get("content")
            n_date = n.get("date")
            n_author = n.get("author", "Admin")
            
            render_notice_item(
                title=n_title,
                content=n_content,
                date_str=n_date,
                author=n_author
            )
            
            if role == "Admin":
                col_btn1, col_btn2, _ = st.columns([1, 1, 6])
                with col_btn1:
                    if st.button("Edit", key=f"edit_not_{n_id}"):
                        st.session_state["edit_notice_id"] = n_id
                        st.info("Navigate to the 'Edit Notice' tab to modify details.")
                        st.toast(f"Editing: {n_title}")
                with col_btn2:
                    confirm_del = st.checkbox("Confirm Delete", key=f"del_chk_not_{n_id}")
                    if confirm_del:
                        if st.button("Delete Now", key=f"del_btn_not_{n_id}", type="primary"):
                            if delete_notice(n_id):
                                st.success("Notice deleted successfully.")
                                st.toast("Notice deleted")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Failed to delete notice.")
            st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# ADMIN ONLY: CREATE NOTICE
# ----------------------------------------------------
if role == "Admin":
    with tab_create:
        st.subheader("Post a New Notice")
        
        with st.form("create_notice_form", clear_on_submit=True):
            title = st.text_input("Notice Title", placeholder="e.g. System Maintenance Work").strip()
            content = st.text_area("Content Details", placeholder="Enter notice content here...").strip()
            
            # st.date_input returns datetime.date object — use .strftime()
            notice_date = st.date_input("Notice Date", value=dt_date.today())
            notice_date_str = notice_date.strftime("%Y-%m-%d")
            
            submit_btn = st.form_submit_button("Post Notice")
            
            if submit_btn:
                if not title or not content:
                    st.error("Title and Content fields are required.")
                else:
                    new_notice = {
                        "title": title,
                        "content": content,
                        "date": notice_date_str,
                        "author": user["username"]
                    }
                    if add_notice(new_notice):
                        st.success("Notice posted successfully!")
                        st.toast("Notice Posted")
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error("Failed to post notice.")

    # ----------------------------------------------------
    # ADMIN ONLY: EDIT NOTICE
    # ----------------------------------------------------
    with tab_edit:
        st.subheader("Edit Notice Details")
        
        edit_not_id = st.session_state.get("edit_notice_id")
        
        if not edit_not_id:
            st.info("Please select a notice to edit from the 'View Notices' tab and click 'Edit'.")
        else:
            notice_to_edit = None
            for n in notices:
                if n.get("id") == edit_not_id:
                    notice_to_edit = n
                    break
                    
            if not notice_to_edit:
                st.error("Notice not found.")
            else:
                with st.form("edit_notice_form"):
                    edit_title = st.text_input("Title", value=notice_to_edit["title"]).strip()
                    edit_content = st.text_area("Content Details", value=notice_to_edit["content"]).strip()
                    
                    try:
                        # Parse stored date string back to datetime.date for the widget
                        parsed_date = datetime.strptime(notice_to_edit["date"], "%Y-%m-%d").date()
                    except Exception:
                        parsed_date = dt_date.today()
                        
                    edit_date = st.date_input("Notice Date", value=parsed_date)
                    edit_date_str = edit_date.strftime("%Y-%m-%d")
                    
                    col_edit_btns = st.columns(2)
                    with col_edit_btns[0]:
                        save_btn = st.form_submit_button("Save Changes", use_container_width=True)
                    with col_edit_btns[1]:
                        cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
                        
                    if save_btn:
                        if not edit_title or not edit_content:
                            st.error("Title and Content fields are required.")
                        else:
                            updated_notice = {
                                "id": edit_not_id,
                                "title": edit_title,
                                "content": edit_content,
                                "date": edit_date_str,
                                "author": notice_to_edit.get("author", user["username"])
                            }
                            if update_notice(edit_not_id, updated_notice):
                                st.success("Notice updated successfully!")
                                st.toast("Notice updated")
                                st.session_state["edit_notice_id"] = None
                                time.sleep(1.0)
                                st.rerun()
                            else:
                                st.error("Failed to update notice.")
                                
                    if cancel_btn:
                        st.session_state["edit_notice_id"] = None
                        st.info("Edit cancelled.")
                        st.rerun()
