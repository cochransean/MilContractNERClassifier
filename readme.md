### Goal: To classify postings to the Department of Defense's Contract Press Release page by organization, date, and monetary value, allowing for more data-driven analysis.

### Install Stanford's Core NLP from their website
http://stanfordnlp.github.io/CoreNLP/

### Stanford Core NLP
### Getting Started
Stanford CoreNLP ships with a built-in server, and requires only the CoreNLP dependencies. To run this server, simply run:

### Set up your classpath. For example, to add all jars in the current directory tree:
export CLASSPATH="`find . -name '*.jar'`"

### Run the server (from the core NLP directory)
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer [port?]
If no value for port is provided, port 9000 will be used by default. You can then test your server by visiting

http://localhost:9000/

### Note: this uses the Standford Core NLP wrapper from
https://github.com/smilli/py-corenlp
