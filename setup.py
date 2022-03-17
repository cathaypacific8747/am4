import os
from dotenv import load_dotenv
import psycopg
import csv

if __name__ == '__main__':
    load_dotenv()

    with psycopg.connect(host=os.getenv('PG_HOST'), user=os.getenv('PG_USER'), port=os.getenv('PG_PORT'), password=os.getenv('PG_PASSWORD'), dbname=os.getenv('PG_DBNAME')) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            existing_tables = [t[0] for t in cur.fetchall()]

            for table_name in ['aircrafts', 'airports', 'engines']:
                if table_name in existing_tables:
                    cur.execute(f"DROP TABLE {table_name}")

                with open(f'data/{table_name}_table.sql', 'r') as s:
                    cur.execute(s.read())

                with cur.copy(f"COPY {table_name} FROM STDIN") as copy:
                    with open(f'data/{table_name}.csv', 'r', encoding='utf-8') as f:
                        for d in csv.reader(f):
                            copy.write_row(tuple(d))

            conn.commit()