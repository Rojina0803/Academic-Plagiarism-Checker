from sentence_transformers import SentenceTransformer
from sentence_transformers import util

import nltk

from nltk.tokenize import sent_tokenize

nltk.download('punkt')

# LOAD MODEL
model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)


def detect_plagiarism(
    text1,
    text2,
    threshold=0.15
):

    sentences1 = sent_tokenize(text1)

    sentences2 = sent_tokenize(text2)

    # EMPTY CHECK
    if not sentences1 or not sentences2:

        return {
            'overall_score': 0,
            'matches': []
        }

    # EMBEDDINGS
    embeddings1 = model.encode(
        sentences1,
        convert_to_tensor=True
    )

    embeddings2 = model.encode(
        sentences2,
        convert_to_tensor=True
    )

    matches = []

    highest_similarity = 0

    # COMPARE
    for i, sentence1 in enumerate(sentences1):

        for j, sentence2 in enumerate(sentences2):

            similarity = util.cos_sim(
                embeddings1[i],
                embeddings2[j]
            ).item()

            # TRACK BEST SCORE
            if similarity > highest_similarity:

                highest_similarity = similarity

            # SAVE MATCH
            if similarity >= threshold:

                matches.append({

                    'original': sentence1,

                    'matched': sentence2,

                    'similarity': round(
                        similarity * 100,
                        2
                    )
                })

    overall_score = round(
        highest_similarity * 100,
        2
    )

    return {

        'overall_score': overall_score,

        'matches': matches
    }