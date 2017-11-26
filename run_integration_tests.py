import sys
import unittest
import os

import shutil

import splbytecode
import subprocess


CODE_DIR = "examples"
TEMP_OUTPUT_DIR = "tmp"


def class_name_from_filename(filename):
    return filename.split(".")[0].title()


def compile_spl(input_file, class_name):

    splbytecode.main(
        input_file=os.path.join(CODE_DIR, input_file),
        output_dir=os.path.join(TEMP_OUTPUT_DIR),
        cls_name=class_name,
        cls_maj_version=50,
        cls_min_version=0,
    )


def run_java(class_name, *args):

    command = ["java", "-cp", TEMP_OUTPUT_DIR, class_name] + [str(a) for a in args]

    return subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=10).decode()


def remove_cr_and_lf(text):
    return "".join(c for c in text if c not in ["\r", "\n"])


class IntegrationTests(unittest.TestCase):
    """
    These tests run the full compiler against the code in the "examples" directory and then execute the produced class,
    asserting that the output is as expected.
    """

    def test_GIVEN_hello_world_example_THEN_it_compiles_and_runs_without_error(self):
        filename = "hello.spl"
        class_name = class_name_from_filename(filename)

        compile_spl(filename, class_name)

        output = remove_cr_and_lf(run_java(class_name))

        self.assertEqual("HELLO, WORLD", output)

    def test_GIVEN_incrementor_example_THEN_it_compiles_and_runs_without_error(self):
        filename = "incrementor.spl"
        class_name = class_name_from_filename(filename)

        compile_spl(filename, class_name)

        output = remove_cr_and_lf(run_java(class_name, 100))

        self.assertEqual("101", output)

    def test_GIVEN_goto_example_THEN_it_compiles_and_runs_without_error(self):
        filename = "goto.spl"
        class_name = class_name_from_filename(filename)

        compile_spl(filename, class_name)

        output = remove_cr_and_lf(run_java(class_name))

        self.assertEqual("1", output)

    def test_GIVEN_conditional_goto_example_THEN_it_compiles_and_runs_without_error(self):
        filename = "condgoto.spl"
        class_name = class_name_from_filename(filename)

        compile_spl(filename, class_name)

        output = remove_cr_and_lf(run_java(class_name, 15))

        expected_output = "".join(str(n) for n in range(1, 16))

        self.assertEqual(expected_output, output)


if __name__ == "__main__":

    # Clean up any leftover output from previous tests
    # Don't do this immediately after running tests because the produced classes may be useful for debugging.
    if os.path.exists(TEMP_OUTPUT_DIR):
        shutil.rmtree(TEMP_OUTPUT_DIR)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()
    suite = loader.loadTestsFromTestCase(IntegrationTests)
    success = runner.run(suite).wasSuccessful()

    sys.exit(not success)
