import random

class grid:
    def __init__(self, size):
        self.size = size
        self.total_squares = size * size
        self.horizontal_first = True
        self.grid = [[" " for x in range(size)] for y in range(size)] # 2d array, size x size
        self.used_words = [] # list of words already used
        self.is_empty = True
        self.word_start_locations = {} #  word: [direction, x, y]
        self.intersection_locations = [] # [[x, y], ...] used to check if a letter can be placed
        self.forbidden_squares = [] # array of squares that are letters ABSOLUTLY cannot go
        self.free_letter_locations = {
            "A":[],
            "B":[],
            "C":[],
            "D":[],
            "E":[],
            "F":[],
            "G":[],
            "H":[],
            "I":[],
            "J":[],
            "K":[],
            "L":[],
            "M":[],
            "N":[],
            "O":[],
            "P":[],
            "Q":[],
            "R":[],
            "S":[],
            "T":[],
            "U":[],
            "V":[],
            "W":[],
            "X":[],
            "Y":[],
            "Z":[]
        }

    def print_debug(self):
        print(self.free_letter_locations)
        print(f"Word List: {self.used_words}")
        print(f"Word Starting Locations: {self.word_start_locations}")
        self.print_grid()

    def print_grid(self):
        for i in range(self.size):
            for j in range(self.size):
                print("╋───", end="")
            print("╋", end="\n")
            for j in range(self.size):
                print("┃ " + str(self.grid[i][j]), end=" ")
            print("┃", end="\n")

        for j in range(self.size):
            print("╋───", end="")
        print("╋", end="\n")
    
    def add_word(self, word):
        can_fit = False
        intersections = {} # index of the common letter(s) which allows for the intersection
         
        if(len(word) > self.size):
            return False
        if(word in self.used_words):
            return False

        # check if any of the letters are already in the grid
        if (self.is_empty):
            # if there are no words in the grid, just add the word
            self.add_first_word(word)
            self.is_empty = False
            return True

        # check if its possible to add the word

        for letter_index in range(len(word)):
            letter = word[letter_index]
            if(self.free_letter_locations[letter] != []):
                can_fit = True
                arr = []

                for i in self.free_letter_locations[letter]:
                    arr.append(i)

                if (letter_index not in intersections):
                    intersections[letter_index] = arr
                else:
                    joined_list = intersections[letter_index] + arr
                    intersections[letter_index] = joined_list

        if(can_fit == False):
            return False

        # try adding horizontally
        h_placement_info = None
        v_placement_info = None
        placement_info = None

        if(self.horizontal_first):
            self.horizontal_first = False
            h_placement_info = self.add_horizontal(word, intersections)

            if(h_placement_info == False):
                v_placement_info = self.add_vertical(word, intersections)
            else:
                placement_info = h_placement_info

            if(v_placement_info != False and v_placement_info != None):
                placement_info = v_placement_info
        else:
            self.horizontal_first = True
            v_placement_info = self.add_vertical(word, intersections)
            
            if(v_placement_info == False):
                h_placement_info = self.add_horizontal(word, intersections)
            else:
                placement_info = v_placement_info
            
            if(h_placement_info != False and h_placement_info != None):
                placement_info = h_placement_info


    
        # remove squares around the intersection point from the free_letter_locations
        if(placement_info != None):
            self.remove_free_letters(placement_info)

            #{'SAFER': [0, 0], 'SEASIDE': [0, 0], 'AMUSE': [0, 1], 'FLU': [0, 2], 'DIP': [5, 0], 'ROE': [0, 4], 'OLD': [1, 4], 'SIP': [5, 2]}

        return False

    def remove_free_letters(self, placement_info):
        # remove letters if they are around the intersection point
        intersection_square = placement_info[list(placement_info.keys())[0]]
        squares_to_check = self.list_squares_to_remove(intersection_square)

        new_letter_positions = []

        for letter in self.free_letter_locations:
            for potential_intersection in self.free_letter_locations[letter]:
                if(potential_intersection not in squares_to_check):
                    new_letter_positions.append(potential_intersection)
            
            self.free_letter_locations[letter] = new_letter_positions
            new_letter_positions = []
        
    def list_squares_to_remove(self, intersection_square):
        arr = []
        for x in range(intersection_square[0] - 1, intersection_square[0] + 2):
            for y in range(intersection_square[1] - 1, intersection_square[1] + 2):
                if(0 <= x < self.size and 0 <= y < self.size):
                    arr.append([x, y])

        arr.append(intersection_square)
        
        return arr

    def add_first_word(self, word):
        # add the first word to the grid
        result = random.randint(0, 2)
        if (result == 0):
            for i in range(len(word)):
                self.grid[0][i] = word[i]
                self.free_letter_locations[word[i]].append([0, i])
            self.used_words.append(word)
            self.word_start_locations[word] = ["h", 0, 0]
        elif (result == 1):
            for i in range(len(word)):
                self.grid[0][self.size - len(word) + i] = word[i]
                self.free_letter_locations[word[i]].append([0, self.size - len(word) + i])
            self.used_words.append(word)
            self.word_start_locations[word] = ["h", 0, self.size - len(word)]
        elif (result == 2):
            for i in range(len(word)):
                self.grid[self.size - 1][i] = word[i]
                self.free_letter_locations[word[i]].append([self.size - 1, 0])
            self.used_words.append(word)
            self.word_start_locations[word] = ["h", self.size - 1, 0]

    def add_horizontal(self, word, intersections):
        word_placement_info = self.horizontal_checks(word, intersections)
        
        # returns a key-value pair or False
        #{word_index: [point_of_intersection]}

        if (word_placement_info):
            word_index = list(word_placement_info.keys())[0]
            intersection_point = word_placement_info[list(word_placement_info.keys())[0]]

            self.intersection_locations.append(intersection_point)

            for letter in range(len(word)):
                self.grid[intersection_point[0]][intersection_point[1] + letter - word_index] = word[letter]
                self.free_letter_locations[word[letter]].append([intersection_point[0], intersection_point[1] + letter - word_index])
            self.used_words.append(word)
            return word_placement_info

        return False        

    def add_vertical(self, word, intersections):
        word_placement_info = self.vertical_checks(word, intersections)

        # returns a key-value pair or False
        #{word_index: [point_of_intersection]}

        if (word_placement_info):
            word_index = list(word_placement_info.keys())[0]
            intersection_point = word_placement_info[list(word_placement_info.keys())[0]]

            self.intersection_locations.append(intersection_point)
            
            for letter in range(len(word)):
                self.grid[intersection_point[0] + letter - word_index][intersection_point[1]] = word[letter]
                self.free_letter_locations[word[letter]].append([intersection_point[0] + letter - word_index, intersection_point[1]])
            self.used_words.append(word)
            return word_placement_info

        return False   

    def horizontal_checks(self, word, intersections):
        # check if the word can fit in at least one spot
        # intersection = #{word_index: [[intersection point]]}
        # {0: [[0, 2], [0, 3]], 1: [[0, 4]], 3: [[0, 1]]}

        for word_index in intersections:
            intersecting_points = intersections[word_index]

            can_fit = True

            for point in intersecting_points:
                if (point[1] - word_index < 0):
                    continue

                if (point[1] + len(word) - word_index >= self.size):
                    continue

                if (point[1] - word_index - 1 >= 0):
                    if (self.grid[point[0]][point[1] - 1] != " "):
                        continue

                # check along the length of the word
                for i in range(len(word)):
                    if ([point[0], point[1] + i - word_index] in self.forbidden_squares):
                        return False

                # check ends of the word
                if(point[1] - word_index - 1 >= 0):
                    if ([point[0], point[1] - word_index - 1] in self.forbidden_squares):
                        continue

                    self.forbidden_squares.append([point[0], point[1] - word_index - 1])

                    if self.grid[point[0]][point[1] - word_index - 1] != " ":
                        continue
                if(point[1] + len(word) - word_index < self.size):
                    if ([point[0], point[1] + len(word) - word_index] in self.forbidden_squares):
                        continue

                    self.forbidden_squares.append([point[0], point[1] + len(word) - word_index])

                    if self.grid[point[0]][point[1] + len(word) - word_index] != " ":
                        continue


                for i in range(len(word)):
                    if(self.grid[point[0]][point[1] + i - word_index] == word[i] and i != 1):
                        continue

                    if(self.grid[point[0]][point[1] + i - word_index] != " " or 
                    ([point[0], point[1] + i - word_index] in self.forbidden_squares)):
                        can_fit = False
                        break

                    if (point[0] - 1 >= 0):
                        if ([point[0], point[1] + i - word_index] not in self.intersection_locations and 
                            self.grid[point[0] - 1][point[1] + i - word_index] != " "):
                            can_fit = False
                            break

                    if (point[0] + 1 < self.size):
                        if ([point[0], point[1] + i - word_index] not in self.intersection_locations and
                            self.grid[point[0] + 1][point[1] + i - word_index] != " "):
                            can_fit = False
                            break

                if(can_fit == False):
                    continue

                # if we get here, we can fit the word
                # return key-value pair

                self.word_start_locations[word] = ["h", point[0], point[1] - word_index]

                return {word_index: point}

        return False

    def vertical_checks(self, word, intersections):
        for word_index in intersections:
            intersecting_points = intersections[word_index]
            can_fit = True

            for point in intersecting_points:
                if (point[0] - word_index < 0):
                    continue

                if (point[0] + len(word) - word_index >= self.size):
                    continue

                if (point[0] - word_index - 1 >= 0):
                    if (self.grid[point[0] - 1][point[1]] != " "):
                        continue

                for i in range(len(word)):
                    if ([point[0]  + i - word_index, point[1]] in self.forbidden_squares):
                        return False

                # check ends of the word
                if(point[0] - word_index - 1 >= 0):
                    if ([point[0] - word_index - 1, point[1]] in self.forbidden_squares):
                        continue

                    self.forbidden_squares.append([point[0] - word_index - 1, point[1]])

                    if self.grid[point[0] - word_index - 1][point[1]] != " ":
                        continue
                if(point[0] + len(word) - word_index + 1 < self.size):
                    if([point[0] + len(word) - word_index + 1, point[1]] in self.forbidden_squares):
                        continue

                    self.forbidden_squares.append([point[0] + len(word) - word_index + 1, point[1]])

                    if self.grid[point[0] + len(word) - word_index + 1][point[1]] != " ":
                        continue

                for i in range(len(word)):
                    if(self.grid[point[0] + i - word_index][point[1]] == word[i] and i != 1):
                        continue

                    if(self.grid[point[0] + i - word_index][point[1]] != " "):
                        can_fit = False
                        break

                    if (point[1] - 1 >= 0):
                        if ([point[0] + i - word_index, point[1]] not in self.intersection_locations and
                            self.grid[point[0] + i - word_index][point[1] - 1] != " "):
                            can_fit = False
                            break

                    if (point[1] + 1 < self.size):
                        if ([point[0] + i - word_index, point[1]] not in self.intersection_locations and
                            self.grid[point[0] + i - word_index][point[1] + 1] != " "):
                            can_fit = False
                            break

                    
                
                if(can_fit == False):
                    continue

                # if we get here, we can fit the word
                # return key-value pair
                self.word_start_locations[word] = ["v", point[0] - word_index, point[1]]

                return {word_index: point}

        return False

