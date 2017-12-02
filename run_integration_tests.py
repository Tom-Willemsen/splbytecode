import sys
import unittest
import os

import shutil

from math import sqrt

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

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=10)
    except TypeError as e:
        if "unexpected keyword argument 'timeout'" not in str(e):
            raise
        # Python 3.2 doesn't support timeout. So try again without one.
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    
    return output.decode()


def remove_junk_line(text):
    if text.split("\n")[0].startswith("Picked up _JAVA_OPTIONS:"):
        return text.split("\n")[1:]
    return text


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

        output = remove_cr_and_lf(remove_junk_line(run_java(class_name)))

        self.assertIn("HELLO, WORLD", output)

    def test_GIVEN_incrementor_example_THEN_it_compiles_and_runs_without_error(self):
        filename = "incrementor.spl"
        class_name = class_name_from_filename(filename)

        compile_spl(filename, class_name)

        output = remove_cr_and_lf(remove_junk_line(run_java(class_name, 12321)))

        self.assertIn("12322", output)

    def test_GIVEN_goto_example_THEN_it_compiles_and_runs_without_error(self):
        filename = "goto.spl"
        class_name = class_name_from_filename(filename)

        compile_spl(filename, class_name)

        output = remove_junk_line(run_java(class_name))

        self.assertEqual("1" + os.linesep, output)

    def test_GIVEN_conditional_goto_example_THEN_it_compiles_and_runs_without_error(self):
        filename = "condgoto.spl"
        class_name = class_name_from_filename(filename)

        compile_spl(filename, class_name)

        output = remove_junk_line(run_java(class_name, 15))

        expected_output = os.linesep.join(str(n) for n in range(1, 16)) + os.linesep

        self.assertEqual(expected_output, output)

    def test_GIVEN_prime_test_example_THEN_it_compiles_and_runs_without_error(self):
        filename = "prime.spl"
        class_name = class_name_from_filename(filename)

        compile_spl(filename, class_name)

        def is_prime(n):
            for divisor in range(2, int(sqrt(n)) + 1):
                if n % divisor == 0:
                    return False
            return True

        for n in range(2, 100):
            output = remove_cr_and_lf(remove_junk_line(run_java(class_name, n)))

            expected_output = "-1" if is_prime(n) else "1"

            self.assertEqual(expected_output, output,
                             "failed on n={}, spl says {}, python says {}".format(n, output, is_prime(n)))


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
