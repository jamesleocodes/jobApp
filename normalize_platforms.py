import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def normalize_platforms():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            # Normalize Jobsdb
            jobsdb_sql = """
            UPDATE job_applications
            SET platform = 'Jobsdb'
            WHERE LOWER(platform) LIKE '%job%';
            """
            cursor.execute(jobsdb_sql)
            print(f"Updated Jobsdb platforms: {cursor.rowcount}")
            # Normalize LinkedIn and common misspellings
            linkedin_sql = """
            UPDATE job_applications
            SET platform = 'LinkedIn'
            WHERE LOWER(platform) LIKE '%link%' 
               OR LOWER(platform) LIKE '%linedin%'
               OR LOWER(platform) LIKE '%lineked%';
            """
            cursor.execute(linkedin_sql)
            print(f"Updated LinkedIn platforms: {cursor.rowcount}")
            connection.commit()
    finally:
        connection.close()
        print("Platform normalization complete.")

if __name__ == '__main__':
    normalize_platforms() 