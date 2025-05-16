# Job Application Email Processor & Dashboard

This project automates the extraction of job application data from your email inbox (Gmail) and stores it in a MySQL database. It also provides a modern web dashboard to view, search, and filter your job applications.

## Features
- **Automated Email Processing:**
  - Extracts job application info from LinkedIn and JobsDB emails.
  - Handles batch/digest emails from JobsDB (multiple applications in one email).
  - Skips duplicates based on company, job title, and date.
- **Database Storage:**
  - Stores all applications in a MySQL table (`job_applications`).
  - Auto-increments the `number` field for each new entry.
- **Web Dashboard:**
  - View all applications in a beautiful, responsive Bootstrap table.
  - Search and filter by company, job title, platform, and status.
  - See application date, company, job title, platform, and status at a glance.

## Folder Structure
```
email_processor/
  process_job_emails.py      # Main script to process emails and update DB
  templates/
    index.html               # Web dashboard template (for Flask app)
  README.md                  # This file
jobapp_web/
  app.py                     # Flask web app (alternative location)
  templates/
    index.html               # Web dashboard template
.env                          # Environment variables (not included)
```

## Setup Instructions

### 1. Clone the repository and install dependencies
```
pip install -r requirements.txt
```

### 2. Configure environment variables
Create a `.env` file in the project directory with:
```
EMAIL_ADDRESS=your_gmail_address@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
DB_HOST=your_mysql_host
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name
TARGET_DATE=02-May-2025  # For email processing script
```

### 3. Run the email processor
```
python process_job_emails.py
```
This will extract job applications from your Gmail and update the MySQL database.

### 4. Run the web dashboard
Navigate to the `jobapp_web` or `email_processor` directory (wherever your Flask app is):
```
python app.py
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Customization
- **Change the target date:** Edit `TARGET_DATE` in your `.env` file.
- **Change database/table:** Update your `.env` and SQL queries as needed.
- **UI tweaks:** Edit `templates/index.html` for custom styles or columns.

## Requirements
- Python 3.7+
- Flask
- PyMySQL
- python-dotenv

## Security Note
- Use an [App Password](https://support.google.com/accounts/answer/185833) for Gmail, not your main password.
- Never commit your `.env` file with real credentials to a public repository.

---

**Enjoy your automated job application tracker and dashboard!** 