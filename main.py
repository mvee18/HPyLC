import os
import argparse as ap
from os.path import abspath
from typing import List, Tuple


def parse_args() -> ap.Namespace:
    # Need an input and output directory arguments.
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='Input directory')
    parser.add_argument('-o', '--output', required=True,
                        help='Output directory')
    args = parser.parse_args()
    return args


def check_dir(dir_path) -> None:
    if not os.path.exists(dir_path):
        raise Exception(f'Directory {dir_path} does not exist.')


def clean_table(table: List[str]) -> List[List[str]]:
    # Since the same number of lines come before the data (i.e., the header, units, and separator lines),
    # We can just remove these (lines 27,28,29 in the example file.)
    table = table[5:]

    # Remove the last objects in the list, which is a blank line and the total.
    table = table[:-3]

    for i in range(len(table)):
        table[i] = table[i].split()

    return table


def parse_file(file_path) -> Tuple[str, List[str]]:
    """ Parses a HPLC file and returns the sample name and the Signal 1 data as a list of strings."""
    print(f'Parsing {file_path}')
    data = []
    with open(file_path, "r", encoding="utf-16") as f:
        sample_name = None
        found = False
        for line in f:
            if line.startswith("Sample Name"):
                sample_name = line.split(":")[1].strip()

            if line.startswith("Signal 1"):
                found = True

            if line.startswith("Signal 2"):
                found = False

            if found:
                data.append(line.strip())

    cleaned_data = clean_table(data)

    return sample_name, cleaned_data


def write_data(data: List[List[str]], output_file: str, sample_name: str, header: bool) -> None:
    with open(output_file, 'a+') as f:
        if header:
            f.write("Sample,RetTime,Area\n")
        for line in data:
            RT = line[1]
            area = line[4]
            p_line = ','.join([sample_name, RT, area])

            print(p_line, file=f)


def main():
    args = parse_args()
    input_dir = abspath(args.input)
    output_dir = abspath(args.output)
    output_file = os.path.join(output_dir, 'output.csv')

    # Check that the input and output directories exist.
    check_dir(input_dir)
    check_dir(output_dir)

    txt_files = []
    # Now, we list the .txt files in the input directory and walk down.
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file == "Report.TXT":
                txt_files.append(os.path.join(root, file))

    # Now, open each file.
    for c, t in enumerate(txt_files):
        if c == 0:
            name, data = parse_file(t)
            write_data(data, output_file, name, True)
        else:
            name, data = parse_file(t)
            write_data(data, output_file, name, False)


if __name__ == "__main__":
    main()
