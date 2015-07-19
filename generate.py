#!/usr/bin/env python3

import os
import subprocess
import sys


def find_files_by_type(path, extension):
    if not extension.startswith('.'):
        extension = '.' + extension

    matches = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                matches.append(os.path.join(root, file))

    return matches


def generate():
    for f in find_files_by_type('.', '.ui'):
        print('Processing: ' + f)

        file_split = os.path.splitext(os.path.basename(f))

        if file_split[1] != '.ui':
            print(os.path.basename(__file__) +
                  ': Invalid extension for UI file: ' +
                  file_split[1],
                  file=sys.stderr)
        else:
            generated_directory = os.path.join(os.path.dirname(f), 'generated')
            try:
                os.mkdir(generated_directory)
            except FileExistsError:
                if os.path.isdir(generated_directory):
                    pass
                else:
                    raise

            output = os.path.join(generated_directory, file_split[0] + '_ui.py')

            subprocess.call(['pyuic5', f, '-o', output])

    return 0


if __name__ == '__main__':
    sys.exit(generate())
