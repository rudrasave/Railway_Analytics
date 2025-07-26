# 🚂 Railway Revenue Analytics & User Management System

A full-stack Streamlit-based web application developed during my internship at **Western Railway – Zonal IT Centre, Churchgate, Mumbai**. This system is designed to assist with **revenue analytics**, **document management**, and **role-based user control** over freight data dashboards.

---

## 🎯 Project Overview

This project was built to support the **Indian Railways IT team** in analyzing apportioned freight revenue, automating data upload to Oracle DB, and managing user access securely.

### 🔧 Modules & Features

#### 📊 Revenue & Freight Data Analytics (Data Engineering + Visualization)
- Multi-year trend analysis of commodity-wise freight revenue.
- Dynamic visualization using **Plotly**, backed by **Oracle SQL queries**.
- Year/month dropdowns for filtering, comparisons, and insights generation.

#### 🔒 Role-Based User Management (Full-Stack Development)
- Secure login/signup with **SHA256 password hashing**.
- OTP-based password reset via **email (SMTP integration)**.
- Admin access to assign roles (employee/admin) and control page-level access.

#### 📁 Document Upload & Excel to Oracle Integration (Automation + Backend)
- Users can upload, search, download, or delete documents via a Streamlit UI.
- Uploaded Excel sheets are **automatically parsed**, **table structures inferred**, and **tables created in Oracle DB**.
- Handles type inference (DATE, NUMBER, VARCHAR) and bulk inserts.

---

## 💻 Tech Stack

- **Frontend**: Streamlit, HTML/CSS Custom Styling
- **Backend**: Python (Pandas, Regex, Oracledb), Oracle SQL
- **Data Viz**: Plotly, Matplotlib, Seaborn
- **Security**: Hashlib, Email OTP (SMTP), Session State
- **Other**: File handling, Regex, SQL templating

---

## 📁 Project Structure

├── app.py # Entry point - dashboard logic
├── Login_user_management.py # User authentication and permission control
├── Document.py # Document manager and Excel-to-Oracle automation
├── page1.py - page4.py # Various revenue analytics pages
├── queries.txt # SQL logic templates
├── testquery.py # DB credentials and constants

---

## 📜 Certificate

> Internship completed under **Zonal IT Centre, Western Railway**  
> Duration: **30 June 2025 – 25 July 2025**  
> Role: **Intern – Software Developer & Data Analyst**  
>  
> ✅ [View Certificate PDF](link-to-certificate)

---

## 🚀 Getting Started

### Prerequisites

- Oracle Instant Client
- Python 3.8+
- Required packages:
  ```bash
  pip install streamlit oracledb pandas plotly openpyxl
Setup Instructions
Clone the repo:

git clone https://github.com/your-username/railway-analytics.git
cd railway-analytics
Add your Oracle DB credentials in testquery.py.

Start the app:

streamlit run app.py
⚙️ React App Setup (If Applicable)
This project uses Create React App for front-end setup (if running alongside a React UI).

Available Scripts
In the project directory, you can run:

npm start
Runs the app in the development mode.
Open http://localhost:3000 to view it in your browser.
The page will reload if you make edits. You may also see lint errors in the console.

npm test
Launches the test runner in the interactive watch mode.
See more in the testing documentation.

npm run build
Builds the app for production to the build folder.
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified, and filenames include hashes.
Your app is ready to be deployed!

npm run eject
Note: this is a one-way operation. Once you eject, you can’t go back!
Ejecting gives you full control over the config files (Webpack, Babel, ESLint, etc.)

📚 Learn More
Create React App Docs

React Docs

Code Splitting

Analyzing the Bundle Size

Progressive Web App

Deployment

Build Fails to Minify

📬 Connect With Me
LinkedIn: Your LinkedIn Profile
