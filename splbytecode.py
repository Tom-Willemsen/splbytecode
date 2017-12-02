import sys
import os
import argparse

from intermediate.asl import flatten_ast
from java_class.builder import Builder, CompilationError
from java_class.exporter import Exporter
from spl.lexer import Lexer
from spl.parser import Parser, SPLSyntaxError


def main(input_file, output_dir, cls_name, cls_maj_version, cls_min_version, jar):
    with open(input_file) as f:
        spl_lexer = Lexer(f.read())

    spl_parser = Parser(spl_lexer.token_generator())

    ast = spl_parser.play()
    asl = flatten_ast(ast)

    cls = Builder(cls_name).asl_dump(asl).build()
    cls.set_version(cls_maj_version, cls_min_version)

    exporter = Exporter(cls)

    if jar:
        exporter.export_as_jar(output_dir)
    else:
        exporter.export_as_file(output_dir)


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(description='Shakespeare programming language to java bytecode compiler.',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('input', type=str,
                            help="File path to the SPL input file.")
    arg_parser.add_argument('--output-dir', type=str,
                            help="Output directory.", default=os.path.join(os.getcwd(), "bin"))
    arg_parser.add_argument('--cls-name', type=str,
                            help="Output class name.", default="SplProgram")
    arg_parser.add_argument('--cls-maj-version', type=int,
                            help="Major version number of java output class.", default=50)
    arg_parser.add_argument('--cls-min-version', type=int,
                            help="Minor version number of java output class.", default=0)
    arg_parser.add_argument('--jar', action='store_true',
                            help="Output as a .jar file instead of a .class file")

    args = arg_parser.parse_args()

    try:
        main(args.input, args.output_dir, args.cls_name, args.cls_maj_version, args.cls_min_version, args.jar)
    except SPLSyntaxError as e:
        print("Syntax error: {}".format(e))
        sys.exit(1)
    except CompilationError as e:
        print("Compiler error: {}".format(e))
        sys.exit(2)
    except Exception as e:
        print("Unknown error: {}".format(e))
        sys.exit(3)

    sys.exit(0)
