import os

from compilation_engine import CompilationEngine, JackTokenizer, TTypes, VALID_TOKEN


class JackAnalyzer:
    @staticmethod
    def tokenize(input_file_path):
        input_file = open(input_file_path)

        output_file_path = f"{input_file_path.strip('.jack')}_.xml"
        output_file = open(output_file_path, 'w')

        tokenizer = JackTokenizer(input_file)

        output_file.write('<tokens>\n')
        while tokenizer.has_more_tokens:
            if tokenizer.advance() is VALID_TOKEN:
                token = tokenizer.current_token
                ttype = tokenizer.token_type

                if ttype == TTypes.SYMBOL:
                    token = tokenizer.symbol

                ttype = tokenizer.token_type.value

                line = f"<{ttype}> {token} </{ttype}>\n"
                output_file.write(line)

        output_file.write('</tokens>\n')

        input_file.close()
        output_file.close()

    @staticmethod
    def compile(input_file_path):
        input_file = open(input_file_path)

        output_file_path = f"{input_file_path.strip('.jack')}_.xml"
        output_file = open(output_file_path, 'w')

        comp_engine = CompilationEngine()
        comp_engine.compile(input_file, output_file)


def main(input_path: str):
    analyzer = JackAnalyzer()

    if os.path.isfile(input_path):
        analyzer.compile(input_path)
    else:
        input_paths = [os.path.join(input_path, p)
                       for p in os.listdir(input_path) if p.endswith('.jack')]
        for input_path in input_paths:
            analyzer.compile(input_path)


if __name__ == '__main__':
    import sys
    path = sys.argv[1]
    # path = 'ExpressionLessSquare/SquareGame.jack'
    main(path)
