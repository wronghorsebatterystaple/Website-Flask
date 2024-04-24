from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor
from markdown.treeprocessors import Treeprocessor


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


# Some things like footnotes aren't expanded and accessible from Treeprocessor,
# so it's probably better to offload that processing to client-side JS
class MyExtensions(Extension):
    def extendMarkdown(self, md):
        # add header classes for CSS customization
        md.treeprocessors.register(HeaderFormatTreeProcessor(md), "headerformat", 105)
        # ~~[text]~~ for strikethrough; ref. documentation example
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()~~([\S\s]*?)~~", "del"), "del", 105)
