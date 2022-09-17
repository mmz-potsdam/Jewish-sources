Parsers produced for the Jewish DH hackathon at the University of
Potsdam, September 2022.

This will eventually be a proper Python package to install with `pip`,
but for now be aware that the .py files depend on each other and must
be placed in the same directory.

## pages module

The `pages` module contains functions for normalizing the text of the
pdfs to extract their content.

Some examples:

```python
import pages

# the input file should _not_ be from the frontmatter
with open("/path/to/text_of_pdf_file_from_catalog.pdf.txt") as file:
    parsed_pages = pages.split_pages(file)
    
# parsed_pages is a list of pages as structured data (in named
# tuples). These objects contain the page number, the header, as well
# as the page content as a list of lines with (with the number and
# header removed.

# serialize one page as a JSON object
a_json_object: str = pages.serialize(parsed_pages[0])


# serialize all pages to a JSON array
a_JSON_array_of_page_objects = pages.serialize_iterable(parsed_pages)

# convert pages to a list of lines (lines also have data about the
# page they are from)
lines = pages.all_page_content(parsed_pages)

print(lines[3])
# (3, "Bundesarchiv, Abteilungen Potsdam", "Telefon:")
# that is (page number, page heading text, line text)
```

The pages module can also be used as a script at the command line:

```bash
$ python3 pages.py /path/to/text_of_pdf_file_from_catalog.pdf.txt
```

The input file here should _not_ be from the frontmatter. The output
will be a JSON array of lines as output the `all_page_content`
function.

## entries module

The entries module is the beginning of a parser to extract entries
from text of the collection. It is not yet complete!
