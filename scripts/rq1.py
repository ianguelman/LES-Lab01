from math import ceil
import os
from unittest import result
from utils.graphql import GraphQL

TOTAL_ITEMS = 1000
PER_PAGE = 100


def run():
    nodes = []
    graphql = GraphQL(os.environ["API_URL"])
    lastCursor = None

    for x in range(0, ceil(TOTAL_ITEMS/PER_PAGE)):
        response = graphql.post(
            """
            query ($lastCursor: String, $perPage: Int) {
                search(query: "stars:>100", type: REPOSITORY, after: $lastCursor, first: $perPage) {
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
            """, {"lastCursor": lastCursor,
                  "perPage": min(PER_PAGE, TOTAL_ITEMS, (TOTAL_ITEMS - len(nodes)))}
        )

        print(response)

        if not response["data"]["search"]["pageInfo"]["hasNextPage"]:
            break

        lastCursor = response["data"]["search"]["pageInfo"]["endCursor"]

        nodes = nodes + response["data"]["search"]["nodes"]

    print(len(nodes))
