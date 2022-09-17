import re
from pathlib import Path
from typing import TextIO, Iterable, NamedTuple, Iterator, Union, List
from functools import singledispatch

PageNumber = Union[int, None]


class Header(NamedTuple):
    entry: str | None
    text: str
    

class Page(NamedTuple):
    number: PageNumber
    header: Header
    content: List[str]


class SectionPage(NamedTuple):
    number: PageNumber
    title: str


class BlankPage(NamedTuple):
    number: PageNumber


PageTypes =  Union[BlankPage, SectionPage, Page]


def update_page_number(page: PageTypes, number):
    if isinstance(page, SectionPage):
        return SectionPage(number, page.title)
    if isinstance(page, BlankPage):
        return BlankPage(number)
    else:
        content = []
        for i, line in enumerate(page.content):
            try:
                num = int(line)
                if (num == number and i > 0) and (not page.content[i-1] and not page.content[i+1]):
                        content.pop()
                else:
                    content.append(line)
            except ValueError:
                content.append(line)
        return Page(number, page.header, content)


def eat_blanks(page_iter):
    while not (line := next(page_iter)):
        pass
    return line


def parse_page(page: Iterable[str]):
    lines = iter(page)
    line = eat_blanks(lines)
    if re.match(r"^\d", line):
        line_parts = line.split(maxsplit=1)
        if len(line_parts) <= 1:
            entry = line
            text = eat_blanks(lines)
        else:
            entry, text = line_parts
        header = Header(entry, text)
    else:
        header = Header(None, line)

    backwards = reversed(list(lines))
    line = eat_blanks(backwards)
    middle = list(reversed(list(backwards)))
    try:
        number = int(line)
        while middle[0] == '':
            middle = middle[1:]
        while middle[-1] == '':
            middle.pop()
        return Page(number, header, middle)
    except ValueError:
        middle.append(line)
        while middle[0] == '':
            middle = middle[1:]
        while middle[-1] == '':
            middle.pop()
        return Page(None, header, middle)


def classify_page(page: Iterable[str]) -> PageTypes:
    lines = [line for line in page if line]
    if not lines:
        return BlankPage(None)
    elif len(lines) == 1:
        return SectionPage(None, lines[0])
    else:
        return parse_page(page)


class PaginationError(Exception):
    pass


def normalize_page_numbers(pages: Iterable[PageTypes]):
    pages = list(pages)
    for i, page in enumerate(pages):
        if page.number:
            first_number = page.number
            break
    tracker = first_number - i
    for page in pages:
        if page.number:
            if page.number == tracker:
                yield page
            else:
                yield update_page_number(page, tracker)
        else:
            yield update_page_number(page, tracker)
        tracker += 1
    

def split_pages(file: TextIO):
    pages_text = file.read().split("\f")
    pages_lines = [p.splitlines() for p in pages_text]
    unnumbered = map(classify_page, pages_lines)
    return normalize_page_numbers(unnumbered)


def _serialize(data: Union[NamedTuple, object]):
    if not isinstance(data, tuple):
        return data
    dct = data._asdict()
    return {k: _serialize(v) for k, v in dct.items()}


def serialize(data: NamedTuple, ensure_ascii=False, **kwargs):
    import json
    return json.dumps(
        _serialize(data),
        ensure_ascii=ensure_ascii,
        **kwargs,
    )

def serialize_iterable(data: Iterable[NamedTuple], ensure_ascii=False, **kwargs):
    import json
    return json.dumps(
        [_serialize(el) for el in data],
        ensure_ascii=ensure_ascii,
        **kwargs,
    )


def all_page_content(pages: Iterable[PageTypes]):
    pages: List[pages_.Page] =  [p for p in pages if isinstance(p, pages_.Page)]
    return [(p.number, p.header.text, l) for p in pages for l in p.content]


def main():
    import sys
    input_file = sys.argv[1]

    with open(input_file) as fh:
        pages = split_pages(fh)
        
    print(serialize_iterable(pages, indent=1))

if __name__ == "__main__":
    main()
