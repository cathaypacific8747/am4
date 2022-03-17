import os
from dotenv import load_dotenv
import psycopg

if __name__ == '__main__':
    load_dotenv()

    with psycopg.connect(host=os.getenv('PG_HOST'), user=os.getenv('PG_USER'), port=os.getenv('PG_PORT'), password=os.getenv('PG_PASSWORD'), dbname=os.getenv('PG_DBNAME')) as conn:
        with conn.cursor() as cur:
            print('OK!')