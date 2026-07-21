"""
EduAttend - Student Attendance Management System
Single-file Streamlit application with session-state routing.
"""
import os
import sys
import time
import hashlib
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date as dt_date, datetime
from typing import Dict, Any, Optional, List, Tuple

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EduAttend – Attendance Management",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_FILES = {
    "users":         os.path.join(DATA_DIR, "users.json"),
    "students":      os.path.join(DATA_DIR, "students.json"),
    "attendance":    os.path.join(DATA_DIR, "attendance.json"),
    "announcements": os.path.join(DATA_DIR, "announcements.json"),
    "notices":       os.path.join(DATA_DIR, "notices.json"),
}

def _ensure_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    for path in DB_FILES.values():
        if not os.path.exists(path):
            _write_json(path, [])
        else:
            try:
                with open(path, "r") as f:
                    txt = f.read().strip()
                if not txt:
                    _write_json(path, [])
                else:
                    json.loads(txt)
            except Exception:
                _write_json(path, [])

def _read_json(path: str) -> list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _write_json(path: str, data: list) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

# ── Users ──────────────────────────────────
def get_users():            return _read_json(DB_FILES["users"])
def save_users(d):          return _write_json(DB_FILES["users"], d)
def get_user(username):     return next((u for u in get_users() if u["username"]==username), None)

# ── Students ───────────────────────────────
def get_students():         return _read_json(DB_FILES["students"])
def save_students(d):       return _write_json(DB_FILES["students"], d)
def get_student(sid):       return next((s for s in get_students() if s["student_id"]==sid), None)

def add_student(data):
    if get_student(data["student_id"]): return False
    students = get_students(); students.append(data); return save_students(students)

def update_student(sid, data):
    students = get_students()
    for i, s in enumerate(students):
        if s["student_id"] == sid:
            data["student_id"] = sid; students[i] = data; return save_students(students)
    return False

def delete_student(sid):
    students = get_students()
    new = [s for s in students if s["student_id"] != sid]
    return save_students(new) if len(new) < len(students) else False

# ── Attendance ─────────────────────────────
def get_attendance():       return _read_json(DB_FILES["attendance"])

def get_att_record(date_s, dept, sec):
    return next((r for r in get_attendance()
                 if r["date"]==date_s and r["department"]==dept and r["section"]==sec), None)

def save_att_record(date_s, dept, sec, records, recorded_by):
    att = get_attendance()
    entry = {"date":date_s,"department":dept,"section":sec,"records":records,"recorded_by":recorded_by}
    for i, r in enumerate(att):
        if r["date"]==date_s and r["department"]==dept and r["section"]==sec:
            att[i] = entry; return _write_json(DB_FILES["attendance"], att)
    att.append(entry); return _write_json(DB_FILES["attendance"], att)

# ── Announcements ──────────────────────────
def get_announcements():
    data = _read_json(DB_FILES["announcements"])
    return sorted(data, key=lambda x: x.get("date",""), reverse=True)

def _next_id(items):
    return str(max((int(x.get("id",0)) for x in items), default=0) + 1)

def add_announcement(data):
    items = _read_json(DB_FILES["announcements"])
    data["id"] = _next_id(items); items.append(data)
    return _write_json(DB_FILES["announcements"], items)

def update_announcement(aid, data):
    items = _read_json(DB_FILES["announcements"])
    for i, a in enumerate(items):
        if a["id"] == aid: data["id"]=aid; items[i]=data; return _write_json(DB_FILES["announcements"], items)
    return False

def delete_announcement(aid):
    items = _read_json(DB_FILES["announcements"])
    new = [a for a in items if a["id"]!=aid]
    return _write_json(DB_FILES["announcements"], new) if len(new)<len(items) else False

# ── Notices ────────────────────────────────
def get_notices():
    data = _read_json(DB_FILES["notices"])
    return sorted(data, key=lambda x: x.get("date",""), reverse=True)

def add_notice(data):
    items = _read_json(DB_FILES["notices"])
    data["id"] = _next_id(items); items.append(data)
    return _write_json(DB_FILES["notices"], items)

def update_notice(nid, data):
    items = _read_json(DB_FILES["notices"])
    for i, n in enumerate(items):
        if n["id"] == nid: data["id"]=nid; items[i]=data; return _write_json(DB_FILES["notices"], items)
    return False

def delete_notice(nid):
    items = _read_json(DB_FILES["notices"])
    new = [n for n in items if n["id"]!=nid]
    return _write_json(DB_FILES["notices"], new) if len(new)<len(items) else False

_ensure_db()

# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────
def hash_pwd(pwd: str, username: str) -> str:
    return hashlib.sha256((pwd + username.lower()).encode()).hexdigest()

def verify_pwd(pwd, username, hashed): return hash_pwd(pwd, username) == hashed

def is_logged_in(): return st.session_state.get("authenticated", False)

def current_user() -> Optional[Dict]:
    return st.session_state.get("user")

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for key, default in [
    ("authenticated", False), ("user", None), ("page", "login"),
    ("edit_student_id", None), ("edit_ann_id", None), ("edit_notice_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important}
.stApp{background:#f0f4f8}
[data-testid="stSidebar"]{background:#0f172a;border-right:1px solid #1e293b}
[data-testid="stSidebar"] *{color:#f1f5f9!important}
div.stButton>button{
    background:linear-gradient(135deg,#1d4ed8,#0f4c81);color:#fff!important;
    border:none;border-radius:8px;padding:.5rem 1.25rem;font-weight:500;
    transition:all .25s ease;box-shadow:0 2px 6px rgba(0,0,0,.15)}
div.stButton>button:hover{transform:translateY(-2px);box-shadow:0 6px 16px rgba(29,78,216,.35)}
.stTextInput input,.stSelectbox select,.stTextArea textarea,.stDateInput input{
    border-radius:8px!important;border:1px solid #cbd5e1!important;background:#fff!important}
.kpi-card{
    background:#fff;border-radius:14px;padding:1.4rem 1.6rem;
    box-shadow:0 2px 8px rgba(0,0,0,.07);border:1px solid #e2e8f0;
    transition:transform .25s,box-shadow .25s;margin-bottom:1rem}
.kpi-card:hover{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.1)}
.kpi-icon{width:48px;height:48px;border-radius:12px;display:flex;
    align-items:center;justify-content:center;font-size:22px;float:left;margin-right:1rem}
.kpi-label{font-size:.75rem;font-weight:600;text-transform:uppercase;
    letter-spacing:.06em;color:#64748b}
.kpi-value{font-size:2rem;font-weight:700;color:#0f172a;line-height:1.1}
.ann-card{background:#fff;border-radius:10px;padding:1rem 1.2rem;
    margin-bottom:.75rem;border-left:4px solid #3b82f6;
    box-shadow:0 1px 4px rgba(0,0,0,.05);transition:transform .2s}
.ann-card:hover{transform:translateX(4px)}
.ann-high{border-left-color:#ef4444}.ann-medium{border-left-color:#f59e0b}.ann-low{border-left-color:#10b981}
.badge{padding:.2rem .65rem;border-radius:999px;font-size:.72rem;font-weight:600;display:inline-block}
.badge-admin{background:#dbeafe;color:#1e40af}
.badge-faculty{background:#f3e8ff;color:#6b21a8}
.badge-present{background:#d1fae5;color:#065f46}
.badge-absent{background:#fee2e2;color:#991b1b}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# NAVIGATION SIDEBAR
# ─────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

with st.sidebar:
    if os.path.exists(logo_path):
        st.image(logo_path, width=220)
    else:
        st.markdown("## 🎓 EduAttend")
    st.markdown("---")

    if is_logged_in():
        u = current_user()
        st.markdown(f"**{u['fullname']}**  \n"
                    f"<span class='badge badge-{'admin' if u['role']=='Admin' else 'faculty'}'>{u['role']}</span>",
                    unsafe_allow_html=True)
        st.markdown("---")
        nav_items = [
            ("📊 Dashboard",          "dashboard"),
            ("👥 Students",           "students"),
            ("✅ Record Attendance",   "attendance"),
            ("📅 Attendance History",  "history"),
            ("📢 Announcements",       "announcements"),
            ("📌 Notice Board",        "notices"),
            ("👤 My Profile",          "profile"),
        ]
        for label, page_key in nav_items:
            active = "background:#1e293b;border-radius:8px;" if st.session_state["page"] == page_key else ""
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state["page"] = page_key
                st.rerun()
    else:
        for label, page_key in [("🔒 Login","login"),("📝 Register","register")]:
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state["page"] = page_key
                st.rerun()

    st.markdown("---")
    st.caption("EduAttend v1.0 • Built with Streamlit")

# ─────────────────────────────────────────────
# HELPER WIDGETS
# ─────────────────────────────────────────────
DEPTS = ["Computer Science","Information Technology","Electrical Engineering",
         "Electronics & Comm","Mechanical Engineering","Civil Engineering","Business Administration"]
YEARS = ["1st Year","2nd Year","3rd Year","4th Year"]
SECS  = ["A","B","C","D"]

def kpi_card(title, value, icon, bg, fg):
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-icon" style="background:{bg};color:{fg}">{icon}</div>
      <div>
        <div class="kpi-label">{title}</div>
        <div class="kpi-value">{value}</div>
      </div>
      <div style="clear:both"></div>
    </div>""", unsafe_allow_html=True)

def ann_card(title, desc, date_s, priority, author):
    cls = f"ann-{priority.lower()}"
    st.markdown(f"""
    <div class="ann-card {cls}">
      <div style="display:flex;justify-content:space-between;font-weight:600;font-size:1rem">
        <span>{title}</span><span class="badge badge-admin">{priority}</span>
      </div>
      <div style="color:#475569;font-size:.875rem;margin-top:.25rem">{desc}</div>
      <div style="color:#94a3b8;font-size:.75rem;margin-top:.4rem;display:flex;justify-content:space-between">
        <span>By {author}</span><span>{date_s}</span>
      </div>
    </div>""", unsafe_allow_html=True)

def notice_card(title, content, date_s, author):
    st.markdown(f"""
    <div class="ann-card" style="border-left-color:#6366f1">
      <div style="font-weight:600;font-size:1rem">{title}</div>
      <div style="color:#475569;font-size:.875rem;margin-top:.25rem">{content}</div>
      <div style="color:#94a3b8;font-size:.75rem;margin-top:.4rem;display:flex;justify-content:space-between">
        <span>By {author}</span><span>{date_s}</span>
      </div>
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: LOGIN
# ─────────────────────────────────────────────
def page_login():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("### 🔒 Sign in to EduAttend")
        st.markdown("---")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            show_pwd = st.checkbox("Show Password")
            password = st.text_input("Password",
                                     type="default" if show_pwd else "password",
                                     placeholder="Enter your password")
            remember = st.checkbox("Remember Me")
            col1, col2 = st.columns(2)
            with col1: submit = st.form_submit_button("Login", use_container_width=True)
            with col2: forgot = st.form_submit_button("Forgot Password?", use_container_width=True)

        if forgot:
            st.info("Please contact your System Administrator to reset your password.")

        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user = get_user(username.strip())
                if not user or not verify_pwd(password, username.strip(), user["password"]):
                    st.error("Invalid username or password.")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = {k: user[k] for k in ("fullname","email","username","role")}
                    st.session_state["page"] = "dashboard"
                    st.success("Login successful!")
                    time.sleep(0.5)
                    st.rerun()

        st.markdown("---")
        if st.button("Don't have an account? Register here →", use_container_width=True):
            st.session_state["page"] = "register"; st.rerun()

# ─────────────────────────────────────────────
# PAGE: REGISTER
# ─────────────────────────────────────────────
def page_register():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("### 📝 Create an Account")
        st.markdown("---")
        with st.form("reg_form", clear_on_submit=True):
            fullname = st.text_input("Full Name", placeholder="e.g. John Doe")
            email    = st.text_input("Email",     placeholder="john@school.edu")
            username = st.text_input("Username",  placeholder="Choose a unique username")
            role     = st.selectbox("Role", ["Faculty", "Admin"])
            password = st.text_input("Password",         type="password", placeholder="Min 6 characters")
            confirm  = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            submit   = st.form_submit_button("Create Account", use_container_width=True)

        if submit:
            errs = []
            if not all([fullname, email, username, password, confirm]): errs.append("All fields are required.")
            if password != confirm:       errs.append("Passwords do not match.")
            if len(password) < 6:         errs.append("Password must be at least 6 characters.")
            if get_user(username.strip()): errs.append(f"Username '{username}' is already taken.")
            if errs:
                for e in errs: st.error(e)
            else:
                users = get_users()
                users.append({
                    "fullname": fullname.strip(), "email": email.strip(),
                    "username": username.strip(), "role": role,
                    "password": hash_pwd(password, username.strip())
                })
                if save_users(users):
                    st.success("Account created! Please log in.")
                    time.sleep(1); st.session_state["page"] = "login"; st.rerun()
                else:
                    st.error("Could not save registration. Please try again.")

        st.markdown("---")
        if st.button("Already have an account? Login →", use_container_width=True):
            st.session_state["page"] = "login"; st.rerun()

# ─────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────
def page_dashboard():
    u = current_user()
    st.title(f"📊 Dashboard")
    st.write(f"Welcome back, **{u['fullname']}** — {u['role']}")
    st.markdown("---")

    # Stats
    students  = get_students()
    att_data  = _read_json(DB_FILES["attendance"])
    today_str = dt_date.today().strftime("%Y-%m-%d")
    today_recs = [r for r in att_data if r["date"] == today_str]

    present = absent = 0
    for r in today_recs:
        for s in r["records"].values():
            if s=="Present": present+=1
            elif s=="Absent": absent+=1

    total = present+absent
    rate = f"{round(present/total*100,1)}%" if total else "N/A"

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi_card("Total Students",  str(len(students)), "👥", "#eff6ff","#1d4ed8")
    with c2: kpi_card("Present Today",   str(present),       "✅", "#f0fdf4","#16a34a")
    with c3: kpi_card("Absent Today",    str(absent),        "❌", "#fef2f2","#dc2626")
    with c4: kpi_card("Attendance Rate", rate,               "📈", "#faf5ff","#7c3aed")

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([5, 3], gap="large")

    with left:
        st.subheader("Analytics")
        t1, t2, t3 = st.tabs(["Today's Split", "By Department", "Trend Over Time"])

        with t1:
            if total == 0:
                st.info("No attendance recorded today yet.")
            else:
                fig = px.pie(values=[present, absent], names=["Present","Absent"],
                             color_discrete_sequence=["#16a34a","#dc2626"], hole=0.45)
                fig.update_layout(height=320, margin=dict(t=20,b=10,l=10,r=10))
                st.plotly_chart(fig, use_container_width=True)

        with t2:
            dept_map: Dict[str, Dict] = {}
            for r in att_data:
                d = r["department"]
                if d not in dept_map: dept_map[d] = {"present":0,"total":0}
                for s in r["records"].values():
                    dept_map[d]["total"] += 1
                    if s=="Present": dept_map[d]["present"] += 1
            if not dept_map:
                st.info("No attendance data available.")
            else:
                rows = [{"Department":d, "Attendance %":round(v["present"]/v["total"]*100,1) if v["total"] else 0}
                        for d,v in dept_map.items()]
                fig2 = px.bar(pd.DataFrame(rows), x="Department", y="Attendance %",
                              color="Department", text="Attendance %")
                fig2.update_layout(showlegend=False, height=320, yaxis_range=[0,110])
                fig2.update_traces(textposition="outside")
                st.plotly_chart(fig2, use_container_width=True)

        with t3:
            day_map: Dict[str, Dict] = {}
            for r in att_data:
                d = r["date"]
                if d not in day_map: day_map[d] = {"present":0,"total":0}
                for s in r["records"].values():
                    day_map[d]["total"] += 1
                    if s=="Present": day_map[d]["present"] += 1
            if not day_map:
                st.info("No trend data available.")
            else:
                rows2 = [{"Date":d,"Attendance %":round(v["present"]/v["total"]*100,1) if v["total"] else 0}
                         for d,v in sorted(day_map.items())]
                fig3 = px.line(pd.DataFrame(rows2), x="Date", y="Attendance %", markers=True)
                fig3.update_layout(height=320, yaxis_range=[0,110])
                st.plotly_chart(fig3, use_container_width=True)

    with right:
        st.subheader("Quick Actions")
        qc1, qc2 = st.columns(2)
        with qc1:
            if st.button("👥 Students",   use_container_width=True):
                st.session_state["page"]="students"; st.rerun()
            if st.button("📅 History",    use_container_width=True):
                st.session_state["page"]="history";  st.rerun()
        with qc2:
            if st.button("✅ Attendance", use_container_width=True):
                st.session_state["page"]="attendance"; st.rerun()
            if st.button("👤 Profile",   use_container_width=True):
                st.session_state["page"]="profile";   st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Recent Notices")
        notices = get_notices()
        if notices:
            for n in notices[:2]:
                notice_card(n["title"], n["content"][:70]+"…" if len(n["content"])>70 else n["content"],
                            n["date"], n.get("author",""))
        else:
            st.caption("No notices yet.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Recent Announcements")
        anns = get_announcements()
        if anns:
            for a in anns[:2]:
                ann_card(a["title"], a["description"][:70]+"…" if len(a["description"])>70 else a["description"],
                         a["date"], a.get("priority","Medium"), a.get("author",""))
        else:
            st.caption("No announcements yet.")

# ─────────────────────────────────────────────
# PAGE: STUDENTS
# ─────────────────────────────────────────────
def page_students():
    st.title("👥 Student Management")
    st.markdown("---")

    tab_view, tab_add, tab_edit = st.tabs(["🔍 View Students","➕ Add Student","✏️ Edit Student"])

    # ── VIEW ──
    with tab_view:
        students = get_students()
        if not students:
            st.info("No students yet. Use 'Add Student' tab.")
        else:
            df = pd.DataFrame(students).rename(columns={
                "student_id":"Student ID","name":"Name","department":"Department",
                "year":"Year","section":"Section","email":"Email","phone":"Phone"})

            sc, dc, so = st.columns([3,2,2])
            with sc: q = st.text_input("🔍 Search", placeholder="Name or ID…")
            with dc:
                depts = ["All"] + sorted(df["Department"].unique().tolist())
                dept_f = st.selectbox("Department", depts)
            with so: sort_f = st.selectbox("Sort By", ["Student ID","Name","Department"])

            if q:       df = df[df["Name"].str.contains(q,case=False,na=False)|df["Student ID"].str.contains(q,case=False,na=False)]
            if dept_f != "All": df = df[df["Department"]==dept_f]
            df = df.sort_values(sort_f)

            st.caption("💡 Select a row to Edit or Delete")
            sel = st.dataframe(df, use_container_width=True, hide_index=True,
                               on_select="rerun", selection_mode="single_row")
            rows = sel.get("selection",{}).get("rows",[])
            if rows:
                sid  = df.iloc[rows[0]]["Student ID"]
                sname = df.iloc[rows[0]]["Name"]
                st.info(f"Selected: **{sname}** (ID: {sid})")
                a1, a2, _ = st.columns([1,1,4])
                with a1:
                    if st.button("✏️ Edit", use_container_width=True):
                        st.session_state["edit_student_id"] = sid
                        st.session_state["page"] = "students"
                        st.info("Go to the 'Edit Student' tab →")
                with a2:
                    if st.checkbox("Confirm Delete", key="del_chk"):
                        if st.button("🗑️ Delete", use_container_width=True):
                            if delete_student(sid):
                                st.success(f"Deleted {sname}"); time.sleep(0.4); st.rerun()
                            else: st.error("Delete failed.")

    # ── ADD ──
    with tab_add:
        st.subheader("Add New Student")
        with st.form("add_stu_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1: sid   = st.text_input("Student ID (unique)", placeholder="e.g. STU1001")
            with c2: sname = st.text_input("Full Name",           placeholder="e.g. Alice Smith")
            c3, c4, c5 = st.columns([3,1,1])
            with c3: sdept = st.selectbox("Department", DEPTS)
            with c4: syear = st.selectbox("Year", YEARS)
            with c5: ssec  = st.selectbox("Section", SECS)
            c6, c7 = st.columns(2)
            with c6: semail = st.text_input("Email", placeholder="alice@school.edu")
            with c7: sphone = st.text_input("Phone", placeholder="+1234567890")
            submitted = st.form_submit_button("Save Student", use_container_width=True)

        if submitted:
            sid = sid.strip(); sname = sname.strip(); semail = semail.strip(); sphone = sphone.strip()
            if not all([sid, sname, semail, sphone]):
                st.error("All fields are required.")
            elif add_student({"student_id":sid,"name":sname,"department":sdept,
                              "year":syear,"section":ssec,"email":semail,"phone":sphone}):
                st.success(f"Added {sname} successfully!"); time.sleep(0.4); st.rerun()
            else:
                st.error("Duplicate Student ID. Please use a unique ID.")

    # ── EDIT ──
    with tab_edit:
        esid = st.session_state.get("edit_student_id")
        if not esid:
            st.info("Select a student in 'View Students' and click ✏️ Edit.")
        else:
            stu = get_student(esid)
            if not stu: st.error("Student not found."); st.session_state["edit_student_id"]=None
            else:
                st.subheader(f"Editing: {stu['name']} ({esid})")
                with st.form("edit_stu_form"):
                    ename  = st.text_input("Full Name", value=stu["name"])
                    ec1, ec2, ec3 = st.columns([3,1,1])
                    di = DEPTS.index(stu["department"]) if stu["department"] in DEPTS else 0
                    yi = YEARS.index(stu["year"]) if stu["year"] in YEARS else 0
                    si = SECS.index(stu["section"]) if stu["section"] in SECS else 0
                    with ec1: edept = st.selectbox("Department", DEPTS, index=di)
                    with ec2: eyear = st.selectbox("Year", YEARS, index=yi)
                    with ec3: esec  = st.selectbox("Section", SECS, index=si)
                    ec4, ec5 = st.columns(2)
                    with ec4: eemail = st.text_input("Email", value=stu["email"])
                    with ec5: ephone = st.text_input("Phone", value=stu["phone"])
                    sb1, sb2 = st.columns(2)
                    with sb1: save   = st.form_submit_button("Save Changes",  use_container_width=True)
                    with sb2: cancel = st.form_submit_button("Cancel",         use_container_width=True)

                if save:
                    if not ename.strip(): st.error("Name is required.")
                    elif update_student(esid,{"student_id":esid,"name":ename.strip(),
                                             "department":edept,"year":eyear,"section":esec,
                                             "email":eemail.strip(),"phone":ephone.strip()}):
                        st.success("Updated!"); st.session_state["edit_student_id"]=None
                        time.sleep(0.4); st.rerun()
                    else: st.error("Update failed.")
                if cancel:
                    st.session_state["edit_student_id"]=None; st.rerun()

# ─────────────────────────────────────────────
# PAGE: ATTENDANCE
# ─────────────────────────────────────────────
def page_attendance():
    st.title("✅ Record Attendance")
    st.markdown("---")

    c1,c2,c3 = st.columns(3)
    with c1: sel_date = st.date_input("Date", value=dt_date.today())
    with c2: sel_dept = st.selectbox("Department", DEPTS)
    with c3: sel_sec  = st.selectbox("Section", SECS)
    date_s = sel_date.strftime("%Y-%m-%d")

    students = [s for s in get_students() if s["department"]==sel_dept and s["section"]==sel_sec]

    if not students:
        st.info(f"No students in {sel_dept} – Section {sel_sec}.")
        return

    existing = get_att_record(date_s, sel_dept, sel_sec)
    if existing:
        st.warning("⚠️ Attendance already recorded for this date. Saving will overwrite.")
    else:
        st.info("Recording new attendance.")

    prev = existing["records"] if existing else {}

    st.subheader(f"{len(students)} Students — {sel_dept} / Section {sel_sec}")

    bk = f"bulk_{sel_dept}_{sel_sec}_{date_s}"
    if bk not in st.session_state: st.session_state[bk] = None

    bc1, bc2, _ = st.columns([1,1,5])
    with bc1:
        if st.button("Mark All Present", use_container_width=True): st.session_state[bk]="P"; st.rerun()
    with bc2:
        if st.button("Mark All Absent",  use_container_width=True): st.session_state[bk]="A"; st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    h1,h2,h3 = st.columns([1,3,1])
    with h1: st.markdown("**ID**")
    with h2: st.markdown("**Name**")
    with h3: st.markdown("**Present?**")
    st.markdown("<hr style='margin:.2rem 0'>", unsafe_allow_html=True)

    selections: Dict[str, str] = {}
    for idx, s in enumerate(students):
        sid = s["student_id"]
        if   st.session_state[bk] == "P": default = True
        elif st.session_state[bk] == "A": default = False
        elif sid in prev:                  default = (prev[sid]=="Present")
        else:                              default = True

        r1,r2,r3 = st.columns([1,3,1])
        with r1: st.write(sid)
        with r2: st.write(s["name"])
        with r3: chk = st.checkbox("Present", value=default, key=f"att_{sid}_{date_s}_{idx}", label_visibility="collapsed")
        selections[sid] = "Present" if chk else "Absent"
        st.markdown("<hr style='margin:.1rem 0;border-color:#f1f5f9'>", unsafe_allow_html=True)

    if st.button("💾 Save Attendance", type="primary", use_container_width=True):
        u = current_user()
        if save_att_record(date_s, sel_dept, sel_sec, selections, u["username"]):
            st.success("Attendance saved successfully!")
            st.session_state.pop(bk, None)
            time.sleep(0.5); st.rerun()
        else:
            st.error("Failed to save attendance.")

# ─────────────────────────────────────────────
# PAGE: HISTORY
# ─────────────────────────────────────────────
def page_history():
    st.title("📅 Attendance History")
    st.markdown("---")

    att_data = _read_json(DB_FILES["attendance"])
    students = get_students()
    stu_map = {s["student_id"]: s for s in students}

    fc1,fc2,fc3,fc4 = st.columns([1,2,2,3])
    with fc1:
        st.write(""); st.write("")
        use_date = st.checkbox("Filter by Date")
    with fc2: f_date = st.date_input("Date", value=dt_date.today(), disabled=not use_date)
    with fc3:
        f_dept = st.selectbox("Department", ["All"]+DEPTS)
    with fc4:
        stu_opts = ["All"] + [f"{s['student_id']} – {s['name']}" for s in students]
        f_stu_raw = st.selectbox("Student", stu_opts)
        f_stu_id  = f_stu_raw.split(" – ")[0] if f_stu_raw!="All" else "All"

    q = st.text_input("🔍 Search by Name", placeholder="Type name…")

    # Build flat report
    rows = []
    for r in att_data:
        if use_date and r["date"] != f_date.strftime("%Y-%m-%d"): continue
        if f_dept!="All" and r["department"]!=f_dept:            continue
        for sid, status in r["records"].items():
            if f_stu_id!="All" and sid!=f_stu_id: continue
            info = stu_map.get(sid,{})
            rows.append({"Date":r["date"],"Student ID":sid,"Name":info.get("name","Unknown"),
                         "Department":r["department"],"Section":r["section"],
                         "Status":status,"Recorded By":r.get("recorded_by","")})

    df = pd.DataFrame(rows)
    if not df.empty and q:
        df = df[df["Name"].str.contains(q,case=False,na=False)]

    if df.empty:
        st.info("No records match the selected filters.")
        return

    pres  = len(df[df["Status"]=="Present"])
    abs_c = len(df[df["Status"]=="Absent"])
    rate  = round(pres/len(df)*100,1) if len(df) else 0

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total Records", len(df))
    m2.metric("Present", pres)
    m3.metric("Absent",  abs_c)
    m4.metric("Rate",    f"{rate}%")

    st.markdown("<br>", unsafe_allow_html=True)
    tl, tr = st.columns([5,3], gap="medium")

    with tl:
        st.subheader("Records")
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode()
        st.download_button("📥 Export CSV", csv,
                           f"attendance_{dt_date.today().strftime('%Y%m%d')}.csv",
                           "text/csv", use_container_width=True)

    with tr:
        st.subheader("Distribution")
        fig = px.pie(values=[pres, abs_c], names=["Present","Absent"],
                     color_discrete_sequence=["#16a34a","#dc2626"], hole=0.4)
        fig.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE: ANNOUNCEMENTS
# ─────────────────────────────────────────────
def page_announcements():
    u = current_user()
    role = u["role"]
    st.title("📢 Announcements")
    st.markdown("---")

    anns = get_announcements()

    if role == "Admin":
        tabs = st.tabs(["🔍 View","➕ Create","✏️ Edit"])
        tab_v, tab_c, tab_e = tabs
    else:
        tab_v = st.tabs(["🔍 View"])[0]

    with tab_v:
        if not anns:
            st.info("No announcements yet.")
        else:
            for a in anns:
                ann_card(a["title"],a["description"],a["date"],a.get("priority","Medium"),a.get("author",""))
                if role=="Admin":
                    b1,b2,_ = st.columns([1,1,6])
                    with b1:
                        if st.button("Edit", key=f"ea_{a['id']}"):
                            st.session_state["edit_ann_id"] = a["id"]; st.rerun()
                    with b2:
                        if st.checkbox("Delete?", key=f"da_{a['id']}"):
                            if st.button("Confirm", key=f"dab_{a['id']}", type="primary"):
                                delete_announcement(a["id"]); time.sleep(0.3); st.rerun()
                st.write("")

    if role=="Admin":
        with tab_c:
            st.subheader("New Announcement")
            with st.form("new_ann", clear_on_submit=True):
                title = st.text_input("Title")
                desc  = st.text_area("Description")
                cc1, cc2 = st.columns(2)
                with cc1: adate    = st.date_input("Date", value=dt_date.today())
                with cc2: priority = st.selectbox("Priority", ["Low","Medium","High"])
                sub = st.form_submit_button("Post Announcement", use_container_width=True)
            if sub:
                if not title or not desc: st.error("Title and Description required.")
                else:
                    add_announcement({"title":title,"description":desc,
                                      "date":adate.strftime("%Y-%m-%d"),
                                      "priority":priority,"author":u["username"]})
                    st.success("Posted!"); time.sleep(0.4); st.rerun()

        with tab_e:
            eid = st.session_state.get("edit_ann_id")
            if not eid:
                st.info("Click 'Edit' on an announcement in the View tab.")
            else:
                ae = next((a for a in anns if a["id"]==eid), None)
                if not ae: st.error("Not found."); st.session_state["edit_ann_id"]=None
                else:
                    with st.form("edit_ann"):
                        et = st.text_input("Title", value=ae["title"])
                        ed = st.text_area("Description", value=ae["description"])
                        ec1,ec2 = st.columns(2)
                        with ec1:
                            try: dv = datetime.strptime(ae["date"],"%Y-%m-%d").date()
                            except: dv = dt_date.today()
                            edate = st.date_input("Date", value=dv)
                        with ec2:
                            pi = ["Low","Medium","High"].index(ae.get("priority","Medium"))
                            epri = st.selectbox("Priority",["Low","Medium","High"],index=pi)
                        sb1,sb2 = st.columns(2)
                        with sb1: save   = st.form_submit_button("Save",   use_container_width=True)
                        with sb2: cancel = st.form_submit_button("Cancel", use_container_width=True)
                    if save:
                        update_announcement(eid,{"title":et,"description":ed,
                                                 "date":edate.strftime("%Y-%m-%d"),
                                                 "priority":epri,"author":ae.get("author","")})
                        st.success("Updated!"); st.session_state["edit_ann_id"]=None
                        time.sleep(0.4); st.rerun()
                    if cancel: st.session_state["edit_ann_id"]=None; st.rerun()

# ─────────────────────────────────────────────
# PAGE: NOTICES
# ─────────────────────────────────────────────
def page_notices():
    u = current_user()
    role = u["role"]
    st.title("📌 Notice Board")
    st.markdown("---")
    notices = get_notices()

    if role=="Admin":
        tab_v, tab_c, tab_e = st.tabs(["🔍 View","➕ Create","✏️ Edit"])
    else:
        tab_v = st.tabs(["🔍 View"])[0]

    with tab_v:
        if not notices: st.info("No notices yet.")
        else:
            for n in notices:
                notice_card(n["title"],n["content"],n["date"],n.get("author",""))
                if role=="Admin":
                    b1,b2,_ = st.columns([1,1,6])
                    with b1:
                        if st.button("Edit", key=f"en_{n['id']}"):
                            st.session_state["edit_notice_id"]=n["id"]; st.rerun()
                    with b2:
                        if st.checkbox("Delete?", key=f"dn_{n['id']}"):
                            if st.button("Confirm", key=f"dnb_{n['id']}", type="primary"):
                                delete_notice(n["id"]); time.sleep(0.3); st.rerun()
                st.write("")

    if role=="Admin":
        with tab_c:
            st.subheader("Post a New Notice")
            with st.form("new_notice", clear_on_submit=True):
                title   = st.text_input("Title")
                content = st.text_area("Content")
                ndate   = st.date_input("Date", value=dt_date.today())
                sub     = st.form_submit_button("Post Notice", use_container_width=True)
            if sub:
                if not title or not content: st.error("Title and Content required.")
                else:
                    add_notice({"title":title,"content":content,
                                "date":ndate.strftime("%Y-%m-%d"),"author":u["username"]})
                    st.success("Notice posted!"); time.sleep(0.4); st.rerun()

        with tab_e:
            eid = st.session_state.get("edit_notice_id")
            if not eid: st.info("Click 'Edit' on a notice in the View tab.")
            else:
                ne = next((n for n in notices if n["id"]==eid), None)
                if not ne: st.error("Not found."); st.session_state["edit_notice_id"]=None
                else:
                    with st.form("edit_notice"):
                        et = st.text_input("Title",   value=ne["title"])
                        ec = st.text_area("Content",  value=ne["content"])
                        try: dv = datetime.strptime(ne["date"],"%Y-%m-%d").date()
                        except: dv = dt_date.today()
                        ed = st.date_input("Date", value=dv)
                        sb1,sb2 = st.columns(2)
                        with sb1: save   = st.form_submit_button("Save",   use_container_width=True)
                        with sb2: cancel = st.form_submit_button("Cancel", use_container_width=True)
                    if save:
                        update_notice(eid,{"title":et,"content":ec,
                                          "date":ed.strftime("%Y-%m-%d"),"author":ne.get("author","")})
                        st.success("Updated!"); st.session_state["edit_notice_id"]=None
                        time.sleep(0.4); st.rerun()
                    if cancel: st.session_state["edit_notice_id"]=None; st.rerun()

# ─────────────────────────────────────────────
# PAGE: PROFILE
# ─────────────────────────────────────────────
def page_profile():
    u = current_user()
    st.title("👤 My Profile")
    st.markdown("---")

    col1, col2 = st.columns([1,1], gap="large")

    with col1:
        st.subheader("Account Details")
        role_badge = "badge-admin" if u["role"]=="Admin" else "badge-faculty"
        st.markdown(f"""
        <div style="background:#fff;padding:2rem;border-radius:14px;border:1px solid #e2e8f0;
                    box-shadow:0 2px 8px rgba(0,0,0,.06)">
          <p style="color:#64748b;font-size:.8rem;margin-bottom:.1rem">FULL NAME</p>
          <p style="font-weight:700;font-size:1.2rem;margin-bottom:1.2rem">{u['fullname']}</p>
          <p style="color:#64748b;font-size:.8rem;margin-bottom:.1rem">EMAIL</p>
          <p style="font-weight:600;margin-bottom:1.2rem">{u['email']}</p>
          <p style="color:#64748b;font-size:.8rem;margin-bottom:.1rem">USERNAME</p>
          <p style="font-weight:600;margin-bottom:1.2rem">{u['username']}</p>
          <p style="color:#64748b;font-size:.8rem;margin-bottom:.4rem">ROLE</p>
          <span class="badge {role_badge}" style="font-size:.9rem">{u['role']}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["page"] = "login"
            st.rerun()

    with col2:
        st.subheader("Change Password")
        with st.form("chg_pwd", clear_on_submit=True):
            old_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password",     type="password", placeholder="Min 6 chars")
            cfm_pwd = st.text_input("Confirm New",      type="password")
            sub     = st.form_submit_button("Update Password", use_container_width=True)

        if sub:
            if new_pwd != cfm_pwd:    st.error("New passwords do not match.")
            elif len(new_pwd) < 6:    st.error("Password must be at least 6 characters.")
            else:
                db_user = get_user(u["username"])
                if not db_user or not verify_pwd(old_pwd, u["username"], db_user["password"]):
                    st.error("Current password is incorrect.")
                else:
                    users = get_users()
                    for usr in users:
                        if usr["username"] == u["username"]:
                            usr["password"] = hash_pwd(new_pwd, u["username"]); break
                    if save_users(users): st.success("Password updated successfully!")
                    else: st.error("Failed to update password.")

# ─────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────
page = st.session_state["page"]

if not is_logged_in():
    if page not in ("login","register"):
        st.session_state["page"] = "login"; page = "login"
    if page == "login":    page_login()
    elif page == "register": page_register()
else:
    if   page == "dashboard":    page_dashboard()
    elif page == "students":     page_students()
    elif page == "attendance":   page_attendance()
    elif page == "history":      page_history()
    elif page == "announcements":page_announcements()
    elif page == "notices":      page_notices()
    elif page == "profile":      page_profile()
    else:
        st.session_state["page"] = "dashboard"; st.rerun()
