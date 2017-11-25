import unittest

from spl.lexer import Lexer
from spl.tokens import Token, TokenTypes


class LexerTests(unittest.TestCase):

    def _assert_tokens_equal(self, actual, expected):
        self.assertEqual(len(actual), len(expected))

        for a, e in zip(actual, expected):
            self.assertEqual(a.type, e.type)
            self.assertEqual(a.value, e.value)

    def test_GIVEN_a_scene_declaration_WHEN_tokenizing_THEN_tokens_contain_necessary_information(self):
        lexer = Lexer("Scene I: Description.")

        expected_tokens = [
            Token(TokenTypes.Scene),
            Token(TokenTypes.Numeral, "i"),
            Token(TokenTypes.Colon),
            Token(TokenTypes.EndLine),
            Token(TokenTypes.Eof),
        ]

        tokens = [t for t in lexer.token_generator()]
        self.assertEqual(tokens, expected_tokens)

    def test_GIVEN_an_act_declaration_WHEN_tokenizing_THEN_tokens_contain_necessary_information(self):
        lexer = Lexer("Act IV: Description.")

        expected_tokens = [
            Token(TokenTypes.Act),
            Token(TokenTypes.Numeral, "iv"),
            Token(TokenTypes.Colon),
            Token(TokenTypes.EndLine),
            Token(TokenTypes.Eof),
        ]

        tokens = [t for t in lexer.token_generator()]
        self._assert_tokens_equal(tokens, expected_tokens)

    def test_GIVEN_an_enter_statement_WHEN_tokenizing_THEN_tokens_contain_necessary_information(self):
        lexer = Lexer("[Enter Hamlet and Romeo]")

        expected_tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Enter),
            Token(TokenTypes.Name, "hamlet"),
            Token(TokenTypes.Add, "+"),
            Token(TokenTypes.Name, "romeo"),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        tokens = [t for t in lexer.token_generator()]
        self._assert_tokens_equal(tokens, expected_tokens)

    def test_GIVEN_an_exit_statement_WHEN_tokenizing_THEN_tokens_contain_necessary_information(self):
        lexer = Lexer("[Exit Hamlet]")

        expected_tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Exit),
            Token(TokenTypes.Name, "hamlet"),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        tokens = [t for t in lexer.token_generator()]
        self._assert_tokens_equal(tokens, expected_tokens)

    def test_GIVEN_an_assignment_statement_WHEN_tokenizing_THEN_tokens_contain_necessary_information(self):
        lexer = Lexer("Romeo: You are a stupid pig!")

        expected_tokens = [
            Token(TokenTypes.Name, "romeo"),
            Token(TokenTypes.Colon),
            Token(TokenTypes.SecondPronoun),
            Token(TokenTypes.Adj, 2),
            Token(TokenTypes.Noun, -1),
            Token(TokenTypes.EndLine),
            Token(TokenTypes.Eof),
        ]

        tokens = [t for t in lexer.token_generator()]
        self._assert_tokens_equal(tokens, expected_tokens)

    def test_GIVEN_a_conditional_statement_WHEN_tokenizing_THEN_tokens_contain_necessary_information(self):
        lexer = Lexer("Romeo: Am I equal to Lady Macbeth?")

        expected_tokens = [
            Token(TokenTypes.Name, "romeo"),
            Token(TokenTypes.Colon),
            Token(TokenTypes.QuestionStart),
            Token(TokenTypes.FirstPronoun),
            Token(TokenTypes.Name, "lady macbeth"),
            Token(TokenTypes.QuestionMark),
            Token(TokenTypes.Eof),
        ]

        tokens = [t for t in lexer.token_generator()]
        self._assert_tokens_equal(tokens, expected_tokens)
