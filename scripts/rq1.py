import os
from unittest import result
from utils.graphql import GraphQL

TOTAL_ITEMS = 1000
PER_PAGE = 100

def run():
    nodes = []
    graphql = GraphQL(os.environ["API_URL"])
    response = graphql.post(
        """
        query popularRepositories {
            search(query: "stars:>100", type: REPOSITORY, first: 100) {
                nodes {
                ... on Repository {
                        nameWithOwner
                        url
                        createdAt
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }    
        }
        """, {}
    )
    nodes = nodes + response["data"]["search"]["nodes"]
    for x in range(1, 10):
        response = graphql.post(
            """
            query ($lastCursor: String) {
                search(query: "stars:>100", type: REPOSITORY, before: $lastCursor, first: 100) {
                    nodes {
                    ... on Repository {
                            nameWithOwner
                            url
                            createdAt
                        }
                    }
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                }    
            }
            """, { "lastCursor" : response["data"]["search"]["pageInfo"]["endCursor"]}
        )
        print(response)
        nodes = nodes + response["data"]["search"]["nodes"]
    print(len(nodes))