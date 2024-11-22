import re
import xml.etree.ElementTree as etree
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor


class Textbox(BlockProcessor):
    """
    A textbox.

    Usage:
        ```

        \begin{<type>}
        
        <content>

        \end{<type>}

        ```
        - HTML output:
            ```
            <div class="md-textbox md-textbox--[type] last-child-no-mb">
              [content]
            </div>
            ```
    """

    def __init__(self, *args, types: dict, html_class: str="", use_math_counter: bool=False,
            use_math_thm_heading: bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.types = types
        self.html_class = html_class
        self.use_math_counter = use_math_counter
        self.use_math_thm_heading = use_math_thm_heading
        self.re_start = None
        self.re_end = None
        self.typ = None

        # init regex patterns
        self.re_start_choices = {}
        self.re_end_choices = {}
        for typ in self.types:
            if self.use_math_thm_heading:
                self.re_start_choices[typ] = rf"\\begin{{{typ}}}(?:\[(.+?)\])?(?:{{(.+?)}})?$"
            else:
                self.re_start_choices[typ] = rf"\\begin{{{typ}}}$"
            self.re_end_choices[typ] = rf"\\end{{{typ}}}$"

    def test(self, parent, block):
        for typ, regex in self.re_start_choices.items():
            if re.match(regex, block):
                self.typ = self.types[typ]
                self.re_start = regex
                self.re_end = self.re_end_choices[typ]
                return True
        return False

    def run(self, parent, blocks):
        if self.re_start is None or self.re_end is None or self.typ is None:
            return False

        org_block_start = blocks[0]
        # fill in math theorem heading if applicable
        # TODO: does this need to be at the end?
        elem = etree.SubElement(parent, "div")
        elem.set("class", f"{self.html_class} {self.typ.get('html_class', '')}")
        default_prefix = self.typ.get("name")
        if default_prefix is not None:
            elem.text = default_prefix
            # TODO: util function for this somehow that is shared with dropdown?
            # fill in math counter by using my `counter` extension's syntax
            if self.use_math_counter:
                counter = self.type.get("counter")
                if counter is not None:
                    elem.text += f" {{{{{counter}}}}}"
            # fill in math theorem heading by using my `thm_heading` extension's syntax
            if self.use_math_thm_heading:
                re_start_match = re.search(self.re_start, blocks[0])
                overrides_heading = self.typ.get("overrides_heading")
                # override heading with theorem if applicable
                if overrides_heading and re_start_match.group(1) is not None:
                    elem_summary.text = re_start_match.group(1)

                elem_summary.text = "{[" + elem_summary.text + "]}"
                if not overrides_heading and re_start_match.group(1) is not None:
                    elem_summary.text += "[" + re_start_match.group(1) + "]"
                if re_start_match.group(2) is not None:
                    elem_summary.text += "{" + re_start_match.group(2) + "}"

        # remove starting delimiter (after extracting theorem headings if applicable)
        blocks[0] = re.sub(self.re_start, "", blocks[0])

        # find and remove ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.RE_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_END, "", block)
                # build HTML
                self.parser.parseBlocks(elem, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter, restore and do nothing
        blocks[0] = org_block_start
        return False


class TextboxExtension(Extension):
    def extendMarkdown(self, md):
        types = {
            "textbox": {"html_class": "md-dropdown--default"}
        }
        md.parser.blockprocessors.register(
                Textbox(md.parser, types=types, html_class="md-textbox last-child-no-mb"),
                "textbox", 105)


def makeExtension(**kwargs):
    return TextboxExtension(**kwargs)
