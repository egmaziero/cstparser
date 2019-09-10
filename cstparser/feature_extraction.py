import json
from preprocess import nlp_analysis, get_sentence, get_number_of_sentences, normalize, tokenize_words, stopwords


synsets = {}
with open('resources/synonyms.json', 'r') as syn_file:
    synsets = json.loads(''.join(syn_file.readlines()))


attribution_verbs = {}
with open('resources/attribution_verbs.json', 'r') as attrib_file:
    attribution_verbs = json.loads(''.join(attrib_file.readlines()))


def get_word_from_class(annotation, class_):
    words = [token.text for token in annotation if token.pos_ == class_]
    return words


def get_attribution_verbs(annotation):
    found_attribution_verbs = []
    for token in annotation:
        if token.lemma_ in attribution_verbs:
            found_attribution_verbs.append(token)
    return found_attribution_verbs


def get_longest_substr(s1, s2):
    m = len(s1)
    n = len(s2)

    longest_suff = [[0 for k in range(n+1)] for l in range(m+1)]
    size = 0
    for i in range(m + 1):
        for j in range(n + 1):
            if (i == 0 or j == 0):
                longest_suff[i][j] = 0
            elif (s1[i-1] == s2[j-1]):
                longest_suff[i][j] = longest_suff[i-1][j-1] + 1
                size = max(size, longest_suff[i][j])
            else:
                longest_suff[i][j] = 0
    return size


def count_synonym_overlaps(annotation1, annotation2):
    synonym_count = 0

    for token1 in annotation1:
        if token1.lemma_ not in stopwords:
            synset1 = synsets.get(token1.lemma_, None)
            if synset1 is not None:
                for token2 in annotation2:
                    if token2.lemma_ not in stopwords:
                        synset2 = synsets.get(token2.lemma_, None)
                        if synset2 is not None:
                            if len([s for s in synset1 if s in synset2]) > 0:
                                synonym_count += 1
                                break
    return synonym_count


def feature_extraction(sentence1, sentence1_position, sentence2, sentence2_position):
    features = []

    # 1 number of word s1 - s2
    s1 = normalize(sentence1, remove_stopwords=False)
    s2 = normalize(sentence2, remove_stopwords=False)

    tokens1 = tokenize_words(s1)
    tokens2 = tokenize_words(s2)
    features.append(len(tokens1) - len(tokens2))

    # 2 % common words in s1
    common_tokens = [t1 for t1 in tokens1 if t1 in tokens2]
    features.append(len(common_tokens) / len(tokens1))

    # 3 % common words in s2
    features.append(len(common_tokens) / len(tokens2))

    # 4 position of s1 (0 start, 1 middle, 2 end)
    features.append(sentence1_position)

    # 5 position of s2 (0 start, 1 middle, 2 end)
    features.append(sentence2_position)

    # 6 number of words in the biggest substring between s1 and s2
    features.append(get_longest_substr(s1, s2))

    annotation1 = nlp_analysis(sentence1)
    annotation2 = nlp_analysis(sentence2)

    # 7 diff in number of nouns
    nouns1 = get_word_from_class(annotation1, 'NOUN')
    nouns2 = get_word_from_class(annotation2, 'NOUN')
    features.append(len(nouns1) - len(nouns2))

    # 8 diff in number of adverbs
    adverbs1 = get_word_from_class(annotation1, 'ADV')
    adverbs2 = get_word_from_class(annotation2, 'ADV')
    features.append(len(adverbs1) - len(adverbs2))

    # 9 diff in number of adjectives
    adjectives1 = get_word_from_class(annotation1, 'ADJ')
    adjectives2 = get_word_from_class(annotation2, 'ADJ')
    features.append(len(adjectives1) - len(adjectives2))

    # 10 diff in number of verbs
    verbs1 = get_word_from_class(annotation1, 'VERB')
    verbs2 = get_word_from_class(annotation2, 'VERB')
    features.append(len(verbs1) - len(verbs2))

    # 11 diff in number of proper nouns (not lowered text)
    propnouns1 = get_word_from_class(annotation1, 'PROP-NOUN')
    propnouns2 = get_word_from_class(annotation2, 'PROP-NOUN')
    features.append(len(propnouns1) - len(propnouns2))

    # 12 diff in number of numerals
    numerals1 = get_word_from_class(annotation1, 'NUM')
    numerals2 = get_word_from_class(annotation2, 'NUM')
    features.append(len(numerals1) - len(numerals2))

    # 13 diff in number of attribution verbs
    attribverbs1 = get_attribution_verbs(annotation1)
    attribverbs2 = get_attribution_verbs(annotation2)
    features.append(len(attribverbs1) - len(attribverbs2))

    # 14 overlap of sinonyms
    features.append(count_synonym_overlaps(annotation1, annotation2))

    return features


def extract_features(selected_pairs, analysis_path):
    features = []

    for d1, d2 in selected_pairs:
        s1 = get_sentence(d1, analysis_path)
        s2 = get_sentence(d2, analysis_path)

        ann1 = nlp_analysis(s1)
        ann2 = nlp_analysis(s2)

        if d1[1] == 0:
            sentence1_position = 0
        elif d1[1] == get_number_of_sentences(d1, analysis_path):
            sentence1_position = 2
        else:
            sentence1_position = 1

        if d2[1] == 0:
            sentence2_position = 0
        elif d2[1] == get_number_of_sentences(d2, analysis_path):
            sentence2_position = 2
        else:
            sentence2_position = 1

        features.append(feature_extraction(
            s1, sentence1_position, s2, sentence2_position))

    return features
