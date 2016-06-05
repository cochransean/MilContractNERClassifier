import csv
from pycorenlp import StanfordCoreNLP
import time
import re

# TODO fix Sep 11, 2006 to Nov 15, 2006 and November 29, 2006 to Dec 4, 2006 data (not separated)
# TODO try this regex to find seperators between the large blocks of text \([a-zA-z0-9-]{6,}[0-9]{3,}\)
# TODO find items with more than one match maybe with
# TODO (\([a-zA-z0-9-]{8,}[0-9]{3,}\)).{300,}(\([a-zA-z0-9-]{8,}[0-9]{3,}\))
# setup variables and server
contracts = []
nlp = StanfordCoreNLP('http://localhost:9000')


def ner_tag_text():

    # load data
    try:
        with open('consolidated_contracts.csv', 'r') as csvfile:
            contract_reader = csv.DictReader(csvfile)
            for row in contract_reader:
                contracts.append({'date': row['date'], 'announcement': row['announcement']})
    except IOError:
        print("Error loading data.")
    else:
        print("Data loaded.")

    classifiers_to_output = {
        'ORGANIZATION': 'organization',
        'MONEY': 'value',
        'LOCATION': 'location',
        'DATE': 'date'
    }

    # loop through each press release
    for contract in contracts:
        # get rid of troublesome unicode characters
        contract['announcement'] = re.sub("[\x92\x93\x94]", "", contract['announcement'])
        contract['announcement'] = contract['announcement'].replace("’", "'")
        contract['announcement'] = contract['announcement'].replace("“", '"')
        contract['announcement'] = contract['announcement'].replace("”", '"')
        contract['announcement'] = contract['announcement'].replace("–", '-')
        contract['announcement'] = contract['announcement'].replace("—", '-')
        contract['announcement'] = contract['announcement'].replace("‑", '-')

        tagged_contract = []
        annotated_text = None
        # get text of release
        successful = False
        number_of_tries = 0
        while not successful and number_of_tries < 10:
            text = contract['announcement']
            print(text)
            annotated_text = nlp.annotate(text, properties={
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

        # loop through sentences
        for sentence in annotated_text['sentences']:
            # create dict to store output
            entry = {}
            # track current list index for each output type
            output_index = {}
            for output in classifiers_to_output.values():
                entry[output] = []
                output_index[output] = 0
            # loop through words and punctuation
            for current_token, next_token in zip(sentence['tokens'], sentence['tokens'][1:]):
                for classifier, output in classifiers_to_output.items():
                    # make sure current word and next match classifier (to separate identical matches in same sentence)
                    if current_token['ner'] == classifier:
                        # add space to list if it isn't there
                        if len(entry[output]) < output_index[output] + 1:
                            entry[output].append('')
                        # include any spaces between words
                        entry[output][output_index[output]] += current_token['originalText'] + current_token['after']
                        if next_token['ner'] != classifier:
                            output_index[output] += 1
            tagged_contract.append(entry)
        # add pertinent data to contracts list
        contract['organization'] = tagged_contract[0]['organization']
        contract['value'] = tagged_contract[0]['value']
        contract['location'] = tagged_contract[0]['location']
        contract['contracting_activity'] = tagged_contract[-1]['organization']
        contract['contracting_activity_location'] = tagged_contract[-1]['location']
        print(contract)


def save_results():
    # export data
    try:
        with open('consolidated_contracts_ner_tags.csv', 'w') as csvfile:
            fieldnames = ['id', 'date', 'organization', 'value', 'location', 'contracting_activity',
                          'announcement', 'contracting_activity_location']
            contract_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            contract_writer.writeheader()
            for contract in contracts:
                unique_id = 0
                contract_writer.writerow({'date': contract['date'], 'organization': contract['organization'],
                                          'value': contract['value'], 'location': contract['location'],
                                          'contracting_activity': contract['contracting_activity'],
                                          'contracting_activity_location': contract['contracting_activity_location'],
                                          'announcement': contract['announcement'], 'id': unique_id})
                unique_id += unique_id
    except IOError:
        print("Error exporting data.")
    else:
        print("Data exported.")

ner_tag_text()
save_results()
