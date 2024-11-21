import re
import xml.etree.ElementTree as etree
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor


class ThmHeading(InlineProcessor):
    """
    A theorem heading that allows you to add custom styling and can generate linkable HTML `id`s.

    Usage:
        ```
        {[<theorem heading>]}[<optional theorem name>][[<optional hidden theorem name>]]
        ```
        - HTML output:
            ```
            <span id="[optional theorem name/optional hidden theorem name]" class="md-thm-heading">
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
        elem.set("class", "md-thm-heading")
        return elem, m.start(0), m.end(0)


class ThmHeadingExtension(Extension):
    def extendMarkdown(self, md):
        regex = r"{\[(.+?)\]}(?:\[(.+?)\])?(?:\[\[(.+?)\]\])?"
        md.inlinePatterns.register(ThmHeading(regex, md), "thm_heading", 105)


def makeExtension(**kwargs):
    return ThmHeadingExtension(**kwargs)
