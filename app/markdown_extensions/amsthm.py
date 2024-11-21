import re
import xml.etree.ElementTree as etree
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor


class TheoremHeading(InlineProcessor):
    """
    A theorem heading that allows you to add custom styling and can generate linkable HTML `id`s.

    Usage:
        ```
        {[<theorem heading>]}{<optional theorem name>}[<optional hidden theorem name>]
        ```
        - HTML output:
            ```
            <span id="[optional theorem name/optional hidden theorem name]" class="md-theorem-heading">
              [theorem heading]
            </span>
            [optional theorem name]
            ```
        - `<optional hidden theorem name>` only adds an HTML `id`, and is not displayed. It is ignored if
          `<optional theorem name>` is provided.
    """

    def handleMatch(self, m, current_text_block):
        def format_for_html(s: str) -> str:
            s = ("-".join(s.split())).lower() 
            s = s[:-1].replace(".", "-") + s[-1] # replace periods except if trailing with hyphens (for thm counter)
            s = re.sub(r"[^A-Za-z0-9-]", r"", s)
            return s

        elem = etree.Element("span")
        elem.text = m.group(1)
        if m.group(2):
            elem.text += f" ({m.group(2)})"
            elem.set("id", format_for_html(m.group(2)))
        elif m.group(3):
            elem.set("id", format_for_html(m.group(3)))
        elem.set("class", "md-theorem-heading")
        return elem, m.start(0), m.end(0)


class Amsthm(BlockProcessor):
    def __init__(self, thms, html_class=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thms = thms
        # temp
        self.thms = {
            # html class: {name to use in regex (begin is auto): option (div/dropdown, optional, default div)}
        }
        if html_class_prefix is not None:
            self.html_class_prefix = html_class_prefix


class AmsthmExtension(Extension):
    def extendMarkdown(self, md):
        regex = r"{\[(.+?)\]}(?:{(.+?)})?(?:\[(.+?)\])?"
        md.inlinePatterns.register(TheoremHeading(regex, md), "theorem_heading", 105)
        # md.parser.blockprocessors.register(Amsthm(md.parser), "amsthm", 105)


def makeExtension(**kwargs):
    return AmsthmExtension(**kwargs)
