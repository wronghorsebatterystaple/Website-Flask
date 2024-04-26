from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor, SimpleTagInlineProcessor
from markdown.treeprocessors import Treeprocessor
import xml.etree.ElementTree as etree

import re


class ThmBlockquoteBlockProcessor(BlockProcessor):
    THM_START_RE = r"\\thm$"
    THM_END_RE = r"\\endthm$"


    def test(self, parent, block):
        return re.match(self.THM_START_RE, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        # remove starting delimiter
        blocks[0] = re.sub(self.THM_START_RE, "", blocks[0])

        # find ending delimiter
        for block_num, block in enumerate(blocks):
            if re.search(self.THM_END_RE, block):
                # remove ending delimiter
                blocks[block_num] = re.sub(self.THM_END_RE, "", block)
                # put area between in <blockquote class="math-blockquote"></blockquote>
                elem = etree.SubElement(parent, "blockquote")
                elem.set("class", "thm")
                self.parser.parseBlocks(elem, blocks[0:block_num + 1])
                # remove used blocks
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter, restore and do nothing
        blocks[0] = original_block
        return False


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
        # ~~[text]~~ for strikethrough; ref. documentation example
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()~~([\S\s]*?)~~", "del"), "del", 105)

        # add header classes for CSS customization
        md.treeprocessors.register(HeaderFormatTreeProcessor(md), "headerformat", 105)

        # add math-blockquote class for CSS customization, using "\thm " at the beginning of a line
        md.parser.blockprocessors.register(ThmBlockquoteBlockProcessor(md.parser), "thmblockquote", 105);
