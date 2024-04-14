from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as etree


class HeaderFormatTreeProcessor(Treeprocessor):
    def run(self, root) -> None:
        def iterate(parent):
            for child in parent:
                if child.tag == "h1" and child.get("class", "") == "":
                    child.set("class", "post-h1")
                elif child.tag == "h2" and child.get("class", "") == "":
                    child.set("class", "post-h2")
                iterate(child)
        iterate(root)


class MyExtensions(Extension):
    def extendMarkdown(self, md):
        # Some things like footnotes aren't expanded and accessible from Treeprocessor,
        # so it's probably better to offload that processing to client-side JS
        md.treeprocessors.register(HeaderFormatTreeProcessor(md.parser), "headerformat", 105)
