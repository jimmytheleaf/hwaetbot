import re

import nltk
from bs4 import BeautifulSoup

import hwaetbot.config as config


def parse_corpus():

    prose, english_riddles, old_english_riddles = load_text_corpuses(config.data_path)

    sentences = tokenize_sentences(english_riddles)
    
    cleaned_sentences = clean_sentences(sentences)

    return cleaned_sentences


def load_text_corpuses(path):
        
    prose = []
    english_riddles = []
    old_english_riddles = []

    for html_doc in path.walk(filter=lambda p: p.isfile() and re.match(r".*html", p.name)):

        soup = BeautifulSoup(html_doc.read_file().decode('utf-8'))

        # Prose found in div.prose tags
        prose = prose + [tag.text for tag in soup.select('div.prose p')]

        for row in soup.select("table tr"):
            row_tds = row.findAll('td', {'align': 'left'})

            if len(row_tds) > 1:

                # English riddles found in leftmost cell in table rows.
                modern_english = row_tds[0].text.strip().encode('utf-8')

                english_riddles.append(modern_english)

                # Old English versions in righthand cell(s)
                old_english = [tag.text.strip().encode('utf-8') for tag in row_tds[1:]]
                old_english_riddles = old_english_riddles + old_english

    # Manual fix to a broken riddle
    english_riddles[-1] = english_riddles[-1].replace(' (etc. as l. 2 above)', '')

    return prose, english_riddles, old_english_riddles


def tokenize_sentences(riddles):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    riddle_sentences = []

    for riddle in riddles:
        sentences = sent_detector.tokenize(riddle.strip().decode('utf-8'))
        riddle_sentences = riddle_sentences + sentences

    return riddle_sentences

def clean_sentences(sentences):

    multiple_spaces = re.compile(ur'(\s)+', re.UNICODE)
    space_before_punct = re.compile(ur' (\W)', re.UNICODE)
    number_in_brackets = re.compile(ur'\[\d\]', re.UNICODE)

    # Encode back in utf-8, lost in tokenization
    sentences = map(lambda x : x.encode('utf-8'), sentences) 
    
    # Remove fragments
    sentences = filter(lambda x: len(x) >= 15, sentences) 

    # Remove whitespace
    sentences = map(lambda x: x.lower().replace('\n', ' ').replace('\xc2\xa0', ' '), sentences)
    sentences = map(lambda x: re.sub(multiple_spaces, ' ', x), sentences)
    sentences = map(lambda x: re.sub(space_before_punct, r'\1', x), sentences)
    sentences = map(lambda x: re.sub(number_in_brackets, '', x), sentences)
    sentences = map(lambda x: x.strip(), sentences)

    return sentences



if __name__ == "__main__":
    sentences = parse_corpus()
    for i, sentence in enumerate(sentences):
        print "%s :: %s" % (i, sentence)

