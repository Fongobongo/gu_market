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


def create_db(db, conn=connection):

    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE {db};")

def create_tables(db):

    conn = psycopg2.connect(user="postgres", password="123456", host="localhost", port=5432, dbname=db)

    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE "prices" (
            "proto" int UNIQUE,
            "token_id" int,
            "eth_meteorite_price" numeric,
            "eth_shadow_price" numeric,
            "eth_gold_price" numeric,
            "eth_diamond_price" numeric,
            "gods_meteorite_price" numeric,
            "gods_shadow_price" numeric,
            "gods_gold_price" numeric,
            "gods_diamond_price" numeric
            );
            
            CREATE TABLE "cards" (
            "id" serial PRIMARY KEY,
            "proto" int UNIQUE,
            "name" varchar,
            "set" varchar,
            "collectable" bool
            );
            
            CREATE TABLE "tokens" (
            "id" serial PRIMARY KEY,
            "name" varchar,
            "price" numeric
            );
            
            ALTER TABLE "cards" ADD FOREIGN KEY ("proto") REFERENCES "prices" ("proto");
            ''')


def fill_table_tokens(db):

    conn = psycopg2.connect(user="postgres", password="123456", host="localhost", port=5432, dbname=db)

    with conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO tokens (name) VALUES ('eth'), ('gods');")

def write_tokens_to_db(db, eth_price, gods_price):

    conn = psycopg2.connect(user="postgres", password="123456", host="localhost", port=5432, dbname=db)

    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            UPDATE tokens SET price=(%s) where name='eth';
            UPDATE tokens SET price=(%s) where name='gods';
            ''', (eth_price, gods_price))


def write_prices_to_db(db, quality, token):

    conn = psycopg2.connect(user="postgres", password="123456", host="localhost", port=5432, dbname=db)

    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            UPDATE tokens SET price=(%s) where name='eth';
            UPDATE tokens SET price=(%s) where name='gods';
            ''', (eth_price, gods_price))
