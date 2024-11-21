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

    # TODO: if publishing these extensions, let these dicts be defined as kwargs in extension config
    RE_START_CHOICES = {
        "default": r"\\begin{textbox}$",
        "coro": r"\\begin{coro}$",
        "defn": r"\\begin{defn}$",
        "impt": r"\\begin{impt}$",
        "notat": r"\\begin{notat}$",
        "prop": r"\\begin{prop}$",
        "thm": r"\\begin{thm}$"
    }
    RE_END_CHOICES = {
        "default": r"\\end{textbox}$",
        "coro": r"\\end{coro}$",
        "defn": r"\\end{defn}$",
        "impt": r"\\end{impt}$",
        "notat": r"\\end{notat}$",
        "prop": r"\\end{prop}$",
        "thm": r"\\end{thm}$"
    }
    RE_START = None
    RE_END = None
    TYPE = None
    
    def test(self, parent, block):
        for type, regex in self.RE_START_CHOICES.items():
            if re.match(regex, block):
                self.TYPE = type
                self.RE_START = regex
                self.RE_END = self.RE_END_CHOICES[type]
                return True
        return False

    def run(self, parent, blocks):
        if not self.RE_START or not self.RE_END or not self.TYPE:
            return False

        # remove starting delimiter
        org_block_start = blocks[0] # use simpler restoring system for non-nested BlockProcessors
        blocks[0] = re.sub(self.RE_START, "", blocks[0])

        # find and remove ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.RE_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_END, "", block)
                # build HTML
                elem = etree.SubElement(parent, "div")
                elem.set("class", f"md-textbox md-textbox--{self.TYPE} last-child-no-mb")
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
        md.parser.blockprocessors.register(Textbox(md.parser), "textbox", 105)


def makeExtension(**kwargs):
    return TextboxExtension(**kwargs)
