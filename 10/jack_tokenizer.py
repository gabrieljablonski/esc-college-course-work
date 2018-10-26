from keywords import Keywords
from token_types import TTypes


EOF = -1
VALID_TOKEN = 0
SYMBOLS = [
    '{',
    '}',
    '(',
    ')',
    '[',
    ']',
    '.',
    ',',
    ';',
    '+',
    '-',
    '*',
    '/',
    '&',
    '|',
    '<',
    '>',
    '=',
    '~'
]
KEYWORDS = [k.value for k in Keywords]


class JackTokenizer:
    def __init__(self, input_file):
        self._input_file = input_file
        self._current_line = ''
        self.line_number = 0
        self._buffered_elements = []
        self._in_comment = False

        self.current_token = None
        self.token_type = None

    @property
    def has_more_tokens(self):
        pos = self._input_file.tell()
        line = self._input_file.readline()
        self._input_file.seek(pos)

        return True if line else False  # if line is empty, EOF

    def advance(self):
        while not self._buffered_elements:
            self._current_line = self._input_file.readline()
            self.line_number += 1
            if not self._current_line:
                return EOF

            if self._in_comment:
                if '*/' in self._current_line:
                    self._current_line = self._current_line.split('*/')[1]
                    self._in_comment = False
                else:
                    self._current_line = ''

            # Strip // comments
            self._current_line = self._current_line.split('//')[0]  \
                                                   .strip()

            # Strip /* and /** comments
            if '/*' in self._current_line:
                if '*/' in self._current_line:
                    self._current_line = ''
                else:
                    self._current_line = self._current_line.split('/*')[0] \
                                                           .strip()
                    self._in_comment = True

            if not self._current_line:  # If the line only had comments, go to next line
                continue

            self._buffered_elements = self._current_line.split()

        if self._buffered_elements:
            # element is defined as each substring separated by spaces in a line
            element = self._buffered_elements.pop(0)

            if element.startswith('"'):
                ttype = TTypes.STRING_CONST
                in_string = True
                token = ''
                element = element[1:]
                while in_string:
                    if '"' in element:
                        element, remaining = element.split('"')
                        self._buffered_elements.insert(0, remaining)
                        token = f"{token} {element}"
                        in_string = False
                    else:
                        token = f"{token} {element}"
                        element = self._buffered_elements.pop(0)

                token = token[1:]  # first character is always space

            else:
                token = element

                # check for direct types
                if element.isdigit():
                    ttype = TTypes.INT_CONST

                elif element in KEYWORDS:
                    ttype = TTypes.KEYWORD

                elif element and element[0] in SYMBOLS:
                    remaining = element[1:]
                    if remaining:
                        self._buffered_elements.insert(0, remaining)
                    token = element[0]
                    ttype = TTypes.SYMBOL

                else:
                    for index, character in enumerate(element):
                        if character in SYMBOLS:
                            ttype = None
                            element, remaining = element[:index], element[index:]
                            self._buffered_elements.insert(0, remaining)
                            break
                    else:
                        # if no symbols were found, whole element must be an identifier
                        ttype = TTypes.IDENTIFIER
                        token = element

                # if symbol was found, must be either int_const, keyword, or identifier
                if ttype is None:
                    token = element
                    if element.isdigit():
                        ttype = TTypes.INT_CONST
                    elif element in KEYWORDS:
                        ttype = TTypes.KEYWORD
                    else:
                        ttype = TTypes.IDENTIFIER

            self.current_token = token
            self.token_type = ttype

            return VALID_TOKEN

    @property
    def symbol(self):
        token = self.current_token
        if token == '<':
            token = '&lt;'
        if token == '>':
            token = '&gt;'
        if token == '"':
            token = '&quot;'
        if token == '&':
            token = '&amp;'
        return token

    @property
    def identifier(self):
        return self.current_token

    @property
    def int_value(self):
        return self.current_token

    @property
    def string_value(self):
        return self.current_token
