from sys import argv, exit
import json
import re
from pprint import pprint


class Token():

    def __init__(self, type_t, value, line, col):

        self.type_t = type_t
        self.value = value
        self.line = line
        self.col = col


class LexicalAnalyzer():

    def __init__(self, table_path, source_code):

        self.col_cont = 0
        self.position = 0
        self.tokens = []
        self.line = 1

        # Loading symbol table.
        with open(table_path, 'r') as f:
            self.symbol_table = json.load(f)

        # Loading the source code.
        with open(source_code, 'r') as fd:
            self.source_code = fd.read()

        # Number of characters.
        self.size_code = len(self.source_code)

    def error_message(self, line, col):

        print("Error: lexical error on line: ", self.line, "column: ", col)
        exit(0)

    def update_position(self, increment=1):
        self.position += increment
        self.col_cont += increment

    def build_token(self, rule):

        c = self.source_code[self.position]
        char_list = []
        # Adding the first element of the string.
        while re.search(rule, c):
            char_list.append(c)
            self.update_position()
            c = self.source_code[self.position]

        # Setting tokens attributes.
        # If this token is not in the symbol table.
        tkn = ''.join(char_list)
        if tkn not in self.symbol_table:
            self.symbol_table[tkn] = "ID"

        t = Token(self.symbol_table[tkn], tkn, self.line, self.col_cont)
        return t

    def small_symbols(self):

        c = self.source_code[self.position]
        if re.search("[\[\[(){},;+*-/]", c):
            self.update_position()
            return Token(self.symbol_table[c], c, self.line, self.col_cont)

        # If it is some of this symbols (<,>,<=,>=,=,==).
        elif re.search("[!<>=]", c):
            if self.position + 1 < self.size_code:
                char_list = []
                char_list.append(c)
                self.update_position()
                c = self.source_code[self.position]
                # If it is some of this "<=, >=, =="
                if c == "=":
                    char_list.append(c)
                    self.update_position()
                    tkn = ''.join(char_list)
                    return Token(self.symbol_table[tkn], tkn, self.line, self.col_cont)
                
                # If it is a = (atribution) verify if the other symbol is a variavel or a value.
                elif re.search("[0-9]|_|[a-zA-Z]|\s", c):
                    return None
                else:
                    print(c)
                    self.error_message(self.line, self.col_cont)
            else:
                self.update_position()
                return Token(self.symbol_table[c], c, self.line, self.col_cont)
        
        # If it is some of these &, |
        elif re.search("[&|]", c):
            # If is is valid.
            if self.position + 1 < self.size_code:
                self.update_position()
                c2 = self.source_code[self.position]
                # If it is && or ||
                if c == c2:
                    tkn = c + c2
                    self.update_position()
                    return Token(self.symbol_table[tkn], tkn, self.line, self.col_cont)
                else:
                    self.error_message(self.line, self.col_cont)
            else:
                self.error_message(self.line, self.col_cont)

        elif c == "\n":
            self.line += 1
            self.col_cont = 0
            self.update_position()
        
        return None
        """
        elif c == "\t" or c == "\r":
            self.update_position()
        """

    def lexical_analysis(self, white_skip=True):

        while self.position < self.size_code:

            c = self.source_code[self.position]
            # white space skipping.
            if c == ' ' and white_skip:
                self.update_position()

            # If it is a letter (it must be a ID or Key-Word).
            elif re.search("[a-zA-Z]", c):
                t = self.build_token("[a-zA-Z]|_|[0-9]")
                self.tokens.append(t)

            # If it is number.
            elif re.search("[0-9]", c):
                t = self.build_token("[0-9]|\.")
                self.tokens.append(t)

            # If is is a diferent reserved symbol (operator.)
            else:
                t = self.small_symbols()
                if t is not None:
                    self.tokens.append(t)

if __name__ == '__main__':

    l = LexicalAnalyzer(argv[1], argv[2])
    l.lexical_analysis()
    for t in l.tokens:
        print(t.value, t.type_t, t.line, t.col)
