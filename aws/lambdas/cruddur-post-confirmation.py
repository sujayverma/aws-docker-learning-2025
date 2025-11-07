import json
import psycopg2
import os

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print(f'userAttributes: {user}')
    user_name = user['name']
    user_email = user['email']
    user_cognito_id = user['sub']
    conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
    cur = conn.cursor()
    try:        
        sql = f"""
         INSERT INTO users (display_name, handle, email, cognito_user_id)
         VALUES(%s, %s, %s, %s)
        """
        cur.execute(sql, (user_name, user_name.lower(), user_email, user_cognito_id))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print("Database connection closed.")
    return event