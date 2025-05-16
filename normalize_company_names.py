import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def normalize_company_names():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            # Select all company names with a full stop
            cursor.execute("SELECT number, company_name FROM job_applications WHERE company_name LIKE '%.%'")
            rows = cursor.fetchall()
            updated = 0
            for row in rows:
                number = row['number']
                company_name = row['company_name']
                new_name = company_name.split('.', 1)[0].strip()
                if new_name != company_name:
                    update_sql = "UPDATE job_applications SET company_name = %s WHERE number = %s"
                    cursor.execute(update_sql, (new_name, number))
                    updated += 1
            connection.commit()
            print(f"Normalized {updated} company names (truncated at first full stop)")
    finally:
        connection.close()
        print("Company name normalization complete.")

if __name__ == '__main__':
    normalize_company_names() 