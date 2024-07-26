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
                # (as captions can be at the end of the figure; not a must though (in case no figure ending deliminator))
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
        caption_elem = None
        for i, block in enumerate(blocks):
            if re.search(self.CAPTION_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.CAPTION_END_RE, "", block)
                # put area between in <figcaption class="md-figure-figcaption"></figcaption>
                caption_elem = etree.Element("figcaption")
                caption_elem.set("class", "md-figure-figcaption")
                self.parser.parseBlocks(caption_elem, blocks[caption_start_i + 1:i + 1])
                # remove used blocks
                for _ in range(caption_start_i + 1, i + 1):
                    blocks.pop(caption_start_i + 1)
                break

        # if no ending delimiter for caption, restore and do nothing
        if caption_elem is None:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove figure ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.FIGURE_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.FIGURE_END_RE, "", block)
                # build <figure class="md-figure">[image Markdown to be processed later][figcaption]</figure>
                figure_elem = etree.SubElement(parent, "figure")
                figure_elem.set("class", "md-figure")
                self.parser.parseBlocks(figure_elem, blocks[0:i + 1])
                figure_elem.append(caption_elem) # make sure captions come after everything else
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
        summary_elem = None
        for i, block in enumerate(blocks):
            if re.search(self.SUMMARY_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.SUMMARY_END_RE, "", block)
                # put area between in <summary class="md-summary"></summary>
                summary_elem = etree.Element("summary")
                summary_elem.set("class", "md-details-summary")
                self.parser.parseBlocks(summary_elem, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                break

        # if no ending delimiter for summary, restore and do nothing
        if summary_elem is None:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove dropdown ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.DROPDOWN_END_RE, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.DROPDOWN_END_RE, "", block)
                # build <details class="md-details">[summary]<span class="md-details-contents">[contents]</span></details>
                details_elem = etree.SubElement(parent, "details")
                details_elem.set("class", "md-details")
                details_elem.append(summary_elem)
                details_contents_elem = etree.SubElement(details_elem, "div")
                details_contents_elem.set("class", "md-details-contents")
                self.parser.parseBlocks(details_contents_elem, blocks[0:i + 1])
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
                # put area between in <table class="textbox"><tbody><tr><td colspan="1" rowspan="1"></td></tr></tbody></table>
                table_elem = etree.SubElement(parent, "table")
                table_elem.set("class", "md-textbox")
                tbody_elem = etree.SubElement(table_elem, "tbody")
                tr_elem = etree.SubElement(tbody_elem, "tr")
                td_elem = etree.SubElement(tr_elem, "td")
                td_elem.set("colspan", "1")
                td_elem.set("rowspan", "1")
                self.parser.parseBlocks(td_elem, blocks[0:i + 1])
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
                # put area between in <blockquote class="md-thm"></blockquote>
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


# Markdown tweaks round 1
class MyInlineExtensions(Extension):
    def extendMarkdown(self, md):
        # `__[text]__` for underline
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()__([\S\s]*?)__", "u"), "underline", 105)

        # `~~[text]~~` for strikethrough
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"()~~([\S\s]*?)~~", "del"), "strikethrough", 105)

        # `'''[text]'''` for gray code
        md.inlinePatterns.register(GrayCodeInlineProcessor(r"'''([\S\s]*?)'''", md), "gray_code", 999)

        # `!\[<span data-width="[number]%">[alt text]</span>\]([image src])` for images with custom width
        # `!\[<span data-inline>[alt text]</span>\]([image src])` for images with "display: inline"
        # if both are present, `data-inline` must be after `data-width`
        md.inlinePatterns.register(ImageInlineProcessor("!\\[<span( data-width=\"([0-9]+?%)\")?( data-inline)?>([\\S\\s]*?)</span>\\]\\(([\\S\\s]*?)\\)",
                md), "image", 999)

        # `\[<span data-same-page>[display text]</span>\]([link href])` for links that open on same page (non-default)
        md.inlinePatterns.register(LinkTargetInlineProcessor(r"\[<span data-same-page>([\S\s]*?)</span>\]\(([\S\s]*?)\)",
                md), "link_target", 999)


class MyBlockExtensions(Extension):
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
