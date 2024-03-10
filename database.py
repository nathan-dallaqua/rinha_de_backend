import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="mydatabase",
        user="admin",
        password="pass",
        host="database"
    )
    return conn

def insert_initial_clients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (id, limit, balance) VALUES (%s, %s, %s)", (1, 100000, 0))
    cur.execute("INSERT INTO clients (id, limit, balance) VALUES (%s, %s, %s)", (2, 80000, 0))
    cur.execute("INSERT INTO clients (id, limit, balance) VALUES (%s, %s, %s)", (3, 1000000, 0))
    cur.execute("INSERT INTO clients (id, limit, balance) VALUES (%s, %s, %s)", (4, 10000000, 0))
    cur.execute("INSERT INTO clients (id, limit, balance) VALUES (%s, %s, %s)", (5, 500000, 0))
    conn.commit()
    cur.close()
    conn.close()

insert_initial_clients()