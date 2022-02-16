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
        query popularRepositories($perPage: Int) {
            search(query: "stars:>100", type: REPOSITORY, first: $perPage) {
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
        """, {"perPage": PER_PAGE}
    )

    nodes = nodes + response["data"]["search"]["nodes"]

    for x in range(1, int(TOTAL_ITEMS/PER_PAGE)):
        response = graphql.post(
            """
            query ($lastCursor: String, $perPage: Int) {
                search(query: "stars:>100", type: REPOSITORY, before: $lastCursor, first: $perPage) {
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
            """, {"lastCursor": response["data"]["search"]["pageInfo"]["endCursor"],
                  "perPage": PER_PAGE}
        )
        print(response)
        nodes = nodes + response["data"]["search"]["nodes"]

    print(len(nodes))
