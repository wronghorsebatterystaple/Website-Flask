from markdown.extensions import Extension

from app.markdown_extensions.dropdown import Dropdown
from app.markdown_extensions.textbox import Textbox


class AmsthmExtension(Extension):
    def extendMarkdown(self, md):
        # TODO: these need to be passed in via extension config
        # same with dropdown, textbox etc
        dropdown_types = {
            "exer": {"name": "Exercise", "counter": "0,0,1", "html_class": "md-dropdown--exer"},
            "pf"  : {"name": "Proof", "html_class": "md-dropdown--pf"},
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
