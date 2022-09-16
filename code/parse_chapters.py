import re
from pathlib import Path
from typing import TextIO, Iterable, NamedTuple, Iterator, Union

PageNumber = Union[int, None]

class SectionPage(NamedTuple):
    number: PageNumber
    title: str


class BlankPage(NamedTuple):
    number: PageNumber


class Header(NamedTuple):
    entry: str | None
    text: str
    
class Page(NamedTuple):
    number: PageNumber
    header: Header
    content: list[str]


PageTypes =  Union[BlankPage, SectionPage, Page]


def eat_blanks(page_iter):
    while not (line := next(page_iter)):
        pass
    return line


def parse_page(page: list[str]):
    lines = iter(page)
    line = eat_blanks(lines)
    if re.match(r"^\d", line):
        entry = line
        text = eat_blanks(lines)
        header = Header(entry, text)
    else:
        header = Header(None, line)

    backwards = reversed(list(lines))
    line = eat_blanks(backwards)
    middle = list(reversed(list(backwards)))
    try:
        number = int(line)
        return Page(number, header, middle)
    except ValueError:
        middle.append(line)
        return Page(None, header, middle)


def classify_page(page: list[str]) -> PageTypes:
    lines = [line for line in page if line]
    if not lines:
        return BlankPage(None)
    elif len(lines) == 1:
        return SectionPage(None, section_name)
    else:
        return parse_page(page)
    

def split_pages(file: TextIO):
    pages_text = file.read().split("\f")
    pages_lines = [p.splitlines() for p in pages_text]
    return map(classify_page, pages_lines)

def extract_content(pages: Iterable[PageTypes]) -> Iterator[str]:
    for page in pages:
        if isinstance(page, Page):
            yield from page.content
