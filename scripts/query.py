from math import ceil
import os
from types import NoneType
from utils.graphql import GraphQL
from utils.mongo import Mongo

TOTAL_ITEMS = 1000
PER_PAGE = 25

def run():
    itemsCount = Mongo().get_documents_count()

    if itemsCount < TOTAL_ITEMS:
        nodes = []
        graphql = GraphQL(os.environ["API_URL"])
        lastCursor = None

        for x in range(0, ceil(TOTAL_ITEMS / PER_PAGE)):
            response = graphql.post(
                """
                query popularRepositories ($lastCursor: String, $perPage: Int) {
                    search(query: "stars:>100", type: REPOSITORY, after: $lastCursor, first: $perPage) {
                        nodes {
                        ... on Repository {
                                nameWithOwner
                                url
                                stargazerCount
                                createdAt
                                pullRequests(first: 10, states: MERGED) {
                                    totalCount
                                }
                                releases {
                                    totalCount
                                }
                                updatedAt
                                primaryLanguage {
                                    name
                                }
                                issues (first: 10){
                                    totalCount
                                }
                                closed: issues(first: 10, states: CLOSED) {
                                    totalCount
                                }
                            }
                        }
                        pageInfo {
                            endCursor
                            hasNextPage
                        }
                    }
                }
                """,
                {
                    "lastCursor": lastCursor,
                    "perPage": min(PER_PAGE, TOTAL_ITEMS, (TOTAL_ITEMS - len(nodes))),
                },
            )
            
            lastCursor = response["data"]["search"]["pageInfo"]["endCursor"]
            
            formatter = lambda node : {
                "nameWithOwner": node["nameWithOwner"],
                "url" : node["url"],
                "stargazerCount": node["stargazerCount"],
                "createdAt": node["createdAt"],
                "pullRequests": node["pullRequests"]["totalCount"],
                "releases": node["releases"]["totalCount"],
                "updatedAt": node["updatedAt"],
                "primaryLanguage": 
                    None
                    if isinstance(node["primaryLanguage"], NoneType) 
                    else node["primaryLanguage"]["name"],
                "issues": node["issues"]["totalCount"],
                "closed": node["closed"]["totalCount"],
            }
            
            nodes = nodes + list(map(formatter, response["data"]["search"]["nodes"]))

            print('{} nodes of {}'.format(len(nodes), TOTAL_ITEMS))

            if not response["data"]["search"]["pageInfo"]["hasNextPage"]:
                break


        Mongo().insert_many(nodes)    

    else:
        print(f"DB já populado com {itemsCount} itens")    

