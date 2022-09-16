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


def update_page_number(page, number):
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

def extract_content(pages: Iterable[PageTypes]) -> Iterator[str]:
    for page in pages:
        if isinstance(page, Page):
            yield from page.content
