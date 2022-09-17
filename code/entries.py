import re

import pages as pages_
from typing import NamedTuple, Iterable, cast, List, Optional, Union, Tuple


class Page(NamedTuple):
    number: int
    filename: str


class Paragraph(NamedTuple):
    number: int
    text: List[str]
    page: Page


class Institution(NamedTuple):
    name: str
    text: str
    page: Page


class HoldingLocation(NamedTuple):
    name: str
    institution: Optional[Institution]
    page: Page


class Entry(NamedTuple):
    number: int
    descriptor: Optional[str]
    paragraphs: List[Paragraph]
    location: Union[HoldingLocation, Institution, None]
    page: Page


def remove_n_lines(entry: Entry, n):
    last_pargraph = entry.paragraphs[-1]
    paragraphs = entry.paragraphs[:-1]
    new_last = Paragraph(
        last_pargraph.number, 
        last_pargraph.text[:-n],
        last_pargraph.page,
    )
    paragraphs.append(new_last)
    return Entry(
        entry.number,
        entry.descriptor,
        paragraphs,
        entry.location,
        entry.page,
    ), last_pargraph.text[-n:]


def append_paragraph(entry: Entry, collected: List[Tuple[int, str]], filename: str, next_head: str):
    last_pargraph = entry.paragraphs[-1]
    page = last_pargraph.page
    last_pargraph.text.extend((text for _, text in collected))


def get_next_entry(
        institution: Optional[Institution],
        location: Optional[HoldingLocation],
        last_entry: Optional[last_entry],
        lines: List[Tuple[int, str, str]],
        idx: int,
        filename: str
):
    collected: List[Tuple[int, str]] = []
    last_number = last_entry.number if last_entry else 0

    while idx < len(lines):
        page_number, _, line = lines[idx]
        number_match = re.match(r"^(d+)(.?)", line)
        if not number_match:
            collected.append((page_number, line))

        initial_number = int(number_match.group(1))

        if initial_number == last_number and number_match.group(2) == "/":
            append_paragraph(last_entry, collected)
            collected.clear()


def from_pages(pages: Iterable[pages_.PageTypes], filename: str):
    lines = pages_.all_page_content(pages)
    institution: Institution = None
    location: HoldingLocation = None
    entries: List[Entry] = []
    last_entry: Entry = None
    idx = 0

    while idx < len(lines):
        institution, location, entry, idx = get_next_entry(
            institution, location, last_entry, lines, idx, filename
        )
        last_entry = entry
        entries.append(entry)

    return entries

