import imaplib
import email
from email.header import decode_header
import pymysql
from datetime import datetime, timedelta
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_email():
    """Connect to Gmail using credentials from environment variables"""
    email_address = os.getenv('EMAIL_ADDRESS')
    password = os.getenv('EMAIL_PASSWORD')
    
    if not email_address or not password:
        raise ValueError("Email credentials not found in .env file")
    
    print(f"Connecting to Gmail as {email_address}...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_address, password)
    print("Successfully connected to Gmail")
    return mail

def connect_to_database():
    """Connect to RDS database using credentials from environment variables"""
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASSWORD')

    if not all([db_host, db_name, db_user, db_pass]):
        raise ValueError("Database credentials not found in .env file")

    print(f"Connecting to database {db_name} on {db_host}...")
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name
    )
    print("Successfully connected to database")
    return connection

def extract_job_info(email_body, email_subject, email_date, from_address):
    """Extract job information from email body and subject (LinkedIn/JobDB)"""
    print(f"\nProcessing email with subject: {email_subject}")
    print(f"From: {from_address}")
    
    job_info = {
        'company_name': None,
        'job_title': None,
        'application_date': None,
        'status': 'Applied',
        'platform': None,  # Will be set below
        'company_platform': 'NA'
    }
    
    # Determine the platform
    if 'linkedin' in from_address.lower():
        job_info['platform'] = 'LinkedIn'
        # 1. Company name from subject or body
        company_match = re.search(r"Your application was sent to ([\w\s\-&().]+)", email_subject)
        if not company_match:
            company_match = re.search(r"Your application was sent to ([\w\s\-&().]+)", email_body)
        if company_match:
            job_info['company_name'] = company_match.group(1).strip()
            print(f"Found company name: {job_info['company_name']}")
        # 2. Job title: first non-empty line after the line with 'Your application was sent to ...'
        lines = email_body.splitlines()
        job_title = None
        found_sent_to = False
        for i, line in enumerate(lines):
            if 'your application was sent to' in line.lower():
                found_sent_to = True
                # Look for the next non-empty line
                for next_line in lines[i+1:]:
                    next_line = next_line.strip()
                    if next_line:
                        job_title = next_line
                        break
                break
        if not job_title:
            # Fallback: first non-empty line that is not company/location
            for line in lines:
                line = line.strip()
                if line and (not job_info['company_name'] or job_info['company_name'].lower() not in line.lower()):
                    job_title = line
                    break
        if job_title:
            job_info['job_title'] = job_title
            print(f"Found job title: {job_info['job_title']}")
        # 3. Application date from body
        app_date_match = re.search(r'Applied on ([A-Za-z]+ \d{1,2}, \d{4})', email_body)
        if app_date_match:
            try:
                parsed_date = datetime.strptime(app_date_match.group(1), "%B %d, %Y")
                job_info['application_date'] = parsed_date.strftime('%Y-%m-%d')
                print(f"Found application date: {job_info['application_date']}")
            except Exception as e:
                print(f"Could not parse application date: {e}")
        # 4. Status from subject
        if 'sent to' in email_subject.lower():
            job_info['status'] = 'Applied'
    else:
        job_info['platform'] = 'Jobsdb'
        # Extract job title from subject: 'your application for (.+?) was successfully'
        job_title_match = re.search(r'your application for ([\w\s\-/&().]+?) was successfully', email_subject, re.IGNORECASE)
        if job_title_match:
            job_info['job_title'] = job_title_match.group(1).strip()
            print(f"Found job title in subject: {job_info['job_title']}")
        # Try to extract company name from body (common in JobsDB emails)
        company_match = re.search(r'company[:\s]*([\w\s\-&().]+)', email_body, re.IGNORECASE)
        if company_match:
            job_info['company_name'] = company_match.group(1).strip()
            print(f"Found company name in body: {job_info['company_name']}")
        # Fallback: try to extract company name from subject if present
        if not job_info['company_name']:
            company_match = re.search(r'at ([\w\s\-&().]+)', email_subject, re.IGNORECASE)
            if company_match:
                job_info['company_name'] = company_match.group(1).strip()
                print(f"Found company name in subject: {job_info['company_name']}")
        if email_date:
            job_info['application_date'] = email_date.strftime('%Y-%m-%d')
        else:
            job_info['application_date'] = datetime.now().strftime('%Y-%m-%d')
    print(f"Application date: {job_info['application_date']}")
    return job_info

def get_next_number(connection):
    """Get the next number for the job_applications table."""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT MAX(number) FROM job_applications")
        result = cursor.fetchone()
        max_number = result[0] if result and result[0] is not None else 0
        return max_number + 1
    finally:
        cursor.close()

def update_database(connection, job_info, next_number):
    """Update the database with job information, using the provided next_number."""
    cursor = connection.cursor()
    # Check if this job application already exists
    check_sql = """
    SELECT 1 FROM job_applications 
    WHERE company_name = %s AND job_title = %s AND application_date = %s
    """
    try:
        print(f"\nChecking if job application exists for company: '{job_info['company_name']}', job title: '{job_info['job_title']}', date: {job_info['application_date']}...")
        cursor.execute(check_sql, (
            job_info['company_name'],
            job_info['job_title'],
            job_info['application_date']
        ))
        if cursor.fetchone() is None:
            # Insert new job application with the next number
            insert_sql = """
            INSERT INTO job_applications 
            (number, company_name, job_title, application_date, status, platform, company_platform) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                next_number,
                job_info['company_name'],
                job_info['job_title'],
                job_info['application_date'],
                job_info['status'],
                job_info['platform'],
                job_info['company_platform']
            ))
            connection.commit()
            print(f"Successfully added job application for {job_info['company_name']} with number {next_number}")
            return True  # Inserted
        else:
            print(f"Duplicate found: Skipping entry for company: '{job_info['company_name']}', job title: '{job_info['job_title']}', date: {job_info['application_date']} (already exists in DB)")
            return False  # Not inserted
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        connection.rollback()
        return False
    finally:
        cursor.close()

def process_linkedin_emails(mail, db_connection, target_date, search_date, before_date, next_number):
    print(f"\nSearching for LinkedIn job application emails from {search_date}...")
    search_criteria = f'(FROM "jobs-noreply@linkedin.com" SINCE "{search_date}" BEFORE "{before_date}" SUBJECT "your application was sent")'
    print(f"Search criteria: {search_criteria}")
    _, messages = mail.search(None, search_criteria)
    added_count = 0
    if not messages[0]:
        print(f"No LinkedIn job application emails found from {search_date}")
        return next_number, added_count
    linkedin_emails = messages[0].split()
    print(f"\nFound {len(linkedin_emails)} LinkedIn job application emails")
    linkedin_applications = []
    for message_num in linkedin_emails:
        _, msg_data = mail.fetch(message_num, "(RFC822)")
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        subject = decode_header(email_message["subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        from_address = email_message["from"]
        # Check if this is a job application email
        if "your application was sent" in subject.lower():
            linkedin_applications.append(message_num)
    print(f"\nFound {len(linkedin_applications)} LinkedIn job application emails with the correct subject pattern")
    if not linkedin_applications:
        print("No matching LinkedIn job application emails to process")
        return next_number, added_count
    for message_num in linkedin_applications:
        print(f"\nProcessing email {message_num.decode()}")
        _, msg_data = mail.fetch(message_num, "(RFC822)")
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        # Get email date
        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            email_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            print(f"Email date: {email_date.strftime('%Y-%m-%d')}")
        else:
            email_date = None
            print("No email date found")
        # Skip if email is not from target date
        if not email_date or email_date.date() != target_date.date():
            print(f"Skipping email from {email_date.strftime('%Y-%m-%d')} (not from target date)")
            continue
        # Get email subject and from address
        subject = decode_header(email_message["subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        from_address = email_message["from"]
        # Get email body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
        # Extract job information
        job_info = extract_job_info(body, subject, email_date, from_address)
        # Update database if we have the required information
        if job_info['company_name'] and job_info['job_title']:
            inserted = update_database(db_connection, job_info, next_number)
            if inserted:
                next_number += 1
                added_count += 1
        else:
            print(f"Could not extract job information from email: {subject}")
    print(f"\nTotal new LinkedIn job applications added: {added_count}")
    return next_number, added_count

def extract_jobsdb_applications(email_body, email_subject, email_date, from_address):
    """Extract all job applications from a JobsDB email body."""
    print(f"\nProcessing JobsDB email with subject: {email_subject}")
    print(f"From: {from_address}")
    applications = []
    # Flexible regex: matches with or without 'Hi ...,' at the start
    pattern = re.compile(
        r'(?:Hi [\w\s,]+)?your application for ([\w\s\-/&().]+?) was successfully submitted to ([\w\s\-&().]+)',
        re.IGNORECASE
    )
    for match in pattern.finditer(email_body):
        job_title = match.group(1).strip()
        company_name = match.group(2).strip()
        print(f"Found job title: {job_title}, company name: {company_name}")
        application_date = email_date.strftime('%Y-%m-%d') if email_date else datetime.now().strftime('%Y-%m-%d')
        applications.append({
            'company_name': company_name,
            'job_title': job_title,
            'application_date': application_date,
            'status': 'Applied',
            'platform': 'Jobsdb',
            'company_platform': 'NA'
        })
    return applications

def process_jobsdb_emails(mail, db_connection, target_date, search_date, before_date, next_number):
    print(f"\nSearching for JobsDB job application emails from {search_date}...")
    jobsdb_search_criteria = f'(FROM "noreply@jobsdb.com" SINCE "{search_date}" BEFORE "{before_date}" SUBJECT "Your application was successfully submitted")'
    print(f"Search criteria: {jobsdb_search_criteria}")
    _, jobsdb_messages = mail.search(None, jobsdb_search_criteria)
    jobsdb_added_count = 0
    if not jobsdb_messages[0]:
        print(f"No JobsDB job application emails found from {search_date}")
        return next_number, jobsdb_added_count
    jobsdb_emails = jobsdb_messages[0].split()
    print(f"\nFound {len(jobsdb_emails)} JobsDB job application emails")
    for message_num in jobsdb_emails:
        print(f"\nProcessing JobsDB email {message_num.decode()}")
        _, msg_data = mail.fetch(message_num, "(RFC822)")
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        # Get email date
        date_tuple = email.utils.parsedate_tz(email_message['Date'])
        if date_tuple:
            email_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            print(f"Email date: {email_date.strftime('%Y-%m-%d')}")
        else:
            email_date = None
            print("No email date found")
        # Skip if email is not from target date
        if not email_date or email_date.date() != target_date.date():
            print(f"Skipping email from {email_date.strftime('%Y-%m-%d')} (not from target date)")
            continue
        # Get email subject and from address
        subject = decode_header(email_message["subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        from_address = email_message["from"]
        # Get email body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
        # Extract all job applications from this email
        applications = extract_jobsdb_applications(body, subject, email_date, from_address)
        for job_info in applications:
            inserted = update_database(db_connection, job_info, next_number)
            if inserted:
                next_number += 1
                jobsdb_added_count += 1
        if not applications:
            print(f"Could not extract job information from email: {subject}")
    print(f"\nTotal new JobsDB job applications added: {jobsdb_added_count}")
    return next_number, jobsdb_added_count

def process_emails():
    """Main function to process emails and update database"""
    try:
        # Connect to email
        mail = connect_to_email()
        mail.select("inbox")
        print("\nSearching for job application emails...")
        
        # Set the target date for processing and searching from .env
        target_date_str = os.getenv("TARGET_DATE")
        if not target_date_str:
            raise ValueError("TARGET_DATE not set in .env file")
        search_date = target_date_str
        # Calculate the next day for BEFORE clause
        dt = datetime.strptime(search_date, "%d-%b-%Y")
        before_date = (dt + timedelta(days=1)).strftime("%d-%b-%Y")
        print(f"\nSearching for LinkedIn job application emails from {search_date}...")
        target_date = dt
        
        db_connection = connect_to_database()
        next_number = get_next_number(db_connection)
        print(f"Starting new entries from number {next_number}")
        
        # Process LinkedIn emails
        next_number, linkedin_added_count = process_linkedin_emails(mail, db_connection, target_date, search_date, before_date, next_number)
        # Process JobsDB emails
        next_number, jobsdb_added_count = process_jobsdb_emails(mail, db_connection, target_date, search_date, before_date, next_number)
        
        # Now close and logout
        mail.close()
        mail.logout()
        db_connection.close()
        print(f"\nProcessing completed. Total new LinkedIn: {linkedin_added_count}, JobsDB: {jobsdb_added_count}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Starting job application email processor...")
    process_emails() 