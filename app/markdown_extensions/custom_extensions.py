from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor, SimpleTagInlineProcessor
from markdown.treeprocessors import Treeprocessor

import re
import xml.etree.ElementTree as etree


class GrayCodeInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        elem = etree.Element("code")
        elem.set("class", "gray")
        elem.text = m.group(1)
        return elem, m.start(0), m.end(0)


class HeadingIdTreeprocessor(Treeprocessor):
    """
    `<h1>` and `<h2>` get `id` attributes based on their text contents so they are reachable by URL fragment.
    """

    def run(self, root):
        for elem in root:
            if elem.tag in {"h1", "h2"}:
                elem.set("id", HeadingIdTreeprocessor.sanitize_heading(elem.text))
            self.run(elem)

    @staticmethod
    def sanitize_heading(heading):
        """
        Replaces whitespace with hyphens, and removes all non-alphanumeric and non-hypthen characters.
        """

        heading = "-".join(heading.split())
        heading = re.sub("[^A-Za-z0-9-]", "", heading)
        return heading


class ImageInlineProcessor(InlineProcessor):
    """
    Images with custom width:
        ```
        !\[<span data-width="[number]%">[alt text]</span>\]([image src])
        ```
    Images with `display: inline`:
        ```
        !\[<span data-inline>[alt text]</span>\]([image src])
        ```
    if both are present, `data-inline` must be after `data-width`.
    """

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
    """
    Links that open on same page, instead of default `target="_blank"`:
        ```
        \[<span data-same-page>[display text]</span>\]([link href])
        ```
    """

    def handleMatch(self, m, data):
        elem = etree.Element("a")
        elem.set("data-same-page", "")
        elem.set("href", m.group(2))
        elem.text = m.group(1)
        return elem, m.start(0), m.end(0)


class CaptionedFigureBlockProcessor(BlockProcessor):
    """
    Markdown:
        ```
        \captioned_figure\caption\end_caption\end_captioned_figure
        ```
    HTML:
        ```
        <figure class="md-captioned-figure"><figcaption class="md-captioned-figure__caption"></figcaption></figure>
        ```
    """

    RE_FIGURE_START = r"\\captioned_figure$"
    RE_FIGURE_END = r"\\end_captioned_figure$"
    RE_CAPTION_START = r"\\caption$"
    RE_CAPTION_END = r"\\end_caption$"

    def test(self, parent, block):
        return re.match(self.RE_FIGURE_START, block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove figure starting delimiter
        blocks[0] = re.sub(self.RE_FIGURE_START, "", blocks[0])

        # find and remove caption starting delimiter
        caption_start_i = -1
        for i, block in enumerate(blocks):
            if re.search(self.RE_CAPTION_START, block):
                # remove ending delimiter and note which block captions started on
                # (as caption content itself is an unknown number of blocks)
                caption_start_i = i
                blocks[i] = re.sub(self.RE_CAPTION_START, "", block)
                break

        # if no starting delimiter for caption, restore and do nothing
        if caption_start_i == -1:
            # `blocks = org_blocks` doesn't work since lists are passed by pointer in Python (value of reference)
            # so changing the address of `blocks` only updates the local copy of it (the pointer)
            # we need to change the values pointed to by `blocks` (its list elements)
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove caption ending delimiter, and extract element
        elem_caption = None
        for i, block in enumerate(blocks):
            if re.search(self.RE_CAPTION_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_CAPTION_END, "", block)
                # put area between in `<figcaption class="md-captioned-figure__caption"></figcaption>`
                elem_caption = etree.Element("figcaption")
                elem_caption.set("class", "md-captioned-figure__caption")
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
            if re.search(self.RE_FIGURE_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_FIGURE_END, "", block)
                # build <figure class="md-captioned-figure">[figure content][figcaption]</figure>
                elem_figure = etree.SubElement(parent, "figure")
                elem_figure.set("class", "md-captioned-figure")
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


class CitedBlockquoteBlockProcessor(BlockProcessor):
    """
    Markdown:
        ```
        \cited_blockquote\citation\end_citation\end_cited_blockquote
        ```
    HTML:
        ```
        <blockquote class="md-cited-blockquote"></blockquote><cite class="md-cited-blockquote-cite"></cite>
        ```
    """

    RE_BLOCKQUOTE_START = r"\\cited_blockquote$"
    RE_BLOCKQUOTE_END = r"\\end_cited_blockquote$"
    RE_CITATION_START = r"\\citation$"
    RE_CITATION_END = r"\\end_citation$"

    def test(self, parent, block):
        return re.match(self.RE_BLOCKQUOTE_START, block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove blockquote starting delimiter
        blocks[0] = re.sub(self.RE_BLOCKQUOTE_START, "", blocks[0])

        # find and remove citation starting delimiter
        citation_start_i = -1
        for i, block in enumerate(blocks):
            if re.search(self.RE_CITATION_START, block):
                # remove ending delimiter and note which block citation started on
                # (as citation content itself is an unknown number of blocks)
                citation_start_i = i
                blocks[i] = re.sub(self.RE_CITATION_START, "", block)
                break

        # if no starting delimiter for citation, restore and do nothing
        if citation_start_i == -1:
            # `blocks = org_blocks` doesn't work since lists are passed by pointer in Python (value of reference)
            # so changing the address of `blocks` only updates the local copy of it (the pointer)
            # we need to change the values pointed to by `blocks` (its list elements)
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove citation ending delimiter, and extract element
        elem_citation = None
        for i, block in enumerate(blocks):
            if re.search(self.RE_CITATION_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_CITATION_END, "", block)
                # put area between in `<cite class="md-cited-blockquote-cite"></cite>`
                elem_citation = etree.Element("cite")
                elem_citation.set("class", "md-cited-blockquote-cite")
                self.parser.parseBlocks(elem_citation, blocks[citation_start_i + 1:i + 1])
                # remove used blocks
                for _ in range(citation_start_i + 1, i + 1):
                    blocks.pop(citation_start_i + 1)
                break

        # if no ending delimiter for citation, restore and do nothing
        if elem_citation is None:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove blockquote ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.RE_BLOCKQUOTE_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_BLOCKQUOTE_END, "", block)
                # build `<blockquote class="md-cited-blockquote">[blockquote]</blockquote>
                # <cite class="md-cited-blockquote-citation">[citation]</class></blockquote>`
                elem_blockquote = etree.SubElement(parent, "blockquote")
                elem_blockquote.set("class", "md-cited-blockquote")
                self.parser.parseBlocks(elem_blockquote, blocks[0:i + 1])
                parent.append(elem_citation) # make sure citation comes after everything else
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter for blockquote, restore and do nothing
        blocks.clear()
        blocks.extend(org_blocks)
        return False


class DropdownBlockProcessor(BlockProcessor):
    """
    Markdown:
        ```
        \dropdown\summary\end_summary\end_dropdown
        ```
    HTML:
        ```
        <details class="md-dropdown"><summary class="md-dropdown__summary"></summary>
        <div class="md-dropdown__contents"></div></details>
        ```
    """

    RE_DROPDOWN_START = r"\\dropdown$"
    RE_DROPDOWN_END = r"\\end_dropdown$"
    RE_SUMMARY_START = r"\\summary$"
    RE_SUMMARY_END = r"\\end_summary$"

    def test(self, parent, block):
        return re.match(self.RE_DROPDOWN_START, block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove dropdown starting delimiter
        blocks[0] = re.sub(self.RE_DROPDOWN_START, "", blocks[0])

        # remove summary starting delimiter that must immediately follow dropdown's starting delimiter
        # if no starting delimiter for summary, restore and do nothing
        if not re.search(self.RE_SUMMARY_START, blocks[1]):
            blocks.clear()
            blocks.extend(org_blocks)
            return False
        blocks[1] = re.sub(self.RE_SUMMARY_START, "", blocks[1])

        # find and remove summary ending delimiter, and extract element
        elem_summary = None
        for i, block in enumerate(blocks):
            if re.search(self.RE_SUMMARY_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_SUMMARY_END, "", block)
                # put area between in `<summary class="md-summary"></summary>`
                elem_summary = etree.Element("summary")
                elem_summary.set("class", "md-dropdown__summary")
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
            if re.search(self.RE_DROPDOWN_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_DROPDOWN_END, "", block)
                # build `<details class="md-dropdown">[summary]<div class="md-dropdown__contents">[contents]</div>
                # </details>`
                elem_details = etree.SubElement(parent, "details")
                elem_details.set("class", "md-dropdown")
                elem_details.append(elem_summary)
                elem_details_contents = etree.SubElement(elem_details, "div")
                elem_details_contents.set("class", "md-dropdown__contents")
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
    """
    Markdown:
        ```
        \textbox\end_textbox
        ```
    HTML:
        ```
        <table class="md-textbox"><tbody><tr><td colspan="1" rowspan="1"></td></tr></tbody></table>
        ```
    """

    RE_START = r"\\textbox$"
    RE_END = r"\\end_textbox$"

    def test(self, parent, block):
        return re.match(self.RE_START, block)

    def run(self, parent, blocks):
        # remove starting delimiter
        org_block_start = blocks[0] # use simpler restoring system for non-nested BlockProcessors
        blocks[0] = re.sub(self.RE_START, "", blocks[0])

        # find and remove ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.RE_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_END, "", block)
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
    """
    Markdown:
        ```
        \thm\end_thm
        ```
    HTML:
        ```
        <blockquote class="md-thm"></blockquote>
        ```
    """

    RE_START = r"\\thm$"
    RE_END = r"\\end_thm$"

    def test(self, parent, block):
        return re.match(self.RE_START, block)

    def run(self, parent, blocks):
        # remove starting delimiter
        org_block_start = blocks[0]
        blocks[0] = re.sub(self.RE_START, "", blocks[0])

        # find and remove ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.RE_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_END, "", block)
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
        regex = r"()__([\S\s]*?)__"
        md.inlinePatterns.register(SimpleTagInlineProcessor(regex, "u"), "underline", 105)

        # `~~[text]~~` for strikethrough
        regex = r"()~~([\S\s]*?)~~"
        md.inlinePatterns.register(SimpleTagInlineProcessor(regex, "del"), "strikethrough", 105)

        # `'''[text]'''` for gray code
        regex = r"'''([\S\s]*?)'''"
        md.inlinePatterns.register(GrayCodeInlineProcessor(regex, md), "gray_code", 999)

        regex = "!\\[<span( data-width=\"([0-9]+?%)\")?( data-inline)?>([\\S\\s]*?)</span>\\]\\(([\\S\\s]*?)\\)"
        md.inlinePatterns.register(ImageInlineProcessor(regex, md), "image", 999)

        regex = r"\[<span data-same-page>([\S\s]*?)</span>\]\(([\S\s]*?)\)"
        md.inlinePatterns.register(LinkTargetInlineProcessor(regex, md), "link_target", 999)


class CustomBlockExtensions(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(CaptionedFigureBlockProcessor(md.parser), "captioned_figure", 105)
        md.parser.blockprocessors.register(CitedBlockquoteBlockProcessor(md.parser), "cited_blockquote", 105)
        md.parser.blockprocessors.register(DropdownBlockProcessor(md.parser), "dropdown", 105)
        md.parser.blockprocessors.register(TextboxBlockProcessor(md.parser), "textbox", 105)
        md.parser.blockprocessors.register(ThmBlockProcessor(md.parser), "thm", 105)
        md.treeprocessors.register(HeadingIdTreeprocessor(self), "heading_id", 999)
