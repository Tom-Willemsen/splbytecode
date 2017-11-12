import sys
import os
import argparse

from java_class.builder import Builder, CompilationError
from java_class.exporter import Exporter
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
                            help="Major version number of java output class.", default=53)
    arg_parser.add_argument('--cls-min-version', type=int,
                            help="Minor version number of java output class.", default=0)

    args = arg_parser.parse_args()

    spl_parser = Parser(args.input)

    try:
        var_initializations, ast = spl_parser.play()
    except SPLSyntaxError as e:
        print("Syntax error: {}".format(e))
        sys.exit(1)

    try:
        cls_builder = Builder(args.cls_name)
        cls_builder.ast_dump(ast)
        cls = cls_builder.build()
    except CompilationError as e:
        print("Compiler error: {}".format(e))
        sys.exit(1)

    cls.set_version(args.cls_maj_version, args.cls_min_version)
    Exporter(cls).export_as_file(args.output_dir)
