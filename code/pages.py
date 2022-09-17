import re
from pathlib import Path
from typing import (
    TextIO,
    Iterable,
    NamedTuple,
    Iterator,
    Union,
    List,
    Optional,
    Callable
)
from functools import singledispatch, partial


class Header(NamedTuple):
    """type for the info at the info at the top of the page

    - entry: many pages have the name of the last entry listed in the
      top of the page.
    - text: the text that's on the page, usually denoting the section of
      the book

    """
    entry: Optional[str]
    text: str
    

class Page(NamedTuple):
    """type for the content of a regular page"""
    number: int
    header: Header
    content: List[str]


class SectionPage(NamedTuple):
    """type a page that only contains a section header"""
    number: int
    title: str


class BlankPage(NamedTuple):
    """type for a blank page"""
    number: int


PageTypes =  Union[BlankPage, SectionPage, Page]
PendingPage = Callable[[int], PageTypes]


def update_page_number(page: PageTypes, number):
    """create a new page with an updated number"""
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


def eat_blanks(page_iter: Iterator[str]):
    """remove blanks from an iterator of a page"""
    while not (line := next(page_iter)):
        pass
    return line


def trim_content(mut_content):
    content = mut_content
    while content[0] == '':
        content = content[1:]
    while content[-1] == '':
        content.pop()
    return content
    


def parse_page(page: Iterable[str]):
    """take a list of lines that is not a section page or a blank page
    and construct a normal Page type.

    """
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
        content = trim_content(middle)
        return Page(number, header, content)
    except ValueError:
        middle.append(line)
        content = trim_content(middle)
        return partial(Page, header=header, content=content)


def classify_page(page: Iterable[str]) -> Union[Page, PendingPage]:
    """take an iterable of lines from a page"""
    lines = [line for line in page if line]
    if not lines:
        return BlankPage
    elif len(lines) == 1:
        return partial(SectionPage, title=lines[0])
    else:
        return parse_page(page)


def normalize_page_numbers(pages: Iterable[Union[Page, PendingPage]]):
    """take an iterable of pages, some of which may not have numbers and
    add numbers. Also correct page numbers which were added incorrectly

    """
    pages = list(pages)
    for i, page in enumerate(pages):
        if isinstance(page, Page):
            first_number = page.number
            break
    tracker = first_number - i
    for page in pages:
        if isinstance(page, Page):
            if page.number == tracker:
                yield page
            else:
                yield update_page_number(page, tracker)
        else:
            yield update_page_number(page(tracker), tracker)
        tracker += 1
    

def split_pages(file: TextIO):
    """take an opened PDF file from the collection as input (after the
    frontmatter) and return an iterator of PageTypes.

    """
    pages_text = file.read().split("\f")
    pages_lines = [p.splitlines() for p in pages_text]
    unnumbered = map(classify_page, pages_lines)
    return normalize_page_numbers(unnumbered)


def _serialize(data: Union[NamedTuple, object]):
    """take a named tuple composed of JSON compatible types and return a
    JSON-compatible object.

    """
    if not isinstance(data, tuple):
        return data
    dct = data._asdict()
    return {k: _serialize(v) for k, v in dct.items()}


def serialize(data: NamedTuple, ensure_ascii=False, **kwargs):
    """take a named tuple composed of JSON compatible types and return a
    JSON object.

    """
    import json
    return json.dumps(
        _serialize(data),
        ensure_ascii=ensure_ascii,
        **kwargs,
    )

def serialize_iterable(data: Iterable[NamedTuple], ensure_ascii=False, **kwargs):
    """take an iterable of named tuples composed of JSON compatible types
    and return a JSON array.

    """
    import json
    return json.dumps(
        [_serialize(el) for el in data],
        ensure_ascii=ensure_ascii,
        **kwargs,
    )


def all_page_content(pages: Iterable[PageTypes]):
    """convert an iterable of PageTypes to a list where each item is
    3-tuple of (page number, page header text, single line of text)

    """
    pages =  (p for p in pages if isinstance(p, Page))
    return [(p.number, p.header.text, l) for p in pages for l in p.content]


def main():
    """take a pdf filename from the collection (after the frontmatter)
    and print a JSON array of lines with their page numbers, header text,
    line text.

    """
    import sys
    import json
    input_file = sys.argv[1]

    with open(input_file) as fh:
        pages = split_pages(fh)

    print("[", end="")
    print("\n,".join(
        json.dumps(l, ensure_ascii=False) for l in all_page_content(pages))
    )
    print("]")


if __name__ == "__main__":
    main()
