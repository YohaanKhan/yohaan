#############
# CONSTANTS #
#############

# All valid digit characters for number parsing
DIGITS = "0123456789"

##########
# ERRORS #
##########

class Error:
    def __init__ (self, error_name, pos_start, pos_end,  details):
        """
        Base class that stores the error name, its position and details.
        """
        self.pos_start = pos_start # where the error starts
        self.pos_end = pos_end # where the error ends
        self.error_name = error_name
        self.details = details

    def as_string(self):
        """
        Returns a string representation of the error
        """
        result = f"{self.error_name} : {self.details}"
        result += f"File {self.pos_start.fn}, line {self.pos_start.line + 1}"
        return result

class IllegalCharError(Error):
    """
    Error raised when an illegal character is encountered during lexing
    """
    def __init__(self, details, pos_start, pos_end):
        super().__init__("Illegal Character", pos_start, pos_end, details)


############
# POSITION #
############

class Position:
    def __init__(self, index, line, column, fn, ftxt):
        self.index = index # current character position
        self.line = line # current line number
        self.column = column # current column number
        self.fn = fn # file name
        self.ftxt = ftxt # full text

    def advance(self, currrent_char):
        """
        Advances the position by one character. Updates index, line, and column accordingly.
        """
        self.index += 1
        self.column += 1

         # If we hit a newline, move to next line and reset column
        if currrent_char == '\n':
            self.line += 1
            self.column = 0
        
        return self
    
    def copy(self):
        """
        Returns a copy of the current position
        """
        return Position(self.index, self.line, self.column, self.fn, self.ftxt)

##########
# TOKENS #
##########

# Token types - these represent different kinds of symbols in this language
TT_INT      = 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'

class Token:
    def __init__(self, type_, value=None):
        """
        Represents a token in the source code.
        """
        self.type = type_
        self.value = value

    def __repr__(self):
        """
        Returns a string representation of the token. 
        """
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    
#########    
# lEXER #
#########

class Lexer:
    """
    Responsible for converting the input text into tokens
    Example: "22 + 11" -> [INT:22, PLUS, INT:11]
    """
    def __init__(self, text, fn):
        self.fn = fn
        self.text = text
        # Start at position -1 so first advance() brings us to index 0
        self.pos = Position(-1, 0, -1, text, fn)
        self.current_char = None
        self.advance()

    def advance(self):
        """
        Advances the lexer to the next character in the input text
        """
        self.pos.advance(self.current_char)
        # Checks if we are still within the bounds of the text
        if self.pos.index < len(self.text):
            self.current_char = self.text[self.pos.index]
        else:
            self.current_char = None

    def make_tokens(self):
        """
        MAIN METHOD
        Tokenizes the entire input text and returns a list of tokens or an error if encountered
        """
        tokens = []

        while self.current_char is not None:
            # Skip whitespace
            if self.current_char in ' \t':
                self.advance()

            # if a number, we parse the entire number
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())

            # single character tokens 
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS))
                self.advance()

            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS))
                self.advance()

            elif self.current_char == "*":
                tokens.append(Token(TT_MUL))
                self.advance()

            elif self.current_char == "/":
                tokens.append(Token(TT_DIV))
                self.advance()

            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN))
                self.advance()

            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN))
                self.advance()

            # if we encounter an unknown error, we return an error
            else:
                # along with its position
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError("'" + char + "'", pos_start, self.pos.copy())

        return tokens, None
            
    def make_number(self):
        """
        Parses a number, handles INT and FLOAT types
        """
        num_str = ''
        dot_count = 0

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        # Return depends on the number of dots encountered
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))

##########
# RUNNER #
##########

def run(text, fn='<stdin>'):
    """
    Main entry point - takes source code text and returns tokens
    
    Args:
        text: The source code to tokenize
        fn: Filename (defaults to '<stdin>' for direct input)
    
    Returns:
        (tokens, error) - tokens is list if successful, error is None if no errors
    """
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()

    return tokens, error