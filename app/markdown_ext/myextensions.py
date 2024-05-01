from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor, SimpleTagInlineProcessor
import xml.etree.ElementTree as etree

import re


class CustomThmBlockProcessor(BlockProcessor):
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
                # put area between in <blockquote class="md-thm"></blockquote>
                elem = etree.SubElement(parent, "blockquote")
                elem.set("class", "md-thm")
                self.parser.parseBlocks(elem, blocks[0:block_num + 1])
                # remove used blocks
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter, restore and do nothing
        blocks[0] = original_block
        return False


class CustomDropdownBlockProcessor(BlockProcessor):
    DROPDOWN_START_RE = r"\\dropdown$"
    DROPDOWN_END_RE = r"\\enddropdown$"
    SUMMARY_START_RE = r"\\summary$"
    SUMMARY_END_RE = r"\\endsummary$"


    def test(self, parent, block):
        return re.match(self.DROPDOWN_START_RE, block)

    def run(self, parent, blocks):
        original_block_0 = blocks[0]
        original_block_1 = blocks[1]
        # remove dropdown starting delimiter
        blocks[0] = re.sub(self.DROPDOWN_START_RE, "", blocks[0])
        # remove summary starting delimiter that must immediately follow dropdown's starting delimiter
        if not re.search(self.SUMMARY_START_RE, blocks[1]):
            blocks[0] = original_block_0
            return False
        blocks[1] = re.sub(self.SUMMARY_START_RE, "", blocks[1])

        # find summary ending delimiter
        summary_elem = None
        for block_num, block in enumerate(blocks):
            if re.search(self.SUMMARY_END_RE, block):
                # remove ending delimiter
                blocks[block_num] = re.sub(self.SUMMARY_END_RE, "", block)
                # put area between in <summary class="md-summary"></summary>
                summary_elem = etree.Element("summary")
                summary_elem.set("class", "md-details-summary")
                self.parser.parseBlocks(summary_elem, blocks[0:block_num + 1])
                # remove used blocks
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                break

        # if no ending delimiter for summary, restore and do nothing
        if summary_elem is None:
            blocks[0] = original_block_0
            blocks[1] = original_block_1
            return False

        # find dropdown ending delimiter
        for block_num, block in enumerate(blocks):
            if re.search(self.DROPDOWN_END_RE, block):
                # remove ending delimiter
                blocks[block_num] = re.sub(self.DROPDOWN_END_RE, "", block)
                # build <details class="md-details">[summary]<span class="md-contents">[contents]</span></details>
                details_elem = etree.SubElement(parent, "details")
                details_elem.set("class", "md-details")
                details_elem.append(summary_elem)
                details_contents_elem = etree.SubElement(details_elem, "div")
                details_contents_elem.set("class", "md-details-contents")
                self.parser.parseBlocks(details_contents_elem, blocks[0:block_num + 1])
                # remove used blocks
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter for dropdown, restore and do nothing
        blocks[0] = original_block_0
        blocks[1] = original_block_1
        return False


# Markdown tweaks round 1: custom syntax only!
class MyExtensions(Extension):
    def extendMarkdown(self, md):
        # __[text]__ for underline
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()__([\S\s]*?)__", "u"), "underline", 105)

        # ~~[text]~~ for strikethrough
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()~~([\S\s]*?)~~", "del"), "strikethrough", 105)

        # add "\thm\endthm" for <blockquote class="md-thm"></blockquote>
        md.parser.blockprocessors.register(CustomThmBlockProcessor(md.parser), "thm", 105);

        # add "\dropdown\summary\endsummary\enddropdown" for
        # <details class="md-details"><summary class="md-summary"></summary></details>
        md.parser.blockprocessors.register(CustomDropdownBlockProcessor(md.parser), "dropdown", 105);
