import sys
import unittest

from java_class.tests.test_constant_pool import ConstantPoolTests
from java_class.tests.test_java_class import JavaClassTests
from spl.tests.test_lexer import LexerTests
from spl.tests.test_parser import ParserTests

if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    test_classes = [
        ParserTests,
        LexerTests,
        JavaClassTests,
        ConstantPoolTests,
    ]

    ret_vals = []
    for test_class in test_classes:
        suite = loader.loadTestsFromTestCase(test_class)
        ret_vals.append(runner.run(suite).wasSuccessful())

    sys.exit(False in ret_vals)
