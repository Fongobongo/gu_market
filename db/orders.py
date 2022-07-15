import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


connection = psycopg2.connect(user="postgres", password="123456", host="localhost", port=5432)
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)


def is_db_exists(db, conn=connection):

    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT datname FROM pg_database WHERE datname=%s);", (db,))
            response = cursor.fetchall()
            answer = response[0][0]
    return answer