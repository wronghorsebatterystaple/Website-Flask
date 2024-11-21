from markdown.extensions import Extension

from app.markdown_extensions.dropdown import Dropdown
from app.markdown_extensions.textbox import Textbox


class AmsthmExtension(Extension):
    def extendMarkdown(self, md):
        # TODO: these need to be passed in via extension config
        # same with dropdown, textbox etc
        dropdown_types = {
            "exer": {"name": "Exercise", "counter": "0,0,1"},
            "pf": {"name": "Proof", "counter": None},
            "rmk": {"name": "Remark", "counter": None}
        }
        textbox_types = {
            "coro": {"name": "Corollary", "counter": "0,0,1"},
            "defn": {"name": "Definition", "counter": "0,0,1"},
            "notat": {"name": "Notation", "counter": None},
            "prop": {"name": "Proposition", "counter": "0,0,1"},
            "thm": {"name": "Theorem", "counter": "0,0,1"}
        }
        md.parser.blockprocessors.register(
                Dropdown(md.parser, types=dropdown_types, html_class="md-dropdown",
                        summary_html_class="md-dropdown__summary last-child-no-mb",
                        content_html_class="md-dropdown__content last-child-no-mb",
                        math_counter=True, math_thm_heading=True),
                "amsthm_dropdown", 105)
        #md.parser.blockprocessors.register(
        #        Textbox(md.parser, types=textbox_types, math_counter=True, math_thm_heading=True),
        #        "amsthm_textbox", 105)
        # TODO: counter needed too with configs on generate html etc?


def makeExtension(**kwargs):
    return AmsthmExtension(**kwargs)
