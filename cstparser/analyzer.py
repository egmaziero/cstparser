import argparse
import os
import logging
import sys
from preprocess import preprocessing, select_pairs
from rules import apply_rules
from feature_extraction import extract_features
from classifiers import multiclass_classify


word_overlap_threshold = 0.12

logging.basicConfig(level=logging.INFO)

embed = False


def analyze():
    parser = argparse.ArgumentParser(description='CST Parser command line')
    parser.add_argument("--d", help="path of directory with the texts",
                        required=True, action="store", dest="directory_path")
    parser.add_argument("--o", help="path of directory to store results",
                        required=True, action="store", dest="analysis_path")
    parser.add_argument("--e", help="embed sentence text into cst analysis",
                        required=False, action="store", dest="embed")

    args = parser.parse_args()

    texts = []

    logging.info('Getting documents ...')
    files = os.listdir(args.directory_path)

    # if macOS
    files = [f for f in files if f != '.DS_Store']

    for f in files:
        try:
            with open(os.path.join(args.directory_path, f), 'r') as file:
                lines = file.readlines()
                texts.append(''.join(lines))
        except:
            print("The following error occurred while opening file {}: ".format(
                os.path.join(args.directory_path, f)), sys.exc_info()[0])
            raise

    """
	Prepare XML data with files tokenized by sentence
	"""
    logging.info('Preprocessing documents ...')
    generated_files = preprocessing(texts, args.analysis_path)

    """
	Select pairs of sentence to be related using word overlap
	"""
    logging.info('Selecting candidate sentence pairs ...')
    selected_pairs = select_pairs(generated_files, 0.12)

    """
	Apply rules on selected pairs
	"""
    logging.info('Applying rules ...')
    apply_rules(selected_pairs, args.analysis_path, args.embed)

    """
	Extract features
	"""
    logging.info('Extracting features ...')
    features = extract_features(selected_pairs, args.analysis_path)

    """
	Applying classifier
	"""
    logging.info('Applying classifier ...')
    multiclass_classify(selected_pairs, features,
                        args.analysis_path, args.embed)

    logging.info('Done! CST analysis out at {}'.format(args.analysis_path))


if __name__ == '__main__':
    analyze()
