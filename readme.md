## Goal: To classify postings to the Department of Defense's Contract Press Release page by organization, date, and monetary value, allowing for more data-driven analysis.

The Jupyter notebook shows the workflow and steps that were taken to split up the messy, scraped data from [this project](https://github.com/cochransean/DefenseContractsScraper).

`NER_tagger.py` contains the script that was used to feed the wrangled data into the natural language tagger.

The tagged, most current data is in the files `consolidated_contracts_ner_tags.csv` and `consolidated_contracts_ner_tags_json.txt`.

## Development Environment Setup:
#### Install Stanford's Core NLP from their website
`http://stanfordnlp.github.io/CoreNLP/`

#### Stanford Core NLP: Getting Started
Stanford CoreNLP ships with a built-in server, and requires only the CoreNLP dependencies. To run this server, simply:

#### Set up your classpath. For example, to add all jars in the current directory tree:
export CLASSPATH="`find . -name '*.jar'`"

#### Run the server (from the core NLP directory)
`java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer [port?]`
If no value for port is provided, port 9000 will be used by default. You can then test your server by visiting

`http://localhost:9000/`

There were initially issues with unprintable UNICODE characters, so ensure that all input is sanitized down to printable characters.

Note: this uses the Standford Core NLP wrapper from
`https://github.com/smilli/py-corenlp`

