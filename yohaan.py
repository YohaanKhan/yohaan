#######################################
# IMPORTS #
#######################################

from string_with_arrows import string_with_arrows

#######################################
# CONSTANTS #
#######################################

# All valid digit characters for number parsing
DIGITS = '0123456789'

#######################################
# ERRORS #
#######################################

class Error:
		def __init__ (self, pos_start, pos_end, error_name, details):
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
				result  = f'{self.error_name}: {self.details}\n'
				result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
				result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
				return result

class IllegalCharError(Error):
		"""
		Error raised when an illegal character is encountered during lexing
		"""
		def __init__(self, pos_start, pos_end, details):
				super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
		def __init__(self, pos_start, pos_end, details=''):
				super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

#######################################
# POSITION #
#######################################

class Position:
		def __init__(self, idx, ln, col, fn, ftxt):
				self.idx = idx # current character position
				self.ln = ln # current line number
				self.col = col # current column number
				self.fn = fn # file name
				self.ftxt = ftxt # full text

		def advance(self, current_char=None):
				"""
				Advances the position by one character. Updates index, line, and column accordingly.
				"""
				self.idx += 1
				self.col += 1

				# If we hit a newline, move to next line and reset column
				if current_char == '\n':
						self.ln += 1
						self.col = 0

				return self

		def copy(self):
				"""
				Returns a copy of the current position
				"""
				return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS #
#######################################

# Token types - these represent different kinds of symbols in this language
TT_INT			= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EOF			= 'EOF'

class Token:
		def __init__(self, type_, value=None, pos_start=None, pos_end=None):
				"""
				Represents a token in the source code.
				"""
				self.type = type_
				self.value = value

				if pos_start:
					self.pos_start = pos_start.copy()
					self.pos_end = pos_start.copy()
					self.pos_end.advance()

				if pos_end:
					self.pos_end = pos_end
		
		def __repr__(self):
				"""
				Returns a string representation of the token. 
				"""
				if self.value: return f'{self.type}:{self.value}'
				return f'{self.type}'

#######################################
# lEXER #
#######################################

class Lexer:
		"""
		Responsible for converting the input text into tokens
		Example: "22 + 11" -> [INT:22, PLUS, INT:11]
		"""
		def __init__(self, fn, text):
				self.fn = fn
				self.text = text
				# Start at position -1 so first advance() brings us to index 0
				self.pos = Position(-1, 0, -1, fn, text)
				self.current_char = None
				self.advance()
		
		def advance(self):
				"""
				Advances the lexer to the next character in the input text
				"""
				self.pos.advance(self.current_char)
				self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

		def make_tokens(self):
				"""
				MAIN METHOD
				Tokenizes the entire input text and returns a list of tokens or an error if encountered
				"""
				tokens = []

				while self.current_char != None:
						# Skip whitespace
						if self.current_char in ' \t':
								self.advance()

						# if a number, we parse the entire number
						elif self.current_char in DIGITS:
								tokens.append(self.make_number())

						# single character tokens 
						elif self.current_char == '+':
								tokens.append(Token(TT_PLUS, pos_start=self.pos))
								self.advance()

						elif self.current_char == '-':
								tokens.append(Token(TT_MINUS, pos_start=self.pos))
								self.advance()

						elif self.current_char == '*':
								tokens.append(Token(TT_MUL, pos_start=self.pos))
								self.advance()

						elif self.current_char == '/':
								tokens.append(Token(TT_DIV, pos_start=self.pos))
								self.advance()

						elif self.current_char == '(':
								tokens.append(Token(TT_LPAREN, pos_start=self.pos))
								self.advance()

						elif self.current_char == ')':
								tokens.append(Token(TT_RPAREN, pos_start=self.pos))
								self.advance()

						# if we encounter an unknown error, we return an error
						else:
								pos_start = self.pos.copy()
								char = self.current_char
								self.advance()
								return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

				tokens.append(Token(TT_EOF, pos_start=self.pos))
				return tokens, None

		def make_number(self):
				"""
				Parses a number, handles INT and FLOAT types
				"""
				num_str = ''
				dot_count = 0
				pos_start = self.pos.copy()

				while self.current_char != None and self.current_char in DIGITS + '.':
						if self.current_char == '.':
								if dot_count == 1:
										break
								dot_count += 1
						num_str += self.current_char
						self.advance()

				# Return depends on the number of dots encountered
				if dot_count == 0:
						return Token(TT_INT, int(num_str), pos_start, self.pos)
				else:
						return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

#######################################
# NODES #
#######################################

class NumberNode:
		def __init__(self, tok):
				self.tok = tok

		def __repr__(self):
				return f'{self.tok}'

class BinOpNode:
		def __init__(self, left_node, op_tok, right_node):
				self.left_node = left_node
				self.op_tok = op_tok
				self.right_node = right_node

		def __repr__(self):
				return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
		def __init__(self, op_tok, node):
				self.op_tok = op_tok
				self.node = node

		def __repr__(self):
				return f'({self.op_tok}, {self.node})'

#######################################
# PARSE RESULT #
#######################################

class ParseResult:
		def __init__(self):
				self.error = None
				self.node = None

		def register(self, res):
				if isinstance(res, ParseResult):
						if res.error:
								self.error = res.error
						return res.node
				return res
		
		def success(self, node):
				self.node = node
				return self
		
		def failure(self, error):
				self.error = error
				return self

#######################################
# PARSER #
#######################################

class Parser:
		def __init__(self, tokens):
				self.tokens = tokens
				self.tok_idx = -1
				self.advance()

		def advance(self):
				self.tok_idx += 1
				if self.tok_idx < len(self.tokens):
						self.current_tok = self.tokens[self.tok_idx]
				return self.current_tok
		
		def parse(self):
				res = self.expr()
				if not res.error and self.current_tok.type != TT_EOF:
						return res.failure(InvalidSyntaxError(
								self.current_tok.pos_start,
								self.current_tok.pos_end,
								"Expected '+', '-', '*' or '/'"
						))
				return res

		def factor(self):
				res = ParseResult()
				tok = self.current_tok

				if tok.type in (TT_PLUS, TT_MINUS):
						res.register(self.advance())
						factor = res.register(self.factor())
						if res.error:
								return res
						return res.success(UnaryOpNode(tok, factor))

				elif tok.type in (TT_INT, TT_FLOAT):
						res.register(self.advance())
						return res.success(NumberNode(tok))

				elif tok.type == TT_LPAREN:
						res.register(self.advance())
						expr = res.register(self.expr())
						if res.error:
								return res
						if self.current_tok.type == TT_RPAREN:
								res.register(self.advance())
								return res.success(expr)
						else:
								return res.failure(InvalidSyntaxError(
										self.current_tok.pos_start,
										self.current_tok.pos_end,
										"Expected ')'"
								))

				return res.failure(InvalidSyntaxError(
						tok.pos_start,
						tok.pos_end,
						"Expected number or '('"
				))

		def term(self):
				return self.bin_op(self.factor, (TT_MUL, TT_DIV))

		def expr(self):
				return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

		def bin_op(self, func, ops):
				res = ParseResult()
				left = res.register(func())
				if res.error:
						return res

				while self.current_tok.type in ops:
						op_tok = self.current_tok
						res.register(self.advance())
						right = res.register(func())
						if res.error:
								return res
						left = BinOpNode(left, op_tok, right)

				return res.success(left)

#######################################
# RUNNER #
#######################################

def run(fn, text):
		"""
		Main entry point - takes source code text and returns tokens
		
		Args:
				text: The source code to tokenize
				fn: Filename (defaults to '<stdin>' for direct input)
		
		Returns:
				(tokens, error) - tokens is list if successful, error is None if no errors
		"""

		# generates tokens
		lexer = Lexer(fn, text)
		tokens, error = lexer.make_tokens()
		if error:
				return None, error

		#generates AST
		parser = Parser(tokens)
		ast = parser.parse()

		return ast.node, ast.error
