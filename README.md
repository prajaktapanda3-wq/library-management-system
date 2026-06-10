# Library Management System

A Full-Stack Library Management System built using Flask and MySQL.

## Features

- User Registration and Login
- Secure Password Hashing
- Admin Dashboard
- User Dashboard
- Add/Edit/Delete Books
- Search Books
- Issue Books
- Return Books
- Fine Calculation
- View Users
- Delete Users
- Change Password
- Responsive Bootstrap UI

## Technology Stack

- Python Flask
- MySQL
- SQLAlchemy
- Bootstrap 5
- HTML/CSS
- Flask-Login

## Installation

### 1. Clone Project

```bash
git clone <repository-url>
cd Library-Management-System
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

Open `config.py` and update:

```python
SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://root:password@localhost/library_management"
)
```

### 4. Create Database

```bash
mysql -u root -p < schema.sql
```

### 5. Run Application

```bash
python app.py
```

### 6. Open Browser

Visit:

```
http://127.0.0.1:5000
```

## Default Admin Account

Username: admin

Password: admin123

(Automatically created on first run.)
