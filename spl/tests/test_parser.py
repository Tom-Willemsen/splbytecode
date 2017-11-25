from __future__ import absolute_import

import unittest

from spl.parser import Parser, SPLSyntaxError
from spl.tokens import TokenTypes, Token


def _add_scene(tokens):
    tokens.extend([
        Token(TokenTypes.Scene),
        Token(TokenTypes.Numeral),
        Token(TokenTypes.Colon),
        Token(TokenTypes.EndLine),
    ])
    return tokens


def _add_act(tokens):
    tokens.extend([
        Token(TokenTypes.Act),
        Token(TokenTypes.Numeral),
        Token(TokenTypes.Colon),
        Token(TokenTypes.EndLine),
    ])
    return tokens


class ParserTests(unittest.TestCase):

    def test_GIVEN_trying_to_parse_play_WHEN_eof_is_the_only_token_THEN_syntax_error_is_raised(self):
        tokens = [Token(TokenTypes.Eof)]
        parser = Parser(t for t in tokens)

        with self.assertRaises(SPLSyntaxError):
            parser.play()

    def test_GIVEN_trying_to_parse_play_WHEN_minimal_valid_play_THEN_no_errors_raised(self):
        tokens = [Token(TokenTypes.EndLine)]  # Have to have an initial line.
        tokens = _add_act(tokens)
        tokens = _add_scene(tokens)
        tokens.append(Token(TokenTypes.Eof))

        parser = Parser(t for t in tokens)

        parser.play()

    def test_GIVEN_trying_to_parse_play_WHEN_play_with_multiple_acts_and_scenes_THEN_no_errors_raised(self):
        tokens = [Token(TokenTypes.EndLine)]  # Have to have an initial line.
        tokens = _add_act(tokens)
        tokens = _add_scene(tokens)
        tokens = _add_scene(tokens)
        tokens = _add_act(tokens)
        tokens = _add_scene(tokens)
        tokens = _add_scene(tokens)
        tokens = _add_scene(tokens)
        tokens.append(Token(TokenTypes.Eof))

        parser = Parser(t for t in tokens)

        parser.play()

    def test_GIVEN_two_characters_on_stage_WHEN_one_speaking_THEN_first_person_pronoun_gets_speaking_character(self):
        tokens = [
            Token(TokenTypes.FirstPronoun),
            Token(TokenTypes.Eof)
        ]

        parser = Parser(t for t in tokens)

        parser.onstage = ["A", "B"]
        parser.speaking = "A"

        self.assertEqual(parser.character_name(), "A")

    def test_GIVEN_two_characters_on_stage_WHEN_one_speaking_THEN_2nd_person_pronoun_gets_not_speaking_character(self):
        tokens = [
            Token(TokenTypes.SecondPronoun),
            Token(TokenTypes.Eof)
        ]

        parser = Parser(t for t in tokens)

        parser.onstage = ["A", "B"]
        parser.speaking = "A"

        self.assertEqual(parser.character_name(), "B")

    def test_GIVEN_two_characters_on_stage_WHEN_get_character_by_name_THEN_can_get_that_character(self):
        tokens = [
            Token(TokenTypes.Name, "C"),
            Token(TokenTypes.Eof)
        ]

        parser = Parser(t for t in tokens)

        parser.onstage = ["A", "B"]
        parser.speaking = "A"

        self.assertEqual(parser.character_name(), "C")

    def test_GIVEN_nonsense_token_WHEN_get_character_by_name_THEN_parse_error(self):
        tokens = [
            Token(TokenTypes.Numeral),
            Token(TokenTypes.Eof)
        ]

        parser = Parser(t for t in tokens)

        parser.onstage = ["A", "B"]
        parser.speaking = "A"

        with self.assertRaises(SPLSyntaxError):
            parser.character_name()

    def test_GIVEN_variable_does_not_exist_WHEN_declaring_variable_THEN_no_parse_error(self):
        tokens = [
            Token(TokenTypes.Name, "A"),
            Token(TokenTypes.Comma),
            Token(TokenTypes.Noun, 1),
            Token(TokenTypes.EndLine, 1),
            Token(TokenTypes.Eof, 1),
        ]

        parser = Parser(t for t in tokens)

        parser.var_assignment()

    def test_GIVEN_variable_already_exists_WHEN_declaring_variable_THEN_parse_error(self):
        tokens = [
            Token(TokenTypes.Name, "A"),
            Token(TokenTypes.Comma),
            Token(TokenTypes.Noun, 1),
            Token(TokenTypes.EndLine, 1),
            Token(TokenTypes.Eof, 1),
        ]

        parser = Parser(t for t in tokens)

        parser.vars_table = ["A"]

        with self.assertRaises(SPLSyntaxError):
            parser.var_assignment()

    def test_GIVEN_exeunt_statement_WHEN_parsing_stage_control_THEN_no_parse_error(self):
        tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Exeunt),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        parser = Parser(t for t in tokens)

        parser.stagecontrol()

    def test_GIVEN_enter_statement_with_no_characters_WHEN_parsing_stage_control_THEN_parse_error(self):
        tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Enter),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        parser = Parser(t for t in tokens)

        with self.assertRaises(SPLSyntaxError):
            parser.stagecontrol()

    def test_GIVEN_enter_statement_with_one_character_WHEN_parsing_stage_control_THEN_no_parse_error(self):
        tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Enter),
            Token(TokenTypes.Name, "A"),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        parser = Parser(t for t in tokens)

        parser.stagecontrol()

    def test_GIVEN_enter_statement_with_two_characters_WHEN_parsing_stage_control_THEN_no_parse_error(self):
        tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Enter),
            Token(TokenTypes.Name, "A"),
            Token(TokenTypes.Add),
            Token(TokenTypes.Name, "B"),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        parser = Parser(t for t in tokens)

        parser.stagecontrol()

    def test_GIVEN_enter_statement_with_two_identical_characters_WHEN_parsing_stage_control_THEN_parse_error(self):
        tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Enter),
            Token(TokenTypes.Name, "A"),
            Token(TokenTypes.Add),
            Token(TokenTypes.Name, "A"),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        parser = Parser(t for t in tokens)

        with self.assertRaises(SPLSyntaxError):
            parser.stagecontrol()

    def test_GIVEN_a_character_on_stage_WHEN_that_character_leaves_THEN_no_parse_error(self):
        tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Exit),
            Token(TokenTypes.Name, "A"),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        parser = Parser(t for t in tokens)
        parser.onstage = ["A"]

        parser.stagecontrol()

    def test_GIVEN_a_character_not_on_stage_WHEN_that_character_leaves_THEN_parse_error(self):
        tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Exit),
            Token(TokenTypes.Name, "A"),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        parser = Parser(t for t in tokens)

        with self.assertRaises(SPLSyntaxError):
            parser.stagecontrol()

    def test_GIVEN_many_characters_on_stage_WHEN_exeunt_THEN_noone_left_on_stage(self):
        tokens = [
            Token(TokenTypes.OpenSqBracket),
            Token(TokenTypes.Exeunt),
            Token(TokenTypes.CloseSqBracket),
            Token(TokenTypes.Eof),
        ]

        parser = Parser(t for t in tokens)

        parser.onstage = ["A", "B", "C", "D"]

        parser.stagecontrol()

        self.assertEqual(parser.onstage, [])
