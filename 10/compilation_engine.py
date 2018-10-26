from jack_tokenizer import JackTokenizer, TTypes, Keywords, VALID_TOKEN


class CompilationEngine:
    def __init__(self):
        self._tokenizer = None
        self._output_file = None
        self._offset = None

    @property
    def _token_n_type(self):
        return self._tokenizer.current_token, self._tokenizer.token_type

    @property
    def _valid_types(self):
        return 'int', 'char', 'boolean'

    @property
    def _valid_statements(self):
        return 'let', 'if', 'while', 'do', 'return'

    @property
    def _valid_operators(self):
        return '+', '-', '*', '/', '&', '|', '<', '>', '='

    def _is_valid_term_start(self, token, ttype):
        if ttype in (TTypes.INT_CONST, TTypes.STRING_CONST, TTypes.IDENTIFIER):
            return True
        elif token in ('true', 'false', 'null', 'this', '(', '-', '~', *self._valid_operators):
            return True
        else:
            return False

    def _raise_missing(self, symbol):
        line_n = self._tokenizer.line_number
        raise Exception(f"{symbol} expected. Line {line_n}")

    def _open_tag(self, tag, new_line=True):
        nl = '\n' if new_line else ''
        pad = ' ' * self._offset
        self._output_file.write(f"{pad}<{tag}>{nl}")

        self._offset = self._offset + 2 if new_line else self._offset

    def _write_token(self, tag, token):
        if tag == 'symbol':
            token = self._tokenizer.symbol

        self._open_tag(tag, new_line=False)
        self._output_file.write(f" {token} ")
        self._close_tag(tag, new_line=False)

    def _close_tag(self, tag, new_line=True):
        self._offset = self._offset - 2 if new_line else self._offset

        pad = ' ' * self._offset if new_line else ''
        self._output_file.write(f"{pad}</{tag}>\n")

    def _advance(self):
        self._tokenizer.advance()
        return self._tokenizer.current_token, self._tokenizer.token_type

    def compile(self, input_file, output_file):
        self._tokenizer = JackTokenizer(input_file)
        self._output_file = output_file
        self._offset = 0

        while self._tokenizer.has_more_tokens:
            if self._tokenizer.advance() == VALID_TOKEN:
                if self._tokenizer.current_token == 'class':
                    tag = 'class'
                    self._open_tag(tag)
                    self._compile_class()
                    self._close_tag(tag)
                else:
                    line_n = self._tokenizer.line_number
                    raise Exception(f"Class declaration expected. Line {line_n}")

    def _compile_class(self):
        self._write_token(tag='keyword', token='class')

        token, ttype = self._advance()

        if ttype == TTypes.IDENTIFIER:
            tag = TTypes.IDENTIFIER.value
            self._write_token(tag, token)

            token, _ = self._advance()
            if token == '{':
                self._write_token(tag='symbol', token=token)
                token, ttype = self._advance()
                while token in ('static', 'field'):
                    tag = 'classVarDec'
                    self._open_tag(tag)
                    self._compile_class_var_dec()
                    self._close_tag(tag)

                    token, ttype = self._advance()

                while token in ('constructor', 'function', 'method'):
                    tag = 'subroutineDec'
                    self._open_tag(tag)
                    self._compile_subroutine()
                    self._close_tag(tag)

                    token, ttype = self._advance()

                if token == '}':
                    self._write_token(tag='symbol', token=token)
                else:
                    self._raise_missing('"}"')

            else:
                self._raise_missing('"{"')

        else:
            line_n = self._tokenizer.line_number
            raise Exception(f"Invalid class name declaration. Line {line_n}")

    def _compile_class_var_dec(self):
        token = self._tokenizer.current_token
        self._write_token(tag='keyword', token=token)

        token, ttype = self._advance()

        if token in self._valid_types or ttype == TTypes.IDENTIFIER:
            tag = ttype.value
            self._write_token(tag=tag, token=token)

            token, ttype = self._advance()

            v = False
            while ttype == TTypes.IDENTIFIER:
                v = True
                self._write_token(tag='identifier', token=token)
                token, ttype = self._advance()
                if token == ',':
                    self._write_token(tag='symbol', token=token)
                    token, ttype = self._advance()
                    continue
                else:
                    break
            if not v:
                self._raise_missing('Valid variable name')

            if token == ';':
                self._write_token(tag='symbol', token=token)
            else:
                self._raise_missing('";"')

        else:
            self._raise_missing('Valid variable type')

    def _compile_subroutine(self):
        token = self._tokenizer.current_token
        self._write_token(tag='keyword', token=token)

        token, ttype = self._advance()

        if token in ('void', *self._valid_types) or ttype == TTypes.IDENTIFIER:
            tag = ttype.value
            self._write_token(tag=tag, token=token)

            token, ttype = self._advance()

            if ttype == TTypes.IDENTIFIER:
                self._write_token(tag='identifier', token=token)

                token, ttype = self._advance()

                if token == '(':
                    self._write_token(tag='symbol', token=token)
                    tag = 'parameterList'
                    self._open_tag(tag)
                    self._compile_parameter_list()
                    self._close_tag(tag)

                    token, _ = self._token_n_type

                    if token == ')':
                        self._write_token(tag='symbol', token=token)
                        self._open_tag('subroutineBody')

                        token, ttype = self._advance()

                        if token == '{':
                            self._write_token(tag='symbol', token=token)
                            tag = 'varDec'
                            while True:
                                token, _ = self._advance()
                                if token == 'var':
                                    self._open_tag(tag)
                                    self._compile_var_dec()
                                    self._close_tag(tag)
                                else:
                                    break

                            tag = 'statements'
                            if token in self._valid_statements:
                                self._open_tag(tag)
                                self._compile_statements()
                                self._close_tag(tag)

                            token, _ = self._token_n_type
                            if token == '}':
                                self._write_token(tag='symbol', token=token)
                                self._close_tag('subroutineBody')
                            else:
                                self._raise_missing('"}"')
                        else:
                            self._raise_missing('"{"')
                    else:
                        self._raise_missing('")"')
                else:
                    self._raise_missing('"("')
            else:
                self._raise_missing('Valid subroutine name')
        else:
            self._raise_missing('Valid subroutine type')

    def _compile_parameter_list(self):
        token, ttype = self._advance()
        if token == ')':
            return

        elif token in self._valid_types or token == TTypes.IDENTIFIER:
            tag = ttype.value
            self._write_token(tag=tag, token=token)

            token, ttype = self._advance()
            v = False
            while ttype == TTypes.IDENTIFIER:
                v = True
                self._write_token(tag='identifier', token=token)
                token, ttype = self._advance()
                if token == ',':
                    self._write_token(tag='symbol', token=token)
                    token, ttype = self._advance()
                    if token in self._valid_types or ttype == TTypes.IDENTIFIER:
                        tag = ttype.value
                        self._write_token(tag=tag, token=token)
                        token, ttype = self._advance()
                    continue
                elif token == ')':
                    return
                else:
                    break
            if not v:
                self._raise_missing('Valid variable name')
        else:
            self._raise_missing('Valid variable type')

    def _compile_var_dec(self):
        token, _ = self._token_n_type
        self._write_token(tag='keyword', token=token)  # token == 'var'

        token, ttype = self._advance()

        if token in self._valid_types or ttype == TTypes.IDENTIFIER:
            tag = ttype.value
            self._write_token(tag=tag, token=token)

            token, ttype = self._advance()

            v = False
            while ttype == TTypes.IDENTIFIER:
                v = True
                self._write_token(tag='identifier', token=token)
                token, _ = self._advance()

                if token == ',':
                    self._write_token(tag='symbol', token=token)
                    token, ttype = self._advance()
                    continue
                elif token == ';':
                    self._write_token(tag='symbol', token=token)
                    break
                else:
                    self._raise_missing('Valid variable declaration')
            if not v:
                self._raise_missing('Valid variable name')
        else:
            self._raise_missing('Valid variable type')

    def _compile_statements(self):
        token, _ = self._token_n_type

        while token in self._valid_statements:
            tag = None
            comp_call = None
            if token == 'let':
                tag = 'letStatement'
                comp_call = self._compile_let

            if token == 'if':
                tag = 'ifStatement'
                comp_call = self._compile_if

            if token == 'while':
                tag = 'whileStatement'
                comp_call = self._compile_while

            if token == 'do':
                tag = 'doStatement'
                comp_call = self._compile_do

            if token == 'return':
                tag = 'returnStatement'
                comp_call = self._compile_return

            self._open_tag(tag)
            self._write_token(tag='keyword', token=token)
            comp_call()
            self._close_tag(tag)

            token, _ = self._token_n_type

            if token in self._valid_statements:
                continue
            else:
                token, _ = self._advance()

    def _compile_let(self):
        token, ttype = self._advance()

        if ttype == TTypes.IDENTIFIER:
            self._write_token(tag='identifier', token=token)
            token, _ = self._advance()
            if token == '[':
                self._write_token(tag='symbol', token=token)
                tag = 'expression'
                self._advance()
                self._open_tag(tag)
                self._compile_expression()
                self._close_tag(tag)

                token, _ = self._token_n_type

                if token == ']':
                    self._write_token(tag='symbol', token=token)
                    token, _ = self._advance()
                else:
                    self._raise_missing('"]"')

            if token == '=':
                self._write_token(tag='symbol', token=token)
                self._advance()

                tag = 'expression'
                self._open_tag(tag)
                self._compile_expression()
                self._close_tag(tag)

                token, _ = self._token_n_type
                if token == ';':
                    self._write_token(tag='symbol', token=token)
                    return
                else:
                    self._raise_missing('";"')
            else:
                self._raise_missing('"="')
        else:
            self._raise_missing('Valid variable name')

    def _compile_if(self):
        token, _ = self._advance()

        if token == '(':
            self._write_token(tag='symbol', token=token)
            self._advance()
            tag = 'expression'
            self._open_tag(tag)
            self._compile_expression()
            self._close_tag(tag)

            token, _ = self._token_n_type
            if token == ')':
                self._write_token(tag='symbol', token=token)
                token, _ = self._advance()
                if token == '{':
                    self._write_token(tag='symbol', token=token)

                    token, _ = self._advance()

                    tag = 'statements'
                    if token in self._valid_statements:
                        self._open_tag(tag)
                        self._compile_statements()
                        self._close_tag(tag)

                    token, _ = self._token_n_type
                    if token == '}':
                        self._write_token(tag='symbol', token=token)
                        token, _ = self._advance()
                        if token == 'else':
                            self._write_token(tag='keyword', token=token)
                            token, _ = self._advance()
                            if token == '{':
                                self._write_token(tag='symbol', token=token)
                                token, _ = self._advance()
                                tag = 'statements'
                                if token in self._valid_statements:
                                    self._open_tag(tag)
                                    self._compile_statements()
                                    self._close_tag(tag)

                                token, _ = self._token_n_type
                                if token == '}':
                                    self._write_token(tag='symbol', token=token)
                                else:
                                    self._raise_missing('"}"')
                            else:
                                self._raise_missing('"{"')
                    else:
                        self._raise_missing('"}"')
                else:
                    self._raise_missing('"{"')
            else:
                self._raise_missing('")"')
        else:
            self._raise_missing('"("')

    def _compile_while(self):
        token, _ = self._advance()
        if token == '(':
            self._write_token(tag='symbol', token=token)
            self._advance()
            tag = 'expression'
            self._open_tag(tag)
            self._compile_expression()
            self._close_tag(tag)

            token, _ = self._token_n_type
            if token == ')':
                self._write_token(tag='symbol', token=token)
                token, _ = self._advance()
                if token == '{':
                    self._write_token(tag='symbol', token=token)
                    token, ttype = self._advance()
                    tag = 'statements'
                    if token in self._valid_statements:
                        self._open_tag(tag)
                        self._compile_statements()
                        self._close_tag(tag)

                    token, _ = self._token_n_type
                    if token == '}':
                        self._write_token(tag='symbol', token=token)
                    else:
                        self._raise_missing('"}"')
                else:
                    self._raise_missing('"{"')
            else:
                self._raise_missing('")"')
        else:
            self._raise_missing('"("')

    def _compile_do(self):
        token, ttype = self._advance()

        if ttype == TTypes.IDENTIFIER:
            self._write_token(tag='identifier', token=token)
            token, _ = self._advance()
            if token == '.':
                self._write_token(tag='symbol', token=token)
                token, ttype = self._advance()
                if ttype == TTypes.IDENTIFIER:
                    self._write_token(tag='identifier', token=token)
                    token, _ = self._advance()
                else:
                    self._raise_missing('Valid class or variable name')
            if token == '(':
                self._write_token(tag='symbol', token=token)

                tag = 'expressionList'
                self._open_tag(tag)
                self._compile_expression_list()
                self._close_tag(tag)

                token, _ = self._token_n_type
                if token == ')':
                    self._write_token(tag='symbol', token=token)

                    token, _ = self._advance()
                    if token == ';':
                        self._write_token(tag='symbol', token=token)
                        return
                    else:
                        self._raise_missing('";"')
                else:
                    self._raise_missing('")"')
            else:
                self._raise_missing('"("')
        else:
            self._raise_missing('Subroutine call')

    def _compile_return(self):
        token, ttype = self._advance()
        tag = 'expression'

        if self._is_valid_term_start(token, ttype):
            self._open_tag(tag)
            self._compile_expression()
            self._close_tag(tag)

        token, _ = self._token_n_type
        if token == ';':
            self._write_token(tag='symbol', token=token)
        else:
            self._raise_missing('";"')

    def _compile_expression(self):
        token, ttype = self._token_n_type
        if self._is_valid_term_start(token, ttype):
            tag = 'term'
            self._open_tag(tag)
            self._compile_term()
            self._close_tag(tag)

            token, ttype = self._token_n_type

            while token in self._valid_operators:
                self._write_token(tag='symbol', token=token)
                token, ttype = self._advance()
                if self._is_valid_term_start(token, ttype):
                    tag = 'term'
                    self._open_tag(tag)
                    self._compile_term()
                    self._close_tag(tag)

                    token, ttype = self._token_n_type
                else:
                    self._raise_missing('Valid term')

    def _compile_term(self):
        token, ttype = self._token_n_type
        self._write_token(tag=ttype.value, token=token)

        if token in ('-', '~'):
            self._advance()
            tag = 'term'
            self._open_tag(tag)
            self._compile_term()
            self._close_tag(tag)

            return

        elif ttype in (TTypes.INT_CONST, TTypes.STRING_CONST) or token in ('true', 'false', 'null', 'this'):
            self._advance()
            return

        if token == '(':
            tag = 'expression'
            self._advance()
            self._open_tag(tag)
            self._compile_expression()
            self._close_tag(tag)

            token, _ = self._token_n_type

            if token == ')':
                self._write_token(tag='symbol', token=token)
                token, _ = self._advance()
            else:
                self._raise_missing('")"')

        elif ttype == TTypes.IDENTIFIER:
            token, ttype = self._advance()

            if token == '[':
                self._write_token(tag='symbol', token=token)
                tag = 'expression'
                self._advance()
                self._open_tag(tag)
                self._compile_expression()
                self._close_tag(tag)

                token, _ = self._token_n_type

                if token == ']':
                    self._write_token(tag='symbol', token=token)
                    token, _ = self._advance()
                else:
                    self._raise_missing('"]"')

                return

            if token == '.':
                self._write_token(tag='symbol', token=token)
                token, ttype = self._advance()
                if ttype == TTypes.IDENTIFIER:
                    self._write_token(tag='identifier', token=token)
                    token, _ = self._advance()
                else:
                    self._raise_missing('Valid class or variable name')

            if token == '(':
                self._write_token(tag='symbol', token=token)

                tag = 'expressionList'
                self._open_tag(tag)
                self._compile_expression_list()
                self._close_tag(tag)

                token, _ = self._token_n_type
                if token == ')':
                    self._write_token(tag='symbol', token=token)

                    token, _ = self._advance()
                else:
                    self._raise_missing('")"')

    def _compile_expression_list(self):
        token, ttype = self._advance()
        if self._is_valid_term_start(token, ttype):
            tag = 'expression'
            self._open_tag(tag)
            self._compile_expression()
            self._close_tag(tag)

            token, _ = self._token_n_type

        while True:
            if token == ',':
                self._write_token(tag='symbol', token=token)
                token, ttype = self._advance()

                if self._is_valid_term_start(token, ttype):
                    tag = 'expression'
                    self._open_tag(tag)
                    self._compile_expression()
                    self._close_tag(tag)

                    token, _ = self._token_n_type
                else:
                    self._raise_missing('Valid expression')
            if token == ')':
                break
