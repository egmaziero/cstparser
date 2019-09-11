import nltk
import joblib
import os
import spacy
import unidecode
import string
import xml.etree.ElementTree as xml_parser
import datetime
from xml.sax.saxutils import escape


annotator = spacy.load('pt_core_news_sm')

stopwords = ["a", "à", "ah", "ai", "algo", "alguém", "algum", "alguma", "algumas",
             "alguns", "alô", "ambos", "ante", "ao", "apenas", "após", "aquela",
             "aquelas", "aquele", "aqueles", "aquilo", "as", "até", "bis", "cada",
             "certa", "certas", "certo", "certos", "chi", "com", "comigo", "conforme",
             "conosco", "consigo", "contigo", "contra", "convosco", "cuja", "cujas",
             "cujo", "cujos", "da", "das", "de", "dela", "delas", "dele", "deles",
                     "desde", "dessa", "dessas", "desse", "desses", "disso", "desta", "destas",
                     "deste", "destes", "disto", "daquela", "daquelas", "daquele", "daqueles",
                     "daquilo", "do", "dos", "e", "eia", "ela", "elas", "ele", "eles", "em",
                     "embora", "enquanto", "entre", "essa", "essas", "esse", "esses", "esta",
                     "este", "estes", "estou", "eu", "hem", "hum", "ih", "isso", "isto", "lhe",
                     "lhes", "logo", "mais", "mas", "me", "menos", "mesma", "mesmas", "mesmo",
                     "mesmos", "meu", "meus", "mim", "minha", "minhas", "muita", "muitas",
                     "muito", "muitos", "na", "nada", "nas", "nela", "nelas", "nele", "neles",
                     "nem", "nenhum", "nenhuma", "nenhumas", "nenhuns", "ninguém", "no", "nos",
                     "nós", "nossa", "nossas", "nosso", "nossos", "nela", "nelas", "nele",
                     "neles", "nessa", "nessas", "nesse", "nesses", "nisso", "nesta", "nestas",
                     "neste", "nestes", "nisto", "naquela", "naquelas", "naquele", "naqueles",
                     "naquilo", "o", "ó", "ô", "oba", "oh", "olá", "onde", "opa", "ora", "os",
                     "ou", "outra", "outras", "outrem", "outro", "outros", "para", "pelo",
                     "pela", "pelos", "pelas", "per", "perante", "pois", "por", "porém",
                     "porque", "portanto", "pouca", "poucas", "pouco", "poucos", "próprios",
                     "psit", "psiu", "quais", "quaisquer", "qual", "qualquer", "quando",
                     "quanta", "quantas", "quanto", "quantos", "que", "quem", "se", "sem",
                     "seu", "seus", "si", "sob", "sobre", "sua", "suas", "talvez", "tanta",
                     "tantas", "tanto", "tantos", "te", "teu", "teus", "ti", "toda", "todas",
                     "todo", "todos", "trás", "tu", "tua", "tuas", "tudo", "ué", "uh", "ui",
                     "um", "uma", "umas", "uns", "vária", "várias", "vário", "vários", "você",
                     "vós", "vossa", "vossas", "vosso", "vossos", "ser", "estar"]


def nlp_analysis(sentence):
    return annotator(sentence)


def get_sentence(d, analysis_path):
    doc_id, sentence_number = d
    with open(os.path.join(analysis_path, 'sentences_doc_{}.xml'.format(doc_id)), 'r') as xml_file:
        parsed_text = xml_parser.parse(xml_file)
        root = parsed_text.getroot()
        sentences = root.findall('BODY/TEXT/S')
        for s in sentences:
            if s.get('SNO') == sentence_number:
                return s.text.replace('"', "&quot;")


def get_number_of_sentences(d, analysis_path):
    doc_id, sentence_number = d
    with open(os.path.join(analysis_path, 'sentences_doc_{}.xml'.format(doc_id)), 'r') as xml_file:
        parsed_text = xml_parser.parse(xml_file)
        root = parsed_text.getroot()
        sentences = root.findall('BODY/TEXT/S')
        return sentences[-1].get('SNO')


def sentence_tokenization(text):
    try:
        sent_detector = joblib.load('tools/sent_detector.dump')
    except:
        sent_detector = nltk.data.load('tokenizers/punkt/portuguese.pickle')
        with open('tools/sent_detector.dump', 'wb') as dump_file:
            joblib.dump(sent_detector, dump_file)

    return sent_detector.tokenize(text)


def preprocessing(texts, analysis_path):
    if not os.path.isdir(analysis_path):
        os.mkdir(analysis_path)

    today_date = datetime.date.today()
    new_today_date = today_date.strftime("%d/%m/%Y")

    created_files = []

    for i, text in enumerate(texts):
        sentences = sentence_tokenization(text)

        with open(os.path.join(analysis_path, 'sentences_doc_{}.xml'.format(i)), 'w') as sentences_xml:
            created_files.append(os.path.join(
                analysis_path, 'sentences_doc_{}.xml'.format(i)))
            sentences_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            sentences_xml.write('<DOCSENT DID="doc_{}">\n'.format(i))
            sentences_xml.write('\t<BODY>\n')
            sentences_xml.write(
                '\t\t<DATE-INFO DATE="{}"></DATE-INFO>\n'.format(new_today_date))
            sentences_xml.write('\t\t<TEXT>\n')
            for j, sentence in enumerate(sentences):
                sentences_xml.write(
                    '\t\t\t<S SNO="{}">{}</S>\n'.format(j, escape(sentence)))
            sentences_xml.write('\t\t</TEXT>\n')
            sentences_xml.write('\t</BODY>\n')
            sentences_xml.write('</DOCSENT>\n')

    return created_files


def normalize(text, remove_stopwords=True, remove_punctuation=True, remove_accents=True, lower=True):
    if remove_punctuation:
        text = text.translate(str.maketrans('', '', string.punctuation))
    if remove_accents:
        text = unidecode.unidecode(text)
    if lower:
        text = text.lower()
    if remove_stopwords:
        tokens = nltk.tokenize.word_tokenize(text)
        tokens = [t for t in tokens if t not in stopwords]
        text = ' '.join(tokens)

    return text


def tokenize_words(text):
    return nltk.tokenize.word_tokenize(text)


def word_overlap(text1, text2):
    tokens1 = tokenize_words(normalize(text1))
    tokens2 = tokenize_words(normalize(text2))
    matches = [1 for t in tokens1 if t in tokens2]

    return sum(matches) / (len(tokens1) + len(tokens2))


def select_pairs(texts, word_overlap_threshold=0.12):
    selected_pairs = []
    for i in range(0, len(texts)):
        xml_file = texts[i]
        parsed_text = xml_parser.parse(xml_file)
        for S in parsed_text.getroot().findall('BODY/TEXT/S'):
            sentence1_text = S.text
            sentence1_id = S.get('SNO')
            for j in range(i + 1, len(texts)):
                xml_file = texts[j]
                parsed_text = xml_parser.parse(xml_file)
                for S in parsed_text.getroot().findall('BODY/TEXT/S'):
                    sentence2_text = S.text
                    sentence2_id = S.get('SNO')

                    if word_overlap(sentence1_text, sentence2_text) >= word_overlap_threshold:
                        selected_pairs.append(
                            [(i, sentence1_id), (j, sentence2_id)])
    return selected_pairs
