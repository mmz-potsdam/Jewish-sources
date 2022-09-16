import re
from pathlib import Path
from typing import TextIO, Iterable, NamedTuple, Iterator


class SectionPage(NamedTuple):
    number: int | None
    title: str


class BlankPage(NamedTuple):
    number: int | None


class Header(NamedTuple):
    entry: str | None
    text: str
    
class Page(NamedTuple):
    number: int | None
    header: Header
    content: list[str]


PageTypes =  BlankPage | SectionPage | Page


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
    match [line for line in page if line]:
        case []:
            return BlankPage(None)
        case [section_name]:
            return SectionPage(None, section_name)
        case stripped_page:
            return parse_page(page)
    

def split_pages(file: TextIO):
    pages_text = file.read().split("\f")
    pages_lines = [p.splitlines() for p in pages_text]
    return map(classify_page, pages_lines)

def extract_content(pages: Iterable[PageTypes]) -> Iterator[str]:
    for page in pages:
        if isinstance(page, Page):
            yield from page.content
