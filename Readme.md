# Weekly Attendance Dashboard

A simple and interactive Streamlit dashboard for analyzing employee attendance data from CSV or Excel files. Users can upload attendance records, view daily, weekly, and monthly reports, track Work From Home (WFH) employees, and download filtered reports. 

---

## Features

✅ Upload CSV or Excel attendance files 

✅ Automatic detection of:
- Employee Name
- Employee ID
- Attendance Date
- Location
- Attendance Status
- Seat Information

✅ Daily Attendance Report

✅ Weekly Attendance Report

✅ Monthly Attendance Report

✅ Employee-wise Filtering

✅ WFH and Office Attendance Tracking

✅ Weekend Attendance Filter

✅ Download Reports as CSV

✅ Dataset Summary and Metrics

---

## Technologies Used

- Python
- Streamlit
- Pandas
- OpenPyXL

---

## Supported File Formats

- CSV (.csv)
- Excel (.xlsx)
- Excel (.xls)

---

## Project Structure

```text
Weekly-Attendance-Dashboard/
│
├── employee.py
├── requirements.txt
└── README.md
```

---

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/Bharath867-cmd/Weekly-Attendance-Dashboard.git
```

### 2. Open the Project Folder

```bash
cd Weekly-Attendance-Dashboard
```

### 3. Install Required Libraries

```bash
uv install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run employee.py
```

---

## Requirements

Create a file named `requirements.txt` and add:

```text
streamlit
pandas
openpyxl
xlrd
```

Install using:

```bash
uv install -r requirements.txt
```

---

## Dashboard Capabilities

### Upload Attendance File
Upload any employee attendance file in CSV or Excel format.

### View Dataset Summary
The dashboard shows:
- Total Records
- Total Employees
- Total Locations
- Attendance Status Count

### Generate Reports

#### Daily Report
View attendance for a selected date.

#### Weekly Report
View attendance records for a selected week.

#### Monthly Report
View attendance data for a selected month.

### WFH Tracking
Automatically identifies:
- WFH
- Office
- ETV
- EC

### Export Reports
Download generated reports as CSV files.

---

## Use Case

This project helps HR teams, managers, and administrators quickly analyze attendance data and monitor employee work locations without requiring a database.

---

## Author

**Bharath Kumar N**

GitHub:  
https://github.com/Bharath867-cmd

---