# EduAttend - Student Attendance Management System

EduAttend is a premium, AI-powered **Student Attendance Management System** built with **Streamlit**, **Plotly**, and **Pandas**. It is designed with a sleek dark-blue and white SaaS-like theme, dynamic routing, role-based controls, and fully structured JSON database models.

---

## 🚀 Features

### 1. Secure Authentication & Authorization
- **Modern Login & Registration:** Password hashing using SHA-256 with user-specific salting (`hashlib`).
- **Dynamic Routing:** Built using modern Streamlit `st.navigation`. Unauthenticated users can only access the Login and Register screens, while authenticated users get access to the full application dashboard.
- **Role-Based Views:** Supports **Admin** (can manage students, announcements, notices, and record/view attendance) and **Faculty** (can record/view attendance and view notices/announcements in read-only format).

### 2. Premium Analytics Dashboard
- **KPI Metrics:** Displays Total Students, Present Count, Absent Count, and Today's Attendance Rate.
- **Interactive Plotly Visualizations:**
  - *Daily Distribution:* Pie chart of present vs absent status.
  - *Department Performance:* Bar chart of class attendance rates grouped by department.
  - *Historical Trends:* Line chart tracking attendance percentage over time.
- **Feeds & Action Panels:** Live notifications for notices, announcements, recent activity logs, and quick page switcher buttons.

### 3. Student Management (Admin CRUD)
- Add new students with ID validation (ensures no duplicates).
- Filter and search students by Name or ID, and sort dynamically.
- Select a student row to edit their full details or delete their profile.

### 4. Attendance Recording
- Filter by Date, Department, and Section.
- Mark attendance easily using checkboxes.
- Bulk check actions: "Mark All Present" and "Mark All Absent".
- Prevents database duplicate records for the same Date, Department, and Section.

### 5. Attendance History & CSV Export
- Search logs using text searches and filters (by date, department, or individual student).
- Live metrics and charts reflecting the filtered subset.
- One-click CSV export utility to download records locally.

### 6. Notice Board & Announcements
- Create, edit, and delete notice posts (Admin only).
- View color-coded prioritized announcements and important alerts.

---

## 📁 Project Folder Structure

```
student attendance/
│
├── app.py                   # Main script & Page Router
├── requirements.txt         # Dependencies list
├── README.md                # System documentation
├── Procfile                 # Startup command for Render
├── runtime.txt              # Python runtime version
│
├── assets/
│      logo.png              # Generated logo
│      background.jpg        # Generated background
│
├── data/                    # JSON Databases (auto-generated if missing)
│      users.json
│      students.json
│      attendance.json
│      announcements.json
│      notices.json
│
├── pages/                   # Application Screens
│      login.py
│      register.py
│      dashboard.py
│      students.py
│      attendance.py
│      history.py
│      announcements.py
│      notices.py
│      profile.py
│
└── utils/                   # Shared logic utilities
       auth.py               # Security & Session management
       database.py           # JSON database layer (CRUD)
       attendance_utils.py   # Analytics calculations
       styles.py             # Global CSS styling
```

---

## 🛠️ Installation & Local Setup

### Prerequisites
- Python 3.9, 3.10, or 3.11 installed.

### 1. Clone the project and navigate to the directory
```bash
cd "student attendance"
```

### 2. Create and activate a Virtual Environment
**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install requirements
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser to view the application.

---

## ☁️ Deployment on Render

This project is deployment-ready out of the box using Render.

### Steps to Deploy:
1. Push this workspace code to a GitHub repository.
2. Log in to your [Render Dashboard](https://dashboard.render.com/) and click **New > Web Service**.
3. Link your GitHub repository.
4. Configure the Web Service settings:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py`
5. Click **Deploy Web Service**.
6. Render will read `runtime.txt` and install python, build your dependencies, and run Streamlit automatically.
