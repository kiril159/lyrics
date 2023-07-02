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
        variables["filters"] = [{"field": "idS3", "operator": "ILIKE", "value": s3Id}]

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