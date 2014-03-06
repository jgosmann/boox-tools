#!/usr/bin/env python

import re

# PDF format reference: http://wwwimages.adobe.com/www.adobe.com/content/dam/Adobe/en/devnet/pdf/pdfs/PDF32000_2008.pdf
# pages 12 to 13 define the character sets
WHITESPACE = '\x00\x09\x0A\x0C\x0D\x20'
DELIMITER = '()<>[]{}/%'

def to_re_char_group(charset):
    return '[{}]'.format(re.escape(charset))

RE_CHAR_GROUPS = {
    'delimiter': to_re_char_group(DELIMITER),
    'float': r'(?:\+|\-)?\d*\.\d*',
    'special': to_re_char_group(WHITESPACE + DELIMITER),
    'ws' : to_re_char_group(WHITESPACE)
}

def create_pdf_regex(pattern):
    return re.compile(pattern.format(**RE_CHAR_GROUPS))

OBJ_RE = create_pdf_regex(
    '(?<={special})obj{ws}*<<.*>>{ws}*endobj(?={special})')
ANNOT_RE = create_pdf_regex('/Type{ws}*/Annot(?={special})')
HIGHLIGHT_RE = create_pdf_regex('/Subtype{ws}*/Highlight(?={special})')
COLOR_RE = create_pdf_regex(
    r'/C{ws}*\[{ws}*({float}){ws}+({float}){ws}+({float}){ws}*\]')


def process_color(match, replacement):
    prefix = '/C['
    suffix = ']'
    diff = len(match.group(0)) - len(replacement) - len(prefix) - len(suffix)
    if diff < 0:
        raise NotImplementedError(
            'Replacement is too long and would require the size of the PDF '
            'file to change. This is not implemented.')
    return prefix + diff * ' ' + replacement + suffix

def process_obj(match, color_string):
    is_annot = ANNOT_RE.search(match.group(0))
    is_highlight = HIGHLIGHT_RE.search(match.group(0))
    if is_annot and is_highlight:
        return COLOR_RE.sub(
            lambda match: process_color(match, color_string), match.group(0))
    else:
        return match.group(0)

def process_file(filename, color_string):
    with open(filename, 'rb') as f:
        data = f.read()
    data = OBJ_RE.sub(lambda match: process_obj(match, color_string), data)
    with open(filename, 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    import argparse
    import sys
    PARSER = argparse.ArgumentParser(
        description='Change the color of all highlights in a PDF.')
    PARSER.add_argument(
        'color', nargs=1, type=str,
        help='Color to apply to the highlights. Has to be a string of 0 to 4 '
        '(but not 2) float values. The number of values defines the color '
        'space: 0 = transparent, 1 = gray scale, 3 = RGB, 4 = CMYK. '
        'This argument is not validated!')
    PARSER.add_argument(
        'filename', nargs='*', type=str, help='PDF file to process.')
    ARGS = PARSER.parse_args()

    for filename in ARGS.filename:
        try:
            process_file(filename, ARGS.color[0])
        except RuntimeError as err:
            sys.stderr.write('{}: {}\n'.format(filename, err))
