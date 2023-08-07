#!/usr/bin/python3

# JUnitXML to todo.txt Parser
# Ace Z. Alba (acezalba+github@slmail.me)
#

import os
import xml.etree.ElementTree as ET

def parse_junitxml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    test_results = []

    junitxml_errors = [
        "AssertionError",
        "NullPointerException",
        "TimeoutException",
        "IllegalArgumentException",
        "Exception",
        "IndexError",
        "KeyError",
        "TypeError",
        "ValueError"
    ]

    total_tests = len(root.findall('.//testcase'))
    successful_tests = total_tests  # Initialize successful_tests to the total number of tests
    failures_count = 0
    errors_count = 0

    for testcase in root.findall('.//testcase'):
        test_name = testcase.get('name')
        classname = testcase.get('classname', '')
        time = testcase.get('time', '')

        failure = testcase.find('failure')
        error = testcase.find('error')

        if failure is not None:
            failures_count += 1
            successful_tests -= 1  # Decrement successful_tests on failure
            failure_message = failure.get('message', '')

            for error_type in junitxml_errors:
                if error_type in failure_message:
                    test_results.append(
                        f"{classname} {test_name} time:{time} @failure @{error_type} message:\"{failure_message}\""
                    )
                    break
            else:
                test_results.append(f"{classname} {test_name} time:{time} @failure message:\"{failure_message}\"")
        elif error is not None:
            errors_count += 1
            successful_tests -= 1  # Decrement successful_tests on error
            error_message = error.get('message', '')

            for error_type in junitxml_errors:
                if error_type in error_message:
                    test_results.append(
                        f"{classname} {test_name} time:{time} @error @{error_type} message:\"{error_message}\""
                    )
                    break
            else:
                test_results.append(f"{classname} {test_name} time:{time} @error message:\"{error_message}\"")
        else:
            test_results.append(f"x {classname} {test_name} time:{time}")

    print("Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Successful Tests: {successful_tests}")
    print(f"Failures: {failures_count}")
    print(f"Errors: {errors_count}")

    return test_results

def save_to_todo_file(todo_file, test_results):
    with open(todo_file, 'w') as file:
        file.write('\n'.join(test_results))

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    junitxml_file = os.path.join(script_dir, os.pardir, "test-results.xml")
    todo_file = os.path.join(script_dir, os.pardir, "test-results.todo.txt")

    test_results = parse_junitxml(junitxml_file)
    save_to_todo_file(todo_file, test_results)
    print(f"Conversion complete. Results saved to test-results.todo.txt")
