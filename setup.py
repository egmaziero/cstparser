from setuptools import setup

setup(name='cstparser',
      version='0.1',
      description='Cross-document Structure Theory Parser for Brazilian Portuguese',
      url='http://github.com/egmaziero/cstparser',
      author='Erick Galani Maziero',
      author_email='egmaziero@gmail.com',
      license='MIT',
      packages=['cstparser'],
      install_requires=['nltk', 
      					'joblib',
      					'unidecode',
      					'spacy',
      					'sklearn'],
      scripts=['bin/download_spacy_model.py'])