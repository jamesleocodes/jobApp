import os
from flask import Flask, render_template, request
import pymysql
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@app.route('/', methods=['GET'])
def index():
    search = request.args.get('search', '')
    filter_platform = request.args.get('platform', '')
    filter_status = request.args.get('status', '')
    query = "SELECT * FROM job_applications WHERE 1=1"
    params = []
    if search:
        query += " AND (company_name LIKE %s OR job_title LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if filter_platform:
        query += " AND platform = %s"
        params.append(filter_platform)
    if filter_status:
        query += " AND status = %s"
        params.append(filter_status)
    query += " ORDER BY application_date DESC, number DESC"
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        applications = cursor.fetchall()
    conn.close()
    # For filter dropdowns
    platforms = sorted({row['platform'] for row in applications if row['platform']})
    statuses = sorted({row['status'] for row in applications if row['status']})
    if 'Offered' not in statuses:
        statuses.append('Offered')
    if 'Interviewing' not in statuses:
        statuses.append('Interviewing')
    return render_template('index.html', applications=applications, search=search, filter_platform=filter_platform, filter_status=filter_status, platforms=platforms, statuses=statuses, status_label='All Status')

if __name__ == '__main__':
    app.run(debug=True) 