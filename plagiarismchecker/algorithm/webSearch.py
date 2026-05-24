from googleapiclient.discovery import build

from plagiarismchecker.algorithm.CosineSim import (
    cosineSim
)

from plagiarismchecker.algorithm.semantic_similarity import (
    detect_plagiarism
)

from plagiarismchecker.utils.fetch_content import (
    fetch_page_text
)

import socket

# Better timeout
socket.setdefaulttimeout(10)

# GOOGLE API
searchEngine_API = 'YOUR_API_KEY'

searchEngine_Id = 'YOUR_SEARCH_ENGINE_ID'


def searchWeb(text, output, c):

    try:

        resource = build(
            "customsearch",
            "v1",
            developerKey=searchEngine_API,
            cache_discovery=False
        ).cse()

        result = resource.list(
            q=text,
            cx=searchEngine_Id
        ).execute()

        # No results
        if 'items' not in result:

            return output, c, 0

        searchInfo = result['searchInformation']

        if int(searchInfo['totalResults']) > 0:

            maxSim = 0

            bestSnippet = ""

            itemLink = ""

            numList = len(result['items'])

            # LIMIT RESULTS
            if numList > 5:
                numList = 5

            for i in range(numList):

                item = result['items'][i]

                link = item['link']

                # FETCH REAL WEBPAGE CONTENT
                page_text = fetch_page_text(link)

                # Skip empty pages
                if not page_text:
                    continue

                # COSINE SIMILARITY
                cosine_score = cosineSim(
                    text.lower(),
                    page_text.lower()
                )

                # SEMANTIC SIMILARITY
                semantic_result = detect_plagiarism(
                    text,
                    page_text,
                    threshold=0.15
                )

                semantic_score = (
                    semantic_result['overall_score']
                    / 100
                )

                # FINAL COMBINED SCORE
                simValue = (
                    (cosine_score * 0.4)
                    +
                    (semantic_score * 0.6)
                )

                # SAVE BEST MATCH
                if simValue > maxSim:

                    maxSim = simValue

                    itemLink = link

                    bestSnippet = page_text[:300]

            # No usable match
            if not itemLink:

                return output, c, 0

            # EXISTING MATCH
            if itemLink in output:

                output[itemLink]['count'] += 1

                old_avg = output[itemLink]['similarity']

                new_avg = (

                    (
                        old_avg
                        *
                        (
                            output[itemLink]['count']
                            - 1
                        )
                    )

                    + maxSim

                ) / output[itemLink]['count']

                output[itemLink]['similarity'] = new_avg

            # NEW MATCH
            else:

                output[itemLink] = {

                    'count': 1,

                    'similarity': maxSim,

                    'snippet': bestSnippet,

                    'source': itemLink
                }

                c[itemLink] = maxSim

    except Exception as e:

        print("========== ERROR ==========")

        print("TEXT:", text)

        print("ERROR:", str(e))

        print("===========================")

        return output, c, 1

    return output, c, 0