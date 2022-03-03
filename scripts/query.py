from math import ceil
import os
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
            nodes = nodes + response["data"]["search"]["nodes"]

            print('{} nodes of {}'.format(len(nodes), TOTAL_ITEMS))

            if not response["data"]["search"]["pageInfo"]["hasNextPage"]:
                break


        Mongo().insert_many(nodes)    

    else:
        print(f"DB já populado com {itemsCount} itens")    

