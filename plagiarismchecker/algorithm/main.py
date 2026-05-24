import nltk

nltk.download('stopwords')

from nltk.corpus import stopwords

from plagiarismchecker.algorithm import webSearch

import sys
import re


# GENERATE SEARCH QUERIES


def getQueries(text, n):

    sentenceEnders = re.compile("['.!?]")

    sentenceList = sentenceEnders.split(text)

    sentencesplits = []

    en_stops = set(stopwords.words('english'))

    for sentence in sentenceList:

        x = re.compile(
            r'\W+',
            re.UNICODE
        ).split(sentence)

        # Remove stopwords
        x = [
            word
            for word in x
            if word.lower() not in en_stops
        ]

        x = [
            ele
            for ele in x
            if ele != ''
        ]

        sentencesplits.append(x)

    finalq = []

    for sentence in sentencesplits:

        l = len(sentence)

        if l > n:

            l = int(l / n)

            index = 0

            for i in range(0, l):

                finalq.append(
                    sentence[index:index+n]
                )

                index = index + n - 1

                if index + n > l:

                    index = l - n - 1

            if index != len(sentence):

                finalq.append(
                    sentence[
                        len(sentence)-index:
                        len(sentence)
                    ]
                )

        else:

            if l > 2:

                finalq.append(sentence)

    return finalq


# FIND SIMILARITY
def findSimilarity(text):

    # Smaller chunks = better detection
    n = 6

    queries = getQueries(text, n)

    print('GetQueries task complete')

    q = [' '.join(d) for d in queries]

    output = {}

    c = {}

    while("" in q):
        q.remove("")

    count = len(q)

    # Limit API usage
    if count > 20:
        count = 20

    numqueries = count

    for s in q[0:count]:

        output, c, errorCount = webSearch.searchWeb(
            s,
            output,
            c
        )

        print('Web search task complete')

        numqueries = numqueries - errorCount

        sys.stdout.flush()

    # Prevent divide by zero
    if numqueries <= 0:
        numqueries = 1

    totalPercent = 0

    outputLink = {}

    for link in output:

        percentage = (
            output[link]['count']
            *
            output[link]['similarity']
            *
            100
        ) / numqueries

        if percentage > 5:

            totalPercent += percentage

            outputLink[link] = {

                'percentage': round(
                    percentage,
                    2
                ),

                'snippet': output[link]['snippet'],

                'source': output[link]['source']
            }

    # Limit score
    if totalPercent > 100:
        totalPercent = 100

    print(totalPercent, outputLink)

    print("\nDone!")

    return round(totalPercent, 2), outputLink