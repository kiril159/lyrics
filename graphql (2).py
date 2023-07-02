import os
from python_graphql_client import GraphqlClient

backend_service = os.getenv("BACKEND_SERVICE", default="llm.dev.finch.fm")
headers = {
    "Cookie": "J_SESSION=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIwYmFlYTJmMC1hZTIwLTM1MGQtYjc4Zi01OGNkZGFjNDQyYTkiLCJpc3MiOiJKYWNxdWVsaW5lIiwiaWQiOiIwYmFlYTJmMC1hZTIwLTM1MGQtYjc4Zi01OGNkZGFjNDQyYTkiLCJleHAiOjE2ODgzNDMzMzksImp0aSI6ImU3YTg3MmRlLWJhN2MtNDZhMC05MjE2LTJiYWJiYjBkNGFjMyIsImF1dGhvcml0aWVzIjpbIlJPTEVfU1VQRVJfVVNFUiIsIlJPTEVfQURNSU4iLCJST0xFX0NPTlNUUlVDVE9SIl0sInVzZXJuYW1lIjoic3VwZXJ1c2VyIn0.PRicBhO9mtbDXMQpr6pBZnyu3nJgVJqoI6Ka0O4GroA; J_REFRESH=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIwYmFlYTJmMC1hZTIwLTM1MGQtYjc4Zi01OGNkZGFjNDQyYTkiLCJpc3MiOiJKYWNxdWVsaW5lIiwianRpIjoiMDJjMjYwNTMtMmFiOC00M2Q4LTliMDktZDhiMDYyODNkZGNjIn0.J2M5jl8ITdTwsNQ8GtR3p05P1D6H0DTwAs6pdvRlZbg"
}

def get_table_from_graphql(table, s3Id=''):
    graphql_client = GraphqlClient(endpoint=f"https://{backend_service}/finch/cms/graphql", headers=headers)

    query = """
        query Table(
            $type: String
            $page: Int! = 0
            $pageSize: Int! = 1
            $orders: [InputOrder]
            $filters: [InputFilter]
        ) {
            table(pageSize: $pageSize, page: $page, type: $type, orders: $orders, filters: $filters) {
                totalCount
                hasMore
                documents {
                    id
                    deleted
                    data
                    snapshot
                }
            }
        }
        """
    pageSize = 200
    variables = {"type": table, "page": 0, "pageSize": pageSize}
    
    if s3Id:
        variables["filters"] = [{"field":"idS3","operator":"ILIKE","value":s3Id}]
    
    request = graphql_client.execute(query=query, variables=variables)
    hasMore = request['data']['table']['hasMore']
    if hasMore:
        page = 1
        while hasMore:
            variables = {"type": table, "page": page, "pageSize": pageSize}
            req = graphql_client.execute(query=query, variables=variables)
            request['data']['table']['documents'] += req['data']['table']['documents']
            hasMore = req['data']['table']['hasMore']
            page += 1
    return request

def get_entry_from_graphql(table, id):
    graphql_client = GraphqlClient(endpoint=f"https://{backend_service}/finch/cms/graphql", headers=headers)

    query = """
        query Get($type: String, $id: String) {
            get(type: $type, id: $id) {
                document {
                    data
                    deleted
                    draftId
                    id
                    snapshot
                    type
                }
            }
        }
    """
    variables = {"type": table, "id": id}
    
    request = graphql_client.execute(query=query, variables=variables)
    
    return request

def update_entry(table, id, data):
    graphql_client = GraphqlClient(endpoint=f"https://{backend_service}/finch/cms/graphql", headers=headers)

    query = """
        mutation update($type: String, $id: String, $data: Json) {
            update(type: $type, id: $id, data: $data) {
                document {
                    type
                    id
                    deleted
                    data
                }
                errors {
                    field
                    msg
                }
            }
        }
    """
    variables = {"type": table, "id": id, "data": data}
    
    request = graphql_client.execute(query=query, variables=variables)
    
    return request

def create_entry(table, data):
    graphql_client = GraphqlClient(endpoint=f"https://{backend_service}/finch/cms/graphql", headers=headers)

    query = """
        mutation create($type: String, $data: Json) {
            create(type: $type, data: $data) {
                document {
                    type
                    id
                    deleted
                    data
                }
                errors {
                    field
                    msg
                }
            }
        }
    """
    variables = {"type": table, "data": data}
    
    request = graphql_client.execute(query=query, variables=variables)
    
    return request

songs = get_table_from_graphql('Music', 37)['data']['table']['documents']

entry = get_entry_from_graphql('Music', '51e95230-3fcf-4551-9d82-45f13299b888')['data']['get']['document']['data']

newData = {
  "idS3": "38329337",
  "songLyrics": [
    {
      "ratio": 82,
      "end_time": 27.1,
      "end_word": 5,
      "text_line": "Прощальных белых поцелуев след во мне",
      "text_test": "Прощайных белых пацую в след вамне",
      "start_time": 21.82,
      "start_word": 0,
      "number_line": 0
    },
    {
      "ratio": 83,
      "end_time": 30.38,
      "end_word": 8,
      "text_line": "Ты не вернёшься",
      "text_test": "Ты не вернався",
      "start_time": 28.52,
      "start_word": 6,
      "number_line": 1
    },
    {
      "ratio": 98,
      "end_time": 36.66,
      "end_word": 13,
      "text_line": "Меня рисуют мелом на стенее",
      "text_test": "Меня рисуют мелом на стене",
      "start_time": 32.7,
      "start_word": 9,
      "number_line": 2
    },
    {
      "ratio": 83,
      "end_time": 41.08,
      "end_word": 16,
      "text_line": "Ты не вернёшься",
      "text_test": "Ты не вернався",
      "start_time": 39.2,
      "start_word": 14,
      "number_line": 3
    },
    {
      "ratio": 92,
      "end_time": 46.34,
      "end_word": 21,
      "text_line": "И пролетают чёрные леса",
      "text_test": "И пролеют ают черные леса",
      "start_time": 43.16,
      "start_word": 17,
      "number_line": 4
    },
    {
      "ratio": 88,
      "end_time": 49.72,
      "end_word": 26,
      "text_line": "Успеть прикрыть бы спину",
      "text_test": "Успеть прикрыть бысь в пинну",
      "start_time": 46.58,
      "start_word": 22,
      "number_line": 5
    },
    {
      "ratio": 93,
      "end_time": 56.18,
      "end_word": 33,
      "text_line": "Я рада  ты живой пока",
      "text_test": "Я рада и ты живой и пока",
      "start_time": 53.66,
      "start_word": 27,
      "number_line": 6
    },
    {
      "ratio": 98,
      "end_time": 59.54,
      "end_word": 38,
      "text_line": "Я удержусь  я не покину",
      "text_test": "Я удержусь я не покину",
      "start_time": 56.76,
      "start_word": 34,
      "number_line": 7
    },
    {
      "ratio": 80,
      "end_time": 62.04,
      "end_word": 39,
      "text_line": "Звучит",
      "text_test": "Зучи",
      "start_time": 61.1,
      "start_word": 39,
      "number_line": 8
    },
    {
      "ratio": 91,
      "end_time": 72.14,
      "end_word": 40,
      "text_line": "Звучит",
      "text_test": "Звучи",
      "start_time": 71.76,
      "start_word": 40,
      "number_line": 9
    },
    {
      "ratio": 50,
      "end_time": 88.22,
      "end_word": 52,
      "text_line": "Как много песен порохом живёт во мне",
      "text_test": "Звучи Звучи Звучи Звучи Звучи Как много детьям пороха Мужи От вамне",
      "start_time": 72.14,
      "start_word": 41,
      "number_line": 10
    },
    {
      "ratio": 83,
      "end_time": 91.78,
      "end_word": 55,
      "text_line": "Ты не вернёшься",
      "text_test": "Ты не вернався",
      "start_time": 89.92,
      "start_word": 53,
      "number_line": 11
    },
    {
      "ratio": 82,
      "end_time": 97.18,
      "end_word": 60,
      "text_line": "А о тебе ещё никто не пел",
      "text_test": "А тебе еще никто не",
      "start_time": 94.02,
      "start_word": 56,
      "number_line": 12
    },
    {
      "ratio": 69,
      "end_time": 102.38,
      "end_word": 64,
      "text_line": "Ты не вернёшься",
      "text_test": "берем Ты не вернався",
      "start_time": 97.18,
      "start_word": 61,
      "number_line": 13
    },
    {
      "ratio": 92,
      "end_time": 107.48,
      "end_word": 69,
      "text_line": "И пролетают чёрные леса",
      "text_test": "И пролеют ают черные леса",
      "start_time": 104.52,
      "start_word": 65,
      "number_line": 14
    },
    {
      "ratio": 88,
      "end_time": 111.12,
      "end_word": 74,
      "text_line": "Успеть прикрыть бы спину",
      "text_test": "Успеть прикрыть бысь в пинну",
      "start_time": 107.88,
      "start_word": 70,
      "number_line": 15
    },
    {
      "ratio": 93,
      "end_time": 117.4,
      "end_word": 81,
      "text_line": "Я рада  ты живой пока",
      "text_test": "Я рада и ты живой и пока",
      "start_time": 115.16,
      "start_word": 75,
      "number_line": 16
    },
    {
      "ratio": 98,
      "end_time": 121.12,
      "end_word": 86,
      "text_line": "Я удержусь  я не покину",
      "text_test": "Я удержусь я не покину",
      "start_time": 118.02,
      "start_word": 82,
      "number_line": 17
    },
    {
      "ratio": 91,
      "end_time": 123.48,
      "end_word": 87,
      "text_line": "Звучит",
      "text_test": "Звучи",
      "start_time": 122.4,
      "start_word": 87,
      "number_line": 18
    },
    {
      "ratio": 91,
      "end_time": 124.36,
      "end_word": 88,
      "text_line": "Звучит",
      "text_test": "Звучи",
      "start_time": 123.56,
      "start_word": 88,
      "number_line": 19
    },
    {
      "ratio": 12,
      "end_time": 128.1,
      "end_word": 90,
      "text_line": "И пролетают чёрные леса",
      "text_test": "Звучи Звучи",
      "start_time": 124.64,
      "start_word": 89,
      "number_line": 20
    },
    {
      "ratio": 7,
      "end_time": 130.2,
      "end_word": 91,
      "text_line": "Успеть прикрыть бы спину",
      "text_test": "Звучи",
      "start_time": 128.5,
      "start_word": 91,
      "number_line": 21
    },
    {
      "ratio": 12,
      "end_time": 134.18,
      "end_word": 93,
      "text_line": "Я рада  ты живой пока",
      "text_test": "Звучи Звучи",
      "start_time": 133.02,
      "start_word": 92,
      "number_line": 22
    },
    {
      "ratio": 18,
      "end_time": 138,
      "end_word": 95,
      "text_line": "Я удержусь  я не покину",
      "text_test": "Звучи Звучи",
      "start_time": 136.24,
      "start_word": 94,
      "number_line": 23
    },
    {
      "ratio": 91,
      "end_time": 140.32,
      "end_word": 96,
      "text_line": "Звучит",
      "text_test": "Звучи",
      "start_time": 139.9,
      "start_word": 96,
      "number_line": 24
    },
    {
      "ratio": 91,
      "end_time": 142.04,
      "end_word": 97,
      "text_line": "Звучит",
      "text_test": "Звучи",
      "start_time": 140.5,
      "start_word": 97,
      "number_line": 25
    },
    {
      "ratio": 15,
      "end_time": 147.94,
      "end_word": 100,
      "text_line": "Прощальных белых поцелуев след во мне",
      "text_test": "Звучи Звучи Звучи",
      "start_time": 142.5,
      "start_word": 98,
      "number_line": 26
    },
    {
      "ratio": 10,
      "end_time": 150.02,
      "end_word": 101,
      "text_line": "Ты не вернёшься",
      "text_test": "Звучи",
      "start_time": 148.5,
      "start_word": 101,
      "number_line": 27
    }
  ],
  "meta": {},
  "published": 'true',
  "Author": "Ночные Снайперы",
  "Title": "Зву-чи!",
  "minRatio": 'null',
  "averageRatio": 'null'
}
update_entry('Music', '51e95230-3fcf-4551-9d82-45f13299b888', newData)
create_entry('Music', newData)