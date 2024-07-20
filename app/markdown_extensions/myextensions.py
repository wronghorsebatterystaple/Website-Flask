from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor, SimpleTagInlineProcessor
import xml.etree.ElementTree as etree

import re


class GrayCodeInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        elem = etree.Element("code")
        elem.set("class", "gray")
        elem.text = m.group(1)
        return elem, m.start(0), m.end(0)


class ImageInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        elem = etree.Element("img")
        elem.set("src", m.group(5))
        elem.set("alt", m.group(4))
        if m.group(2):
            elem.set("width", m.group(2))
        if m.group(3):
            elem.set("class", "md-image-inline")
        return elem, m.start(0), m.end(0)


class LinkTargetInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        elem = etree.Element("a")
        elem.set("data-same-page", "")
        elem.set("href", m.group(2))
        elem.text = m.group(1)
        return elem, m.start(0), m.end(0)


class DropdownBlockProcessor(BlockProcessor):
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


class TextboxBlockProcessor(BlockProcessor):
    TEXTBOX_START_RE = r"\\textbox$"
    TEXTBOX_END_RE = r"\\endtextbox$"

    def test(self, parent, block):
        return re.match(self.TEXTBOX_START_RE, block)

    def run(self, parent, blocks):
        original_block = blocks[0]
        # remove starting delimiter
        blocks[0] = re.sub(self.TEXTBOX_START_RE, "", blocks[0])

        # find ending delimiter
        for block_num, block in enumerate(blocks):
            if re.search(self.TEXTBOX_END_RE, block):
                # remove ending delimiter
                blocks[block_num] = re.sub(self.TEXTBOX_END_RE, "", block)
                # put area between in <table class="textbox"><tbody><tr><td colspan="1" rowspan="1"></td></tr></tbody></table>
                table_elem = etree.SubElement(parent, "table")
                table_elem.set("class", "md-textbox")
                tbody_elem = etree.SubElement(table_elem, "tbody")
                tr_elem = etree.SubElement(tbody_elem, "tr")
                td_elem = etree.SubElement(tr_elem, "td")
                td_elem.set("colspan", "1")
                td_elem.set("rowspan", "1")
                self.parser.parseBlocks(td_elem, blocks[0:block_num + 1])
                # remove used blocks
                for _ in range(0, block_num + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter, restore and do nothing
        blocks[0] = original_block
        return False


class ThmBlockProcessor(BlockProcessor):
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


# Markdown tweaks round 1: custom syntax only!
class MyInlineExtensions(Extension):
    def extendMarkdown(self, md):
        # __[text]__ for underline
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()__([\S\s]*?)__", "u"), "underline", 105)

        # ~~[text]~~ for strikethrough
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()~~([\S\s]*?)~~", "del"), "strikethrough", 105)

        # '''[text]''' for gray code
        md.inlinePatterns.register(GrayCodeInlineProcessor(r"'''([\S\s]*?)'''", md), "gray_code", 999)

        # !\[<span data-width="[number]%">[alt text]</span>\]([image src]) for images with custom width
        # !\[<span data-inline>[alt text]</span>\]([image src]) for images with "display: inline"
        # If both are present, "data-inline" must be after "data-width"
        md.inlinePatterns.register(ImageInlineProcessor("!\\[<span( data-width=\"([0-9]+?%)\")?( data-inline)?>([\\S\\s]*?)</span>\\]\\(([\\S\\s]*?)\\)",
                md), "image", 999)

        # \[<span data-same-page>[display text]</span>\]([link href]) for links that open on same page (non-default)
        md.inlinePatterns.register(LinkTargetInlineProcessor(r"\[<span data-same-page>([\S\s]*?)</span>\]\(([\S\s]*?)\)",
                md), "link_target", 999)


class MyBlockExtensions(Extension):
    def extendMarkdown(self, md):
        # add "\dropdown\summary\endsummary\enddropdown" for
        # <details class="md-details"><summary class="md-summary"></summary></details>
        md.parser.blockprocessors.register(DropdownBlockProcessor(md.parser), "dropdown", 105)

        # add "\textbox\endtextbox" for
        # <table class="md-textbox"><tbody><tr><td colspan="1" rowspan="1"></td></tr></tbody></table>
        md.parser.blockprocessors.register(TextboxBlockProcessor(md.parser), "textbox", 105)

        # add "\thm\endthm" for <blockquote class="md-thm"></blockquote>
        md.parser.blockprocessors.register(ThmBlockProcessor(md.parser), "thm", 105)
