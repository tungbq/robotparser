import sys
import getopt
import json
import datetime
import re
import time
import xmltodict
from collections import OrderedDict

ALL_TEST_SUITES = []

def logger(message, level="INFO"):
    print(f"[{level}] {message}")

def generate_test_detail(test):
    test_detail = OrderedDict()

    test_detail['name'] = test['@name']
    test_detail['tag'] = test.get('tags', {}).get('tag', test.get('tag', ''))
    test_detail['status'] = test['status']['@status']

    start_time_key = '@starttime' if '@starttime' in test['status'] else '@start'
    test_detail['start_time'] = test['status'][start_time_key]

    if '@starttime' in test['status']:
        test_detail['end_time'] = test['status']['@endtime']
        test_detail['elapsed_time'] = calculate_elapsed_time(
            test['status']['@starttime'], test['status']['@endtime']
        )
    else:
        test_detail['elapsed_time'] = test['status']['@elapsed']

    test_detail['message'] = test['status'].get('#text', '')
    return test_detail

def parse_tests(tests):
    return [generate_test_detail(test) for test in tests] if isinstance(tests, list) else [generate_test_detail(tests)]

def collect_test_cases(suites):
    test_data = {'details': [detail for suite in suites for detail in parse_tests(suite['test'])]}
    return test_data

def calculate_elapsed_time(start_time, end_time):
    start = time.mktime(datetime.datetime.strptime(start_time, "%Y%m%d %H:%M:%S.%f").timetuple())
    end = time.mktime(datetime.datetime.strptime(end_time, "%Y%m%d %H:%M:%S.%f").timetuple())
    formatted_elapsed_time = time.strftime('%H:%M:%S', time.gmtime(end - start))
    return formatted_elapsed_time

def find_total_stat(all_tests_stat):
    logger("Finding total stats...")

    # Return if this is single dict
    if isinstance(all_tests_stat, dict):
        return all_tests_stat

    total_stat = next((stat for stat in all_tests_stat if isinstance(stat, dict) and stat.get('#text') == 'All Tests'), None)
    return total_stat

def collect_all_test_suites(suite):
    if 'test' in suite:
        ALL_TEST_SUITES.append(suite)
        return
    elif isinstance(suite, list):
        for sub_suite in suite:
            collect_all_test_suites(sub_suite)
    else:
        collect_all_test_suites(suite['suite'])

def get_total_stat(total_stat):

    if total_stat:
        total_pass = int(total_stat.get('@pass', 0))
        total_fail = int(total_stat.get('@fail', 0))
        total_skip = int(total_stat.get('@skip', 0))
    else:
        total_pass = total_fail = total_skip = 0

    return total_pass, total_fail, total_skip

def read_and_parse_xml(xml_file_path):
    with open(xml_file_path, "r") as xml_file:
        xml_input = xml_file.read().replace('\n', '')
        all_data = xmltodict.parse(xml_input)['robot']
        collect_all_test_suites(all_data['suite'])
        test_cases = collect_test_cases(ALL_TEST_SUITES)
        output_data = OrderedDict()

        total_stat = find_total_stat(all_data['statistics']['total']['stat'])
        total_pass, total_fail, total_skip = get_total_stat(total_stat)

        output_data.update(total=total_pass + total_fail + total_skip, pass_=total_pass, fail=total_fail, skip=total_skip)
        output_data['elapsed_time'] = 'N/A' if all_data['suite']['status']['@starttime'] == 'N/A' or all_data['suite']['status']['@endtime'] == 'N/A' else calculate_elapsed_time(
            all_data['suite']['status']['@starttime'], all_data['suite']['status']['@endtime']
        )
        output_data['test_case_stats'] = test_cases['details']

    return output_data

def write_json_to_file(data, json_file_path):
    with open(json_file_path, "w+") as json_file:
        json.dump(data, json_file, indent=4)


def usage():
    print("""Usage: python parse-robot-output.py -i <input-xml-file> -o <output-json-file>
Options:
  -i, --input-file    Specify the input XML file generated by robot test (e.g., robot-result/output.xml)
  -o, --output-file   Specify the output JSON file (e.g., output/output.json)
  -h, --help          Display this help message

Example:
  python parse-robot-output.py -i robot-result/output.xml -o output/output.json

Note:
  Make sure to provide valid file paths.
""")
    sys.exit(2)

def check_input_parameters(argv):
    input_file, output_file = '', ''

    try:
        opts, args = getopt.getopt(argv, 'i:o:h:', ['input-file=', 'output-file=', 'help'])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ("-i", "--input-file"):
            input_file = arg
        elif opt in ("-o", "--output-file"):
            output_file = arg
        else:
            usage()

    if not input_file:
        print('Missing input file, please check!')
        usage()

    if not output_file:
        print('Missing output file, please check!')
        usage()

    print('Input file is: ', input_file)
    print('Output file is: ', output_file)

    return input_file, output_file

def main(argv):
    print('Checking input parameters ...')
    input_file, output_file = check_input_parameters(argv)

    print('Parsing xml file ...')
    data = read_and_parse_xml(input_file)

    print(f'Saving json data to output file: {output_file} ...')
    write_json_to_file(data, output_file)


if __name__ == "__main__":
    main(sys.argv[1:])

