
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import requests

BROWSER = None
WORDS = []
cached_definitions = {}

DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

failed_words = []

def get_words(num_words):
    """ Get Random words by scalping randomlists.com """
    num_category = {
        "num_adj": [0, "https://www.randomlists.com/random-adjectives?dup=false&qty="],
        "num_verb": [0, "https://www.randomlists.com/random-verbs?dup=false&qty="],
        "num_adverb": [0, "https://www.randomlists.com/random-adverbs?dup=false&qty="],
        "num_noun": [0, "https://www.randomlists.com/random-nouns?dup=false&qty="],
        "num_animal": [0, "https://www.randomlists.com/random-animals?dup=false&qty="], 
        "num_food": [0, "https://www.randomlists.com/random-food?dup=false&qty="],
        "num_job": [0, "https://www.randomlists.com/random-jobs?dup=false&qty="],
        "num_fruit": [0, "https://www.randomlists.com/random-fruits?dup=false&qty="], 
        "num_body_part": [0, "https://www.randomlists.com/random-body-parts?dup=false&qty="],
        "num_sport": [0, "https://www.randomlists.com/random-sports?dup=false&qty="],
        "num_compound": [0, "https://www.randomlists.com/compound-words?dup=false&qty="],
        "num_instrument": [0, "https://www.randomlists.com/random-instruments?dup=false&qty="],
        "num_preposition": [0, "https://www.randomlists.com/random-prepositions?dup=false&qty="],
        "num_clothes": [0, "https://www.randomlists.com/random-clothing?dup=false&qty="],
        "num_country": [0, "https://www.randomlists.com/random-country?dup=false&qty="],
        "num_dinner": [0, "https://www.randomlists.com/random-dinner?dup=false&qty="]
    }

    for i in range(num_words):
        index = np.random.randint(0, len(num_category))
        num_category[list(num_category.keys())[index]][0] += 1

    for key in num_category:
        if num_category[key][0] > 0:
            fetch_words(num_category[key][1]+str(num_category[key][0]))

    print(num_category)

    return WORDS

def fetch_words(url):
    """Init BROWSER if not already active"""
    global BROWSER

    if BROWSER is None:
        driver_path = "chromedriver.exe"
        brave_path = "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"

        option = webdriver.ChromeOptions()
        option.binary_location = brave_path
        option.add_argument("--headless")
        option.add_argument("--disable-web-security")
        option.add_argument("--disable-browser-side-navigation")

        BROWSER = webdriver.Chrome(executable_path=driver_path, options=option)

    BROWSER.get(url)
    soup = (BeautifulSoup(BROWSER.page_source, "html.parser")).find("body")

    random_words = (soup.find("div", {"class": "Rand-stage"})).find_all("span", {"class":"rand_large"})
    for word in random_words:
        # check for non-alphanumeric characters
        if word.text.isalnum() and 2 < len(word.text) < 16:
            WORDS.append(word.text.upper())

    print(WORDS)

def fetch_definitions(v_words, h_words):
    """ Take in words and find their definitions"""
    v_def = []
    h_def = []

    v_def = process_response(v_words)
    h_def = process_response(h_words)

    return v_def, h_def

def process_response(words):
    """ process the words and get their definitions """
    word_def = []

    for word in words:
        need_to_scalp = False
        chosen_def = None

        if word in cached_definitions:
            word_def.append([word, cached_definitions[word][np.random.randint(0, len(cached_definitions[word]))]])
            continue

        response = requests.get(DICTIONARY_URL + word)
        word_info = response.json()

        # fails if 404 or w/e error pops up
        try:
            word_info[0]["meanings"][0]["definitions"]
            need_to_scalp = False
        except KeyError:
            need_to_scalp = True

        if(not need_to_scalp):
            chosen_def = process_results(word_info, word)

        if(chosen_def is None):
            try:
                chosen_def = scalp_from_merriam(word)
            except Exception:
                failed_words.append(word)
                chosen_def = "failed"

        word_def.append([word, chosen_def])
    return word_def

def process_results(word_info, word):
    """ parse data related to a word, output a definition """
    possible_definitions = []
    for definition_details in word_info[0]["meanings"][0]["definitions"]:
        definition = definition_details["definition"]
        if len(definition) < 200:
            definition = definition[0].upper() + definition[1:]
            possible_definitions.append(definition)
    
    cached_definitions[word] = possible_definitions

    if len(possible_definitions) == 0:
        return None

    chosen_def = possible_definitions[np.random.randint(0, len(possible_definitions))]
    return chosen_def

def scalp_from_merriam(word):
    """ well, scalp definitions from meriam webster. Allowed by their robots.txt"""
    global BROWSER

    url = f"https://www.merriam-webster.com/dictionary/{word}"

    if BROWSER is None:
        driver_path = "C:/Users/Zachary/Desktop/Java Projects/automated crossword puzzle generator/chromedriver.exe"
        brave_path = "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"

        option = webdriver.ChromeOptions()
        option.binary_location = brave_path
        option.add_argument("--headless")
        option.add_argument("--disable-web-security")

        BROWSER = webdriver.Chrome(executable_path=driver_path, options=option)
    
    BROWSER.get(url)
    soup = (BeautifulSoup(BROWSER.page_source, "html.parser")).find("body")

    definitions = (soup.find("div", {"id": "left-content"})).find_all("span", {"class":"dtText"})
    definitions_raw = []
    for definition in definitions:
        if len(definition) < 200:
            text = definition.text
            text = text[2].upper() + text[3:]
            definitions_raw.append(text)

    cached_definitions[word] = definitions_raw

    return definitions_raw[np.random.randint(0, len(definitions_raw))]

# guarrenteed to break
def remove_words(words):
    """ Remove words that have been proven to break this entire thing. 
        A cleaner solution to adding another dictionary to check and so on and so on.
    """
    to_remove = [
        "CENTERCUT",
        "BUGSPRAY",
        "NEEDILY",
        "KOOKILY",
        "SHADYSIDE",
        "UPLIFTINGLY",
        "JUDGEMENTALLY",
        "SNOWSHOVEL",
        "JOSHINGLY",
        "WIFFLEBALL",
        "UNDERDEVELOP",
        "COAXINGLY",
        "GYNASTICS",
        "SHIPBOTTOM",
        "CARDSTOCK",
        "ATCHCASE"
    ]

    words = [word for word in words if word not in to_remove]
    return words

if __name__ == "__main__":
    process_response(["something"])
