import psycopg2

def get_postgres_schema(creds):
    conn = psycopg2.connect(
        dbname=creds.dbname,
        user=creds.user,
        password=creds.password,
        host=creds.host,
        port=creds.port
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    schema = {}
    for table, column, dtype in rows:
        schema.setdefault(table, []).append(f"{column} {dtype}")
    return "\n\n".join(
        f"Table {t}:\n" + "\n".join(cols) for t, cols in schema.items()
    )


def execute_sql(sql: str, creds):
    conn = psycopg2.connect(
        dbname=creds.dbname,
        user=creds.user,
        password=creds.password,
        host=creds.host,
        port=creds.port
    )
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return [dict(zip(columns, row)) for row in result]


def get_query_plan(sql: str, creds):
    conn = psycopg2.connect(
        dbname=creds.dbname,
        user=creds.user,
        password=creds.password,
        host=creds.host,
        port=creds.port
    )
    cur = conn.cursor()
    cur.execute(f"EXPLAIN (FORMAT JSON) {sql}")
    plan = cur.fetchone()[0]
    cur.close()
    conn.close()
    return plan
