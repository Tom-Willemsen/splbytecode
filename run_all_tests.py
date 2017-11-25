from __future__ import absolute_import

import sys
import unittest

from spl.tests.test_lexer import LexerTests
from spl.tests.test_parser import ParserTests

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        ParserTests,
        LexerTests,
    ]

    ret_vals = []
    for test_class in test_classes:
        suite = loader.loadTestsFromTestCase(test_class)
        ret_vals.append(unittest.TextTestRunner().run(suite).wasSuccessful())

    sys.exit(False in ret_vals)
