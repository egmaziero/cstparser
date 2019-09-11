import os
import logging
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MinMaxScaler
from preprocess import get_sentence
from joblib import load
from xml.sax.saxutils import escape, unescape


classifier = load('models/mlp_multiclass_classifier.joblib')
scaler = load('models/scaler.joblib')
label_encoder = load('models/label_encoder.joblib')


def write_results(selected_pairs, results, analysis_path, embed):

    with open(os.path.join(analysis_path, 'CST.xml'), 'a+') as cst_file:
        for i, (d1, d2) in enumerate(selected_pairs):
            if embed:
                s1 = get_sentence(d1, analysis_path)
                s2 = get_sentence(d2, analysis_path)
                cst_file.write('\t\t<R SDID="{}" SSENT="{}" TDID="{}" TSENT="{}">\n'.format(
                    d1[0], escape(s1), d2[0], escape(s2)))
            else:
                cst_file.write('<\t\tR SDID="{}" SSENT="{}" TDID="{}" TSENT="{}">\n'.format(
                    d1[0], escape(d1[1]), d2[0], escape(d2[1])))
            cst_file.write(
                '\t\t\t<RELATION TYPE="{}" JUDGE="CSTParser_classifier"/>\n'.format(results[i]))
            cst_file.write('\t\t</R>\n')


def multiclass_classify(selected_pairs, features, analysis_path, embed):
    if len(features) > 0:
        results = classifier.predict(features)
        results = [label_encoder.inverse_transform([r])[0] for r in results]
        write_results(selected_pairs, results, analysis_path, embed)
    else:
        logging.info('No instances to classify ...')

    # closing cst xml file
    with open(os.path.join(analysis_path, 'CST.xml'), 'a+') as cst_file:
        cst_file.write('\t</RELATIONS>\n')
