import re
import xml.etree.ElementTree as etree
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

from app.markdown_extensions.dropdown import Dropdown
from app.markdown_extensions.textbox import Textbox


# TODO: make ending punct customizeable, also whether no-title headings are given ending punct too
class ThmHeading(InlineProcessor):
    """
    A theorem heading that allows you to add custom styling and can generate linkable HTML `id`s.

    Usage:
        ```
        {[<theorem_heading>]}[<optional_theorem_name>][[<optional_hidden_theorem_name>]]
        ```
        - HTML output:
            ```
            <span id="[optional_theorem_name/optional_hidden_theorem_name]" class="md-thm-heading">
              [theorem_heading]
            </span>
            [optional_theorem_name]
            ```
        - `<optional_hidden_theorem_name>` only adds an HTML `id`, and is not displayed. It is ignored if
          `<optional_theorem_name>` is provided.
    """

    def handleMatch(self, m, current_text_block):
        def format_for_html(s: str) -> str:
            s = ("-".join(s.split())).lower() 
            s = s[:-1].replace(".", "-") + s[-1] # replace periods except if trailing with hyphens (for thm counter)
            s = re.sub(r"[^A-Za-z0-9-]", r"", s)
            return s

        elem = etree.Element("span")
        elem_heading = etree.SubElement(elem, "span")
        elem_heading.text = f"{m.group(1)} "
        if m.group(2) is not None:
            elem_non_heading = etree.SubElement(elem, "span")
            elem_non_heading.text = f"({m.group(2)}). "
            elem.set("id", format_for_html(m.group(2)))
        elif m.group(3) is not None:
            elem.set("id", format_for_html(m.group(3)))
        elem.set("class", "md-thm-heading")
        elem_heading.set("class", "md-thm-heading--heading")
        return elem, m.start(0), m.end(0)


class AmsthmExtension(Extension):
    def extendMarkdown(self, md):
        regex = r"{\[(.+?)\]}(?:\[(.+?)\])?(?:{(.+?)})?"
        md.inlinePatterns.register(ThmHeading(regex, md), "thm_heading", 105)

        # TODO: these need to be passed in via extension config
        # same with dropdown, textbox etc
        dropdown_types = {
            "exer": {"name": "Exercise", "counter": "0,0,1", "html_class": "md-dropdown--exer"},
            "pf"  : {"name": "Proof", "html_class": "md-dropdown--pf", "overrides_heading": True},
            "rmk" : {"name": "Remark", "html_class": "md-dropdown--rmk"}
        }
        textbox_types = {
            "coro" : {"name": "Corollary", "counter": "0,0,1", "html_class": "md-textbox--coro"},
            "defn" : {"name": "Definition", "counter": "0,0,1", "html_class": "md-textbox--defn"},
            "notat": {"name": "Notation", "html_class": "md-textbox--notat"},
            "prop" : {"name": "Proposition", "counter": "0,0,1", "html_class": "md-textbox--prop"},
            "thm"  : {"name": "Theorem", "counter": "0,0,1", "html_class": "md-textbox--thm"}
        }
        md.parser.blockprocessors.register(
                Dropdown(md.parser, types=dropdown_types, html_class="md-dropdown",
                        summary_html_class="md-dropdown__summary last-child-no-mb",
                        content_html_class="md-dropdown__content last-child-no-mb",
                        math_counter=True, math_thm_heading=True),
                "amsthm_dropdown", 999)
        #md.parser.blockprocessors.register(
        #        Textbox(md.parser, types=textbox_types, html_class="md-textbox",
        #                summary_html_class="md-textbox__summary last-child-no-mb",
        #                content_html_class="md-textbox__content last-child-no-mb",
        #                math_counter=True, math_thm_heading=True),
        #        "amsthm_textbox", 105)


def makeExtension(**kwargs):
    return AmsthmExtension(**kwargs)
