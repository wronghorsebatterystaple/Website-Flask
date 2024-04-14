from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as etree


class HeaderFormatTreeProcessor(Treeprocessor):
    def run(self, root) -> None:
        for child in root:
            if child.tag == "h1" and child.get("class", "") == "":
                child.set("class", "post-h1")
            elif child.tag == "h2" and child.get("class", "") == "":
                child.set("class", "post-h2")
            self.run(child)


# custom Markdown \lf{}\elf to give stuff inside LaTeX font
class LatexFontInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        elem = etree.Element("span")
        elem.text = m.group(1)
        elem.set("class", "font-latex")
        return elem, m.start(0), m.end(0)


class MyExtensions(Extension):
    def extendMarkdown(self, md):
        LF_RE_FROM = r"\\lf{([\S\s]*?)}\\elf"
        md.treeprocessors.register(HeaderFormatTreeProcessor(md), "headerformat", 105)
        md.inlinePatterns.register(LatexFontInlineProcessor(LF_RE_FROM, md), "latexfont", 105)
