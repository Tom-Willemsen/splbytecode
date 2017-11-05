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
    arg_parser.add_argument('--output_dir', type=str,
                            help="Output directory.", default=os.getcwd())
    arg_parser.add_argument('--output_class', type=str,
                            help="Output class name.", default="SplProgram")

    args = arg_parser.parse_args()

    spl_parser = Parser(args.input)

    try:
        var_initializations, statements = spl_parser.play()
    except SPLSyntaxError as e:
        print("Syntax error: {}".format(e))
        sys.exit(1)

    try:
        cls_builder = Builder(args.output_class)
        for var in var_initializations:
            cls_builder.set_field(var, 0)

        for statement in statements:
            cls_builder.ast_dump(statement)

        cls = cls_builder.build()
    except CompilationError as e:
        print("Compiler error: {}".format(e))
        sys.exit(1)

    Exporter(cls).export_as_file(args.output_dir)
