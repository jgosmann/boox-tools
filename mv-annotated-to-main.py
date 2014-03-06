#!/usr/bin/env python

import argparse
import os
import os.path
import re


REGEX = re.compile(r'^(.*)_\d{4}-\d{1,2}-\d{1,2}_\d{1,2}-\d{1,2}-\d{1,2}.pdf$')

def process(filename):
    match = REGEX.match(filename)
    if match is not None:
        new_filename = match.group(1) + '.pdf'
        os.rename(filename, new_filename)
        print '{} -> {}'.format(filename, new_filename)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Removes the date suffix from the PDF files with '
        'merged annotations from the Onyx Boox M92 ebook reader.')
    PARSER.add_argument(
        '-r', help='Descend recursively into directories.',
        action='store_true', default=False)
    PARSER.add_argument('filenames', nargs='*', help='Files to process.')
    ARGS = PARSER.parse_args()

    for name in ARGS.filenames:
        if os.path.isdir(name):
            for dirpath, dirnames, sub_filenames in os.walk(name):
                for sub_filename in sub_filenames:
                    process(os.path.join(dirpath, sub_filenames))
        else:
            process(name)
