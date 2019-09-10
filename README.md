# CSTParser

```cstparser``` is a multi-document semantic/discoursive analyzer for Brazilian Portuguese.

### Installation
```cstparser``` can be installed in two ways:

- clonning this repository:
```git clone https://github.com/egmaziero/cstparser.git```.   
- Using pip:
```pip install cstparser```

### Dependencies
If you cloned this repository. Install dependencies using

```pip install -r requirements.txt```.

```spacy``` will be installed, but you need to install Portuguese model. To do this, run the script in bin directory:

```python3 bin\download_spacy_model.py```
 

### Basic usage
```cstparser``` performs multi-document analysis on a group of documents. They need to be in the same directory, as simple text. To run the parser use:

```python3 cstparser\analyzer.py --d directory_path --o directory_output --e False/True```


### Citation

To cite this tool, use the following reference:

>Maziero, E.G.; Castro Jorge, M.L.R.; Pardo, T.A.S. (2014). Revisiting Cross-document Structure Theory for multi-document discourse parsing. _Information Processing & Management_, Vol. 50, N. 2, pp. 297-314.