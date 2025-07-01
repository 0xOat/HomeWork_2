from clickhouse_connect import get_client

client = get_client(host='172.30.71.21', username='default', password='')

def query_clickhouse(sql):
    result = client.query(sql)
    print()
    return result.result_rows