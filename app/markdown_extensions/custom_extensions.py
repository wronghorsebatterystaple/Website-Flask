from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor, SimpleTagInlineProcessor

import re
import xml.etree.ElementTree as etree


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


class CaptionedFigureBlockProcessor(BlockProcessor):
    FIGURE_START_RE = r"\\figure$"
    FIGURE_END_RE = r"\\endfigure$"
    CAPTION_START_RE = r"\\caption$"
    CAPTION_END_RE = r"\\endcaption$"

    def test(self, parent, block):
        return re.match(self.FIGURE_START_RE, block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove figure starting delimiter
        blocks[0] = re.sub(self.FIGURE_START_RE, "", blocks[0])

        # find and remove caption starting delimiter
        caption_start_i = -1
        for i, block in enumerate(blocks):
            if re.search(self.CAPTION_START_RE, block):
                # remove ending delimiter and note which block captions started on
                # (as captions don't have to be at the end of the figure for intuition's sake)
                caption_start_i = i
                blocks[i] = re.sub(self.CAPTION_START_RE, "", block)
                break

        # if no starting delimiter for caption, restore and do nothing
        if caption_start_i == -1:
            # `blocks = org_blocks` doesn't work since lists as passed by pointer in Python (value of reference)
            # so changing the address of `blocks` only updates the local copy of it (the pointer)
            # we need to change the values pointed to by `blocks` (its list elements)
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove caption ending delimiter, and extract element
        elem_caption = None
        for i, block in enumerate(blocks):
            if re.search(self.CAPTION_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.CAPTION_END_RE, "", block)
                # put area between in `<figcaption class="md-figure-figcaption"></figcaption>`
                elem_caption = etree.Element("figcaption")
                elem_caption.set("class", "md-figure-figcaption")
                self.parser.parseBlocks(elem_caption, blocks[caption_start_i + 1:i + 1])
                # remove used blocks
                for _ in range(caption_start_i + 1, i + 1):
                    blocks.pop(caption_start_i + 1)
                break

        # if no ending delimiter for caption, restore and do nothing
        if elem_caption is None:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove figure ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.FIGURE_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.FIGURE_END_RE, "", block)
                # build <figure class="md-figure">[image Markdown to be processed later][figcaption]</figure>
                elem_figure = etree.SubElement(parent, "figure")
                elem_figure.set("class", "md-figure")
                self.parser.parseBlocks(elem_figure, blocks[0:i + 1])
                elem_figure.append(elem_caption) # make sure captions come after everything else
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter for figure, restore and do nothing
        blocks.clear()
        blocks.extend(org_blocks)
        return False


class DropdownBlockProcessor(BlockProcessor):
    DROPDOWN_START_RE = r"\\dropdown$"
    DROPDOWN_END_RE = r"\\enddropdown$"
    SUMMARY_START_RE = r"\\summary$"
    SUMMARY_END_RE = r"\\endsummary$"

    def test(self, parent, block):
        return re.match(self.DROPDOWN_START_RE, block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)
        # remove dropdown starting delimiter
        blocks[0] = re.sub(self.DROPDOWN_START_RE, "", blocks[0])

        # remove summary starting delimiter that must immediately follow dropdown's starting delimiter
        # if no starting delimiter for summary, restore and do nothing
        if not re.search(self.SUMMARY_START_RE, blocks[1]):
            blocks.clear()
            blocks.extend(org_blocks)
            return False
        blocks[1] = re.sub(self.SUMMARY_START_RE, "", blocks[1])

        # find and remove summary ending delimiter, and extract element
        elem_summary = None
        for i, block in enumerate(blocks):
            if re.search(self.SUMMARY_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.SUMMARY_END_RE, "", block)
                # put area between in `<summary class="md-summary"></summary>`
                elem_summary = etree.Element("summary")
                elem_summary.set("class", "md-details-summary")
                self.parser.parseBlocks(elem_summary, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                break

        # if no ending delimiter for summary, restore and do nothing
        if elem_summary is None:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove dropdown ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.DROPDOWN_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.DROPDOWN_END_RE, "", block)
                # build <details class="md-details">[summary]<span class="md-details-contents">[contents]</span></details>
                elem_details = etree.SubElement(parent, "details")
                elem_details.set("class", "md-details")
                elem_details.append(elem_summary)
                elem_details_contents = etree.SubElement(elem_details, "div")
                elem_details_contents.set("class", "md-details-contents")
                self.parser.parseBlocks(elem_details_contents, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter for dropdown, restore and do nothing
        blocks.clear()
        blocks.extend(org_blocks)
        return False


class TextboxBlockProcessor(BlockProcessor):
    TEXTBOX_START_RE = r"\\textbox$"
    TEXTBOX_END_RE = r"\\endtextbox$"

    def test(self, parent, block):
        return re.match(self.TEXTBOX_START_RE, block)

    def run(self, parent, blocks):
        # remove starting delimiter
        org_block_start = blocks[0] # use simpler restoring system for non-nested BlockProcessors
        blocks[0] = re.sub(self.TEXTBOX_START_RE, "", blocks[0])

        # find and remove ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.TEXTBOX_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.TEXTBOX_END_RE, "", block)
                # put area between in `<table class="textbox"><tbody><tr><td colspan="1" rowspan="1">
                # </td></tr></tbody></table>`
                elem_table = etree.SubElement(parent, "table")
                elem_table.set("class", "md-textbox")
                elem_tbody = etree.SubElement(elem_table, "tbody")
                elem_tr = etree.SubElement(elem_tbody, "tr")
                elem_td = etree.SubElement(elem_tr, "td")
                elem_td.set("colspan", "1")
                elem_td.set("rowspan", "1")
                self.parser.parseBlocks(elem_td, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter, restore and do nothing
        blocks[0] = org_block_start
        return False


class ThmBlockProcessor(BlockProcessor):
    THM_START_RE = r"\\thm$"
    THM_END_RE = r"\\endthm$"

    def test(self, parent, block):
        return re.match(self.THM_START_RE, block)

    def run(self, parent, blocks):
        # remove starting delimiter
        org_block_start = blocks[0]
        blocks[0] = re.sub(self.THM_START_RE, "", blocks[0])

        # find and remove ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.THM_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.THM_END_RE, "", block)
                # put area between in `<blockquote class="md-thm"></blockquote>`
                elem = etree.SubElement(parent, "blockquote")
                elem.set("class", "md-thm")
                self.parser.parseBlocks(elem, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter, restore and do nothing
        blocks[0] = org_block_start
        return False


"""Markdown tweaks round 1."""
class CustomInlineExtensions(Extension):
    def extendMarkdown(self, md):
        # `__[text]__` for underline
        reg = r"()__([\S\s]*?)__"
        md.inlinePatterns.register(SimpleTagInlineProcessor(reg, "u"), "underline", 105)

        # `~~[text]~~` for strikethrough
        reg = r"()~~([\S\s]*?)~~"
        md.inlinePatterns.register(SimpleTagInlineProcessor(reg, "del"), "strikethrough", 105)

        # `'''[text]'''` for gray code
        reg = r"'''([\S\s]*?)'''"
        md.inlinePatterns.register(GrayCodeInlineProcessor(reg, md), "gray_code", 999)

        # `!\[<span data-width="[number]%">[alt text]</span>\]([image src])` for images with custom width
        # `!\[<span data-inline>[alt text]</span>\]([image src])` for images with "display: inline"
        # if both are present, `data-inline` must be after `data-width`
        reg = "!\\[<span( data-width=\"([0-9]+?%)\")?( data-inline)?>([\\S\\s]*?)</span>\\]\\(([\\S\\s]*?)\\)"
        md.inlinePatterns.register(ImageInlineProcessor(reg, md), "image", 999)

        # `\[<span data-same-page>[display text]</span>\]([link href])` for links that open on same page
        reg = r"\[<span data-same-page>([\S\s]*?)</span>\]\(([\S\s]*?)\)"
        md.inlinePatterns.register(LinkTargetInlineProcessor(reg, md), "link_target", 999)


class CustomBlockExtensions(Extension):
    def extendMarkdown(self, md):
        # `\figure\caption\endcaption\endfigure` for
        # `<figure class="md-figure"><figcaption class="md-figure-figcaption"></figcaption></figure>`
        md.parser.blockprocessors.register(CaptionedFigureBlockProcessor(md.parser), "captioned_figure", 105)

        # `\dropdown\summary\endsummary\enddropdown` for
        # `<details class="md-details"><summary class="md-details-summary"></summary></details>`
        md.parser.blockprocessors.register(DropdownBlockProcessor(md.parser), "dropdown", 105)

        # `\textbox\endtextbox` for
        # `<table class="md-textbox"><tbody><tr><td colspan="1" rowspan="1"></td></tr></tbody></table>`
        md.parser.blockprocessors.register(TextboxBlockProcessor(md.parser), "textbox", 105)

        # `\thm\endthm` for
        # `<blockquote class="md-thm"></blockquote>`
        md.parser.blockprocessors.register(ThmBlockProcessor(md.parser), "thm", 105)
