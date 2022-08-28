# Test the file in utils/grid.py
import unittest
from utils.collect_words import *
from utils.grid import *

# this only checks for exceptions
# word definitions need to be manually checked
class Encapsulate(unittest.TestCase):
    #class TestCollectingWords(unittest.TestCase):
    driver_path = "chromedriver.exe"
    brave_path = "C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe"

    def test_headless_browser(self):
        option = webdriver.ChromeOptions()
        option.binary_location = self.brave_path
        option.add_argument("--headless")
        option.add_argument("--disable-web-security")
        option.add_argument("--disable-browser-side-navigation")

        browser = webdriver.Chrome(executable_path=self.driver_path, options=option)
        browser.get("https://www.google.ca")

        # there's no assert for it so this works I guess
        print("BROWSER IS WORKING!!!")

    def test_connections(self):
        option = webdriver.ChromeOptions()
        option.binary_location = self.brave_path
        option.add_argument("--headless")
        option.add_argument("--disable-web-security")
        option.add_argument("--disable-browser-side-navigation")

        browser = webdriver.Chrome(executable_path=self.driver_path, options=option)
        # I checked each site's robot.txt
        browser.get("https://www.randomlists.com")
        print("randomlists.com is online")
        browser.get("https://api.dictionaryapi.dev/api/v2/entries/en/random")
        print("dictionaryapi.dev is online")
        browser.get("https://www.merriam-webster.com/dictionary/random")
        print("merriam-webster.com is online")

    def test_collection(self):
        words = get_words(10)
        words = remove_words(words)
        v_def, h_def = fetch_definitions(words, words)
        print(words)
        print(v_def)

    #class TestCollectingWords(unittest.TestCase):
    def test_grid_creation(self):
        grid_area = grid(15)
        self.assertTrue(grid_area.is_empty)
        self.assertEqual(grid_area.size, 15)

    def test_adding_words(self):
        grid_area = grid(15)
        grid_area.add_word("RANDOM")
        self.assertFalse(grid_area.is_empty)
        grid_area.add_word("RANDOMNESS")
        grid_area.add_word("DETERMINISTIC")
        grid_area.add_word("LIKELY")
        grid_area.add_word("PROBABILITY")
        grid_area.add_word("MAYBE")
        grid_area.add_word("GENERATOR")
        grid_area.add_word("DISTRIBUTION")
        grid_area.add_word("IMPOSSIBLE")
        grid_area.add_word("CERTAIN")

        # if it can add most of these in one pass, its good enough
        grid_area.print_debug()

if __name__ == '__main__':
    unittest.main()