import sys
import os
import argparse

from intermediate.asl import flatten_ast
from java_class.builder import Builder, CompilationError
from java_class.exporter import Exporter
from spl.lexer import Lexer
from spl.parser import Parser, SPLSyntaxError

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description='Shakespeare programming language to java bytecode compiler.',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('input', type=str,
                            help="File path to the SPL input file.")
    arg_parser.add_argument('--output-dir', type=str,
                            help="Output directory.", default=os.getcwd())
    arg_parser.add_argument('--cls-name', type=str,
                            help="Output class name.", default="SplProgram")
    arg_parser.add_argument('--cls-maj-version', type=int,
                            help="Major version number of java output class.", default=50)
    arg_parser.add_argument('--cls-min-version', type=int,
                            help="Minor version number of java output class.", default=0)

    args = arg_parser.parse_args()

    with open(args.input) as f:
        spl_lexer = Lexer(f.read())

    spl_parser = Parser(spl_lexer.token_generator())

    try:
        ast = spl_parser.play()
        asl = flatten_ast(ast)
    except SPLSyntaxError as e:
        print("Syntax error: {}".format(e))
        sys.exit(1)

    try:
        cls = Builder(args.cls_name).asl_dump(asl).build()
        cls.set_version(args.cls_maj_version, args.cls_min_version)
    except CompilationError as e:
        print("Compiler error: {}".format(e))
        sys.exit(1)

    Exporter(cls).export_as_file(args.output_dir)
