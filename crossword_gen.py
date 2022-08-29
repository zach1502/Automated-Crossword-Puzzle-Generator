from math import floor
import random
from copy import deepcopy
from os import listdir
from PIL import Image, ImageDraw, ImageFont
from matplotlib.transforms import Bbox
import matplotlib.pyplot as plt
import matplotlib
from utils.collect_words import get_words, fetch_definitions, remove_words, failed_words
from utils.grid import grid

# ISSUES:
# 1. Improve readibility of code
# 2. Some words aren't in the API or Merriam webster
MULTIPLIER = 1

TEXT_SIZE = 24
TEXT_UPPERMARGIN = 5
LEFT_ANS_INDENT = 212
LEFT_INDENT = 76
PAGE_SIZE = (1240, 1754)
PAGE_NUMBER_LOCATION = (PAGE_SIZE[0] >> 1, floor(PAGE_SIZE[1] * 0.95))
CROSSWORD_IMG_HEIGHT = 968
BLACK = (0, 0, 0)
LINE_CHAR_LIMIT = 100
HEADER_SIZE = TEXT_SIZE << 1
TEXT_FONT = ImageFont.truetype('times.ttf', size=TEXT_SIZE)
HEADER_FONT = ImageFont.truetype('times.ttf', size=HEADER_SIZE)
matplotlib.use('Agg') # don't use tkAgg (better memory usage)

TARGET_DENSITY_LOW = 0.25
TARGET_DENSITY_HIGH = 0.95

PDF_PATH = "crossword.pdf"
ANS_PATH = "answers/"
QUESTION_PATH = "questions/"

# takes ~15s to make 1 page
# should make this multithreaded, each thread with its own browser
PAGES_DESIRED = 3

page_number = 1
puzzle_list = []

def main():
    """This is the main function, encapsulates everything"""

    global words
    global failed_words
    words = get_words(100000)
    # these words aren't in the Dictionary API and Merriam-Webster
    # i.e. will cause an exception. much better than having to manually build a list
    words = remove_words(words)
    print(f"There are {len(words)} words being used")

    for i in range(PAGES_DESIRED):
        play_area = create_crossword(words)

        print(f"Puzzle {i+1}:")
        play_area.print_debug()

        create_crossword_ans(play_area)

        # create a grid image to overlay the number hints
        create_play_grid(play_area)

        # split into vertical and horizontal words
        v_words, h_words = split_words(play_area.word_start_locations)

        # get word definitions
        v_def, h_def = fetch_definitions(v_words, h_words)

        # Display hints + crossword
        # combine_images
        enumerated_squares = assign_numbers(play_area.word_start_locations)
        build_page(v_def, h_def, play_area.word_start_locations, enumerated_squares)
        print(failed_words)

    build_answers()

    build_book()

    print(failed_words)

def build_book():
    """ Takes all the images in puzzle_list and combines it into a PDF """
    global puzzle_list
    
    puzzle_list[0].save(PDF_PATH, "PDF", resolution=150.0, save_all=True, append_images=puzzle_list[1:])

def build_answers():
    """ Reads in all images in the answers folder and builds pages full of the answers in order """
    ans_list = [
        Image.open(ANS_PATH + f)
        for f in listdir(ANS_PATH)
    ]

    build_answer_pages(ans_list)

def build_answer_pages(ans_list):
    """ Takes in a list of images and compiles them into an answer page. Finished page gets appended to puzzle_list"""
    global page_number
    
    position1 = (LEFT_ANS_INDENT, 50)
    position2 = (LEFT_ANS_INDENT, 850)
    first = True
    page = None
    # draw.text(PAGE_NUMBER_LOCATION, str(page_number), BLACK, font=TEXT_FONT)
    for i in range(len(ans_list)):
        solution = ans_list[i]

        if(first):
            page = Image.new('RGB', PAGE_SIZE, color='white')
            draw = ImageDraw.Draw(page)
            draw.text((LEFT_INDENT, 300), f"Puzzle {i + 1}", BLACK, font=TEXT_FONT)
            page.paste(solution, position1)
            first = False
        else:
            page.paste(solution, position2)
            first = True
            draw.text(PAGE_NUMBER_LOCATION, str(page_number), BLACK, font=TEXT_FONT)
            draw.text((LEFT_INDENT, 1150), f"Puzzle {i + 1}", BLACK, font=TEXT_FONT)
            page_number += 1
            page = page.resize((PAGE_SIZE[0] * 2, PAGE_SIZE[1] * 2), Image.NEAREST)
            puzzle_list.append(page)

    if not first:
        draw.text(PAGE_NUMBER_LOCATION, str(page_number), BLACK, font=TEXT_FONT)
        page = page.resize((PAGE_SIZE[0] * 2, PAGE_SIZE[1] * 2), Image.NEAREST)
        puzzle_list.append(page)


def split_words(words_details):
    """ cache which words are in which direction for the sake of easier access """
    v_words = []
    h_words = []

    for key, value in words_details.items():
        if(value[0] == "v"):
            v_words.append(key)
        else:
            h_words.append(key)

    return v_words, h_words

def assign_numbers(word_start_locations):
    """ Adds numbers to the top left corner of each starting spot for a square"""
    squares = []
    word_start_locations_list = list(word_start_locations.items())
    num_common_squares = 0

    for locations_index in range(len(word_start_locations_list)):
        flag = False

        cords = word_start_locations_list[locations_index][1]

        for i in range(len(squares)):
            if(cords[1] == squares[i][0] and cords[2] == squares[i][1]):
                flag = True
                num_common_squares += 1
                break
            
        if(flag):
            continue

        squares.append([cords[1], cords[2], locations_index - num_common_squares + 1])

    return squares

### V_def and h_def could contain the index
def build_page(v_def, h_def, word_start_locations, enumerated_squares):
    """ Assembles the crossword puzzle page, with definitions and hints in order """
    global page_number
    global puzzle_list

    bg_image = Image.new('RGB', PAGE_SIZE, color='white')
    crossword_img = Image.open('crossword_question.png')

    # overlay crossword image
    bg_image.paste(crossword_img, (LEFT_INDENT, 0))
    draw = ImageDraw.Draw(bg_image)
    draw.fontmode = "L"

    row = 0
    row = write_text(h_def, row, word_start_locations, enumerated_squares, draw, is_horizontal=True)
    row = write_text(v_def, row, word_start_locations, enumerated_squares, draw, is_horizontal=False)

    draw.text(PAGE_NUMBER_LOCATION, str(page_number), BLACK, font=TEXT_FONT)
    page_number += 1
    bg_image = bg_image.resize((PAGE_SIZE[0] * 2, PAGE_SIZE[1] * 2), Image.NEAREST)
    puzzle_list.append(bg_image)
    bg_image.save("page.png", resolution=150.0)

def draw_underlined_text(draw, x, y, text: str, font, color):
    """ Draw underlined text at a specific (x, y)"""
    draw.text((x, y), text, fill=color, font=font)
    draw.line((x, y + font.size , x + HEADER_SIZE * len(text) * 0.4, y + font.size), fill=color)

def split_line(line):
    # split the line into x lines, each about 100 char long, ending where there's a space
    start_point = 0
    end_point = LINE_CHAR_LIMIT
    lines = []

    while line.__len__() > end_point:
        if line[end_point] == " ":
            lines.append(line[start_point:end_point].strip())
            start_point = end_point
            end_point += LINE_CHAR_LIMIT
        else:
            end_point += 1

    lines.append(line[start_point:].strip())

    return lines

def write_text(definition_list, row, word_start_locations, enumerated_squares, draw, is_horizontal=True):
    """ On the page, write down the numbered hints. This goes below the puzzle itself """
    row += 1
    title_text = "Horizontal Words: " if is_horizontal else "Vertical Words: "
    draw_underlined_text(draw, LEFT_INDENT + 15, CROSSWORD_IMG_HEIGHT + row * (TEXT_UPPERMARGIN + TEXT_SIZE), title_text, HEADER_FONT, BLACK)
    row += 2
    # right col
    for word_def_pair in definition_list:
        # find the word start location
        word = word_def_pair[0]
        definition = word_def_pair[1]

        # find the word's index in word_start_locations
        word_info =  word_start_locations[word]
        word_index = 0

        starting_square = [word_info[1], word_info[2]]

        for i in range(len(enumerated_squares)):
            if(enumerated_squares[i][0] == starting_square[0] and enumerated_squares[i][1] == starting_square[1]):
                word_index = enumerated_squares[i][2]
                break

        lines = split_line(definition)
        draw.text((LEFT_INDENT + 15, CROSSWORD_IMG_HEIGHT + row * (TEXT_UPPERMARGIN + TEXT_SIZE)), f"{word_index}. ", fill=BLACK, font=TEXT_FONT)
        while lines.__len__() > 0:
            line = lines.pop(0)
            draw.text((LEFT_INDENT + 60, CROSSWORD_IMG_HEIGHT + row * (TEXT_UPPERMARGIN + TEXT_SIZE)), line, BLACK, font=TEXT_FONT)
            row += 1

    return row

def create_crossword(words):
    """ Automatically create a crossword puzzle """
    while(True):
        og_wordlist = deepcopy(words)
        play_area = grid(15)

        for i in range(3):
            for j in range(len(words)):
                word = words[random.randint(0, len(words)-1)]
                if(play_area.add_word(word)):
                    #print("Added word: " + word)
                    words.remove(word)
        letter_count = 0
        for x in range(play_area.size):
            for y in range(play_area.size):
                if(play_area.grid[x][y] != " "):
                    letter_count += 1
        letter_density = letter_count / float(play_area.total_squares)
        if(TARGET_DENSITY_LOW  <= letter_density <= TARGET_DENSITY_HIGH): # target density
            # print(f"Success! Crossword has a density of {letter_density}")
            break
        else:
            # print(f"Failed! Crossword has a density of {letter_density}")
            words = og_wordlist

    return play_area

def create_play_grid(play_area):
    """ Draws out the crossword puzzle grid """
    # add number hints
    # [[1x, y], [2x, y], [3x, y], [4x, y]]

    number_hints = []
    for key, value in play_area.word_start_locations.items():
        if [value[1], value[2]] not in number_hints:
            number_hints.append([value[1], value[2]])

    fig, ax = plt.subplots()

    ax.axis('tight')
    ax.axis('off')
    ax.set_aspect('equal')

    # center the text
    ax.text(0.5, 0.5, play_area.grid, ha='center', va='center')
    fig.patch.set_visible(False)

    hint_grid = [[" " for x in range(play_area.size)] for y in range(play_area.size)]

    for x in range(play_area.size):
        for y in range(play_area.size):
            if([x, y] in number_hints):
                hint_grid[x][y] = str(number_hints.index([x, y]) + 1)

    cell_bg_colour = [["w" for x in range(play_area.size)] for y in range(play_area.size)]

    for x in range(play_area.size):
        for y in range(play_area.size):
            if(play_area.grid[x][y] == " "):
                cell_bg_colour[x][y] = "black"
    
    table = ax.table(cellColours=cell_bg_colour,
            cellText=hint_grid,
            loc="center",
            cellLoc='left',
            rowLabels=None,
            colLabels=None,
            colWidths=[0.75/play_area.size for x in range(play_area.size)]
            )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(3, 3)

    plt.savefig("crossword_question.png", dpi=128, pad_inches=0.0, bbox_inches= Bbox([[-1, -1.5], [7.5, 6.25]]))
    plt.savefig(f"questions/crossword_question_{page_number}.png", dpi=128, pad_inches=0.0, bbox_inches= Bbox([[-1, -1.5], [7.5, 6.25]]))
    plt.close()

def create_crossword_ans(play_area):
    """ Create the crossword puzzle answers, results get saved into the answers folder """
    #create new plot
    #plt.margins(0,0)
    fig, ax = plt.subplots()

    # center the text
    fig.patch.set_visible(False)
    ax.text(0.5, 0.5, play_area.grid, ha='center', va='center')
    ax.axis('tight')
    ax.axis('off')
    ax.set_aspect('equal')

    cell_bg_colour = [["w" for x in range(play_area.size)] for y in range(play_area.size)]

    for x in range(play_area.size):
        for y in range(play_area.size):
            if(play_area.grid[x][y] == " "):
                cell_bg_colour[x][y] = "black"

    ax.table(cellColours=cell_bg_colour,
                cellText=play_area.grid,
                loc="center",
                cellLoc='center',
                rowLabels=None,
                colLabels=None,
                colWidths=[0.75/play_area.size for x in range(play_area.size)]
                ).scale(3, 3)

    plt.savefig(f"answers/crossword_answers_{page_number}.png", dpi=96, pad_inches=0.0, bbox_inches= Bbox([[-1, -1.5], [7.5, 6.25]]))
    plt.close()

if __name__ == "__main__":
    # create a crossword
    main()
