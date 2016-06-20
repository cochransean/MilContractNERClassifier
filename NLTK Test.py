import csv
from pycorenlp import StanfordCoreNLP
import time
import re
import ast

# TODO fix Sep 11, 2006 to Nov 15, 2006 and November 29, 2006 to Dec 4, 2006 data (not separated)
# TODO try this regex to find seperators between the large blocks of text \([a-zA-z0-9-]{6,}[0-9]{3,}\)
# TODO find items with more than one match maybe with
# TODO (\([a-zA-z0-9-]{8,}[0-9]{3,}\)).{300,}(\([a-zA-z0-9-]{8,}[0-9]{3,}\))
# setup variables and server
dates = []
results = []
nlp = StanfordCoreNLP('http://localhost:9000')


def ner_tag_text():

    # load data
    try:
        with open('consolidated_contracts_split.csv', 'r') as csvfile:
            contract_reader = csv.DictReader(csvfile)
            for row in contract_reader:
                dates.append({'date': row['date'], 'announcements': ast.literal_eval(row['announcement'])})
    except IOError:
        print("Error loading data.")
    else:
        print("Data loaded.")

    classifiers_to_output = {
        'ORGANIZATION': 'organization',
        'MONEY': 'value',
        'LOCATION': 'location',
        'DATE': 'dates_in_announcement'
    }

    # loop through each press release
    for date in dates:
        for contract in date['announcements']:

            tagged_contract = []
            annotated_text = None
            # get text of release
            successful = False
            number_of_tries = 0
            while not successful and number_of_tries < 10:
                annotated_text = nlp.annotate(contract, properties={
                    'annotators': 'ner',
                    'outputFormat': 'json'
                })
                # check for errors and repeat if needed (server sometimes can't handle requests)
                if type(annotated_text) == str:
                    print('Error with server: ' + annotated_text)
                    # pause in case server is overloaded
                    time.sleep(5)
                    number_of_tries += 1
                    if number_of_tries >= 10:
                        print('10 failed tries with server. Saving current results and exiting.')
                        return
                else:
                    successful = True

            # create dict to store output
            entry = dict()
            entry.update({'press_release': contract, 'date_of_announcement': date['date']})
            # track current list index for each output type
            output_index = {}
            for output in classifiers_to_output.values():
                entry[output] = []
                output_index[output] = 0

            # loop through sentences
            for sentence in annotated_text['sentences']:
                # loop through words and punctuation
                for current_token, next_token in zip(sentence['tokens'], sentence['tokens'][1:]):
                    for classifier, output in classifiers_to_output.items():
                        # make sure current word and next match classifier (to separate identical matches in sentence)
                        if current_token['ner'] == classifier:
                            # add space to list if it isn't there
                            if len(entry[output]) < output_index[output] + 1:
                                entry[output].append('')
                            # include any spaces between words
                            entry[output][output_index[output]] += current_token['originalText'] + current_token['after']
                            if next_token['ner'] != classifier:
                                output_index[output] += 1
                tagged_contract.append(entry)
            # add pertinent data to output
            results.append(entry)


def save_results():
    # export data
    try:
        with open('consolidated_contracts_ner_tags.csv', 'w') as csvfile:
            fieldnames = ['id', 'date', 'organization', 'value', 'location', 'press_release']
            contract_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            contract_writer.writeheader()
            unique_id = 0
            for result in results:
                contract_writer.writerow({'dates_in_announcement': result['dates_in_announcement'],
                                          'organization': result['organization'], 'value': result['value'],
                                          'location': result['location'], 'press_release': result['press_release'],
                                          'id': unique_id, 'date_of_announcement': result['date_of_announcement']})
                unique_id += unique_id
    except IOError:
        print("Error exporting data.")
    else:
        print("Data exported.")

ner_tag_text()
save_results()
