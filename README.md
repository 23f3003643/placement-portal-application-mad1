# 🎓 Campus Placement Portal

A web-based **Placement Portal Application** built using **Flask** that helps institutes manage campus recruitment efficiently.

The platform connects **Admin (Placement Cell), Companies, and Students** to streamline the placement process — from company registration to student job applications and final selections.

This system replaces manual processes such as spreadsheets and email communication with a centralized recruitment platform.

---

# 🚀 Features

## 🔐 Authentication System
- Role-based login for **Admin, Company, and Student**
- Student and Company registration
- **Admin account is predefined**
- Secure authentication using **Flask-Login**

---

# 👨‍💼 Admin Functionalities

Admin represents the **Institute Placement Cell** and has full system access.

Admin can:

- 📊 View dashboard statistics
- ✅ Approve / reject company registrations
- 📝 Approve / reject placement drives
- 👨‍🎓 Manage student accounts
- 🏢 Manage company accounts
- 📄 View all applications
- 🔍 Search students by:
  - Name
  - Student ID
  - Phone
- 🔍 Search companies by name
- 🚫 Blacklist or deactivate students
- 🚫 Blacklist or deactivate companies

---

# 🏢 Company Functionalities

Companies must be **approved by Admin before accessing the dashboard**.

Companies can:

- 📝 Create company profile
- 📢 Create placement drives
- ✏️ Edit placement drives
- 🔒 Close placement drives
- 🗑 Delete placement drives
- 👀 View student applications
- 📂 Review student resumes
- ⭐ Shortlist candidates
- 🏆 Update application status:
  - Shortlisted
  - Selected
  - Rejected

---

# 🎓 Student Functionalities

Students can:

- 📝 Register and login
- 👤 Update profile
- 📄 Upload resume
- 🔎 Browse approved placement drives
- 📌 Apply to placement drives
- 📊 Track application status
- 📜 View application history

---

# 📊 Key Entities

## 📢 Placement Drive
Represents a job posting created by a company.

Attributes include:
- Drive ID
- Company ID
- Job Title
- Job Description
- Eligibility Criteria
- Minimum CGPA
- Salary
- Location
- Deadline
- Status (Pending / Approved / Closed)

---

## 📄 Application
Represents a student's job application.

Attributes include:
- Application ID
- Student ID
- Drive ID
- Application Date
- Status (Applied / Shortlisted / Selected / Rejected)

---

## 🏢 Company Profile

Stores information about registered companies.

Attributes include:
- Company ID
- Company Name
- HR Contact
- Website
- Approval Status
- Description

---

# 🛠 Technology Stack

### Backend
- Python
- Flask

### Frontend
- HTML
- CSS
- Bootstrap
- Jinja2

### Database
- SQLite

### Libraries
- Flask-Login
- SQLAlchemy
- Werkzeug

---

# 📂 Project Structure
placement-portal/

static/
│
├── css/
│ └── style.css
│
├── images/
│
└── resumes/

templates/
│
├── base.html
├── login.html
├── index.html
│
├── admin_dashboard.html
├── admin_companies.html
├── admin_students.html
├── admin_drives.html
├── admin_applications.html
│
├── company_dashboard.html
├── company_drive.html
├── create_drive.html
├── edit_drive.html
├── company_profile.html
│
├── student_dashboard.html
├── student_drives.html
├── student_applications.html
└── student_profile.html

main.py
models.py
routes.py
extensions.py
requirements.txt
README.md

### Run the application
python3 main.py

### Open browser
http://127.0.0.1:5000

# 🔑 Default Admin Login
Email: admin@123.com
Password: 123admin

---

# 📌 Core Functionalities Implemented

✔ Role-based authentication  
✔ Company approval system  
✔ Placement drive approval workflow  
✔ Student job application system  
✔ Application status tracking  
✔ Resume upload system  
✔ Admin search functionality  
✔ Dashboard analytics for each role  

---
