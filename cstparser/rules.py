import json
import os
import logging
import xml.etree.ElementTree as xml_parser
#from googletrans import Translator
from preprocess import normalize, nlp_analysis, get_sentence
from xml.sax.saxutils import escape, unescape



# translator = Translator()


numbers_conversion = {}
with open('resources/numbers_to_digit.json', 'r') as numbers_file:
    numbers_conversion = json.loads(''.join(numbers_file.readlines()))


attribution_verbs = {}
with open('resources/attribution_verbs.json', 'r') as attrib_file:
    attribution_verbs = json.loads(''.join(attrib_file.readlines()))


def rule_identity(sentence1, sentence2):
    s1 = normalize(sentence1, remove_stopwords=False)
    s2 = normalize(sentence2, remove_stopwords=False)
    if s1 == s2:
        return True
    else:
        return False


def rule_contradiction(ann1, ann2):
    # TODO parser errando muito???
    numbers1 = [token.text for token in ann1 if token.pos_ == "NUM"]
    numbers2 = [token.text for token in ann2 if token.pos_ == "NUM"]

    numbers1 = [numbers_conversion.get(n.lower(), n.lower()) for n in numbers1]
    numbers2 = [numbers_conversion.get(n.lower(), n.lower()) for n in numbers2]

    if len(numbers1) > 0 and len(numbers2) > 0:
        diff_numbers = [n for n in numbers1 if n not in numbers2]

        if len(diff_numbers) > 0:
            return True
    return False


def rule_indirect_attribution_citation(ann1, ann2):
    attribution_found = False
    conformity_found = False

    # analyze first sentence
    ok1 = False
    for token in ann1:
        # attribution verb ... que
        if attribution_verbs.get(token.lemma_.lower(), False):
            attribution_found = True
        if attribution_found and token.text.lower() == 'que':
            ok1 = True
            break
        # conforme|segundo|para ...
        if token.text.lower() in ['conforme', 'segundo']:
            conformity_found = True
        if conformity_found and (token.pos_ in ['NOUN', 'PROPN', 'DET', 'PRON']):
            ok1 = True
            break
        # TODO de acordo com ...

    # analyze second sentence
    ok2 = False
    for token in ann2:
        # contains verb in first person
        if token.pos_ == 'VERB' and ('1S' in token.tag_ or '1P' in token.tag_):
            ok2 = True

    if ok1 and ok2:
        return 'Indirect_Speech'
    elif ok1 or ok2:
        return 'Attribution'

    return False


"""TODO
recreate translation rule...

pt_words = {}
with open('resources/pt_words.json', 'r') as pt_words_file:
    pt_words = json.loads(''.join(pt_words_file.readlines()))
    

def rule_translation(ann1, ann2):
    not_pt1 = [token.text.lower() for token in ann1
               if ((token.pos_ not in ['NUM', 'PUNCT']) and (token.text.lower() not in pt_words))]
    not_pt2 = [token.text.lower() for token in ann2
               if ((token.pos_ not in ['NUM', 'PUNCT']) and (token.text.lower() not in pt_words))]

    try:
        translations1 = [translator.translate(
            word, dest='pt').text for word in not_pt1]
        translations2 = [translator.translate(
            word, dest='pt').text for word in not_pt2]
    except:
        logging.warning("Error during translation rule. Skipping the rule ...")
        return False

    tokens1 = [token.text.lower() for token in ann1]
    tokens2 = [token.text.lower() for token in ann2]

    for word in translations1:
        if word in tokens2:
            return True
    for word in translations2:
        if word in tokens1:
            return True
    return False
"""


def apply_rules(selected_pairs, analysis_path, embed):
    matched_rules = []
    for d1, d2 in selected_pairs:
        s1 = get_sentence(d1, analysis_path)
        s2 = get_sentence(d2, analysis_path)

        ann1 = nlp_analysis(s1)
        ann2 = nlp_analysis(s2)

        if rule_identity(s1, s2):
            matched_rules.append(["Identity", d1[0], d1[1], d2[0], d2[1]])
        if rule_contradiction(ann1, ann2):
            matched_rules.append(["Contradiction", d1[0], d1[1], d2[0], d2[1]])
        # if rule_translation(ann1, ann2):
        #     matched_rules.append(["Translation", d1[0], d1[1], d2[0], d2[1]])

        # both directions
        # s1 -> s2
        result = rule_indirect_attribution_citation(ann1, ann2)
        if result:
            matched_rules.append([result, d1[0], d1[1], d2[0], d2[1]])
        # s2 -> s1
        result = rule_indirect_attribution_citation(ann2, ann1)
        if result:
            matched_rules.append([result, d2[0], d2[1], d1[0], d1[1], ])

    with open(os.path.join(analysis_path, 'CST.xml'), 'w') as cst_file:
        cst_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        cst_file.write('\t<RELATIONS>\n')
        for rule, sd, ss, td, ts in matched_rules:
            if embed:
                s1 = get_sentence([sd, ss], analysis_path)
                s2 = get_sentence([td, ts], analysis_path)
                cst_file.write(
                    '\t\t<R SDID="{}" SSENT="{}" TDID="{}" TSENT="{}">\n'.format(sd, escape(s1), td, escape(s2)))
            else:
                cst_file.write(
                    '<\t\tR SDID="{}" SSENT="{}" TDID="{}" TSENT="{}">\n'.format(sd, escape(ss), td, escape(ts)))
            cst_file.write(
                '\t\t\t<RELATION TYPE="{}" JUDGE="CSTParser_rule"/>\n'.format(rule))
            cst_file.write('\t\t</R>\n')
