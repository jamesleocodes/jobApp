# Job Application Email Processor & Dashboard

![Dashboard Preview](dashboard.png)

## Features
- **Automated Email Processing:**
  - Extracts job application info from LinkedIn and JobsDB emails.
  - Handles batch/digest emails from JobsDB (multiple applications in one email).
  - Skips duplicates based on company, job title, and date.
- **Database Storage:**
  - Stores all applications in AWS RDS MySQL database.
  - Auto-increments the `number` field for each new entry.
  - Secure and scalable cloud database solution.
- **Web Dashboard:**
  - View all applications in a beautiful, responsive Bootstrap table.
  - Search and filter by company, job title, platform, and status.
  - See application date, company, job title, platform, and status at a glance.
- **AWS Integration:**
  - Secure connection to AWS RDS MySQL instance.
  - Automated data pipeline for reliable data storage.
  - Cloud-based solution for better scalability and reliability.

## Data Pipeline Structure
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Email Inbox    │────▶│  Email Parser   │────▶│  Data Processor │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Web Dashboard  │◀────│  Flask Server   │◀────│  AWS RDS MySQL  │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Pipeline Components:
1. **Gmail Inbox**
   - Source of job application emails
   - Connects via Gmail API
   - Filters for LinkedIn and JobsDB emails

2. **Email Parser**
   - Extracts job details from emails
   - Handles different email formats
   - Identifies duplicates

3. **Data Processor**
   - Cleans and normalizes data
   - Formats data for database storage
   - Handles batch processing

4. **AWS RDS MySQL**
   - Stores processed job applications
   - Maintains data integrity
   - Enables efficient querying

5. **Flask Server**
   - Serves the web dashboard
   - Handles API requests
   - Manages data retrieval

6. **Web Dashboard**
   - Displays job applications
   - Provides search and filter functionality
   - Real-time data updates

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
DB_HOST=your_aws_rds_endpoint
DB_USER=your_aws_rds_username
DB_PASSWORD=your_aws_rds_password
DB_NAME=your_database_name
TARGET_DATE=02-May-2025  # For email processing script
AWS_REGION=your_aws_region  # e.g., us-east-1
```

### 3. AWS RDS Setup
1. Create an AWS RDS MySQL instance if you haven't already
2. Configure security groups to allow access from your application
3. Note down the RDS endpoint, username, and password
4. Update your `.env` file with the RDS credentials

### 4. Run the email processor
```
python process_job_emails.py
```
This will extract job applications from your Gmail and update the MySQL database.

### 5. Run the web dashboard
Navigate to the `jobapp_web` or `email_processor` directory (wherever your Flask app is):
```
python app.py
```
Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Customization
- **Change the target date:** Edit `TARGET_DATE` in your `.env` file.
- **Change database/table:** Update your `.env` and SQL queries as needed.
- **UI tweaks:** Edit `templates/index.html` for custom styles or columns.
- **AWS Configuration:** Modify AWS region and RDS settings in `.env` file.

## Requirements
- Python 3.7+
- Flask
- PyMySQL
- python-dotenv
- AWS RDS MySQL instance
- AWS CLI (optional, for additional AWS services)

## Security Note
- Use an [App Password](https://support.google.com/accounts/answer/185833) for Gmail, not your main password.
- Never commit your `.env` file with real credentials to a public repository.
- Ensure your AWS RDS security groups are properly configured.
- Use IAM roles and policies for secure AWS access.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Enjoy your automated job application tracker and dashboard!** 