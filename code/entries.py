import pages 
from typing import NamedTuple


class Paragraph(NamedTuple):
    number: int
    text: str


class HoldingLocation(NamedTuple):
    name: str


class Institution(NamedTuple):
    name: str


class Entry(NamedTuple):
    number: int
    abbreviations: str | None
    paragraphs: list[Paragraph]
    institution: Institution
    location: HoldingLocation
