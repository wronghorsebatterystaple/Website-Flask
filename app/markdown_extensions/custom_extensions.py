from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor, SimpleTagInlineProcessor
from markdown.postprocessors import Postprocessor

import re
import xml.etree.ElementTree as etree


# TODO: release all these extensions as separate packages? how to package multiple in one like extra?
class CounterPostProcessor(Postprocessor):
    def __init__(self, regex, md, add_html_elem=False, html_id_prefix="", html_class="", *args, **kwargs):
        super().__init__(md, *args, **kwargs)
        self.regex = regex
        self.add_html_elem = add_html_elem
        self.html_id_prefix = html_id_prefix
        self.html_class = html_class
        self.counter = []

    def run(self, text):
        new_text = ""
        prev_match_end = 0
        for m in re.finditer(self.regex, text):
            input_counter = m.group(1)
            parsed_counter = input_counter.split(",")
            # make sure we have enough room to parse counter into `self.counter`
            while len(parsed_counter) > len(self.counter):
                self.counter.append(0)

            # parse counter
            for i, parsed_item in enumerate(parsed_counter):
                try:
                    parsed_item = int(parsed_item)
                except:
                    return False
                self.counter[i] += parsed_item
                # if changing current counter section, reset all child sections back to 0
                if parsed_item != 0 and len(parsed_counter) >= i + 1:
                    self.counter[i+1:] = [0] * (len(self.counter) - (i+1))

            # only output as many counter sections as were inputted
            output_counter = list(map(str, self.counter[:len(parsed_counter)]))
            output_text = ".".join(output_counter)
            if self.add_html_elem:
                output_text = \
                        f"<span id=\"{self.html_id_prefix}{'-'.join(output_counter)}\" class=\"{self.html_class}\">" \
                        + output_text \
                        + "</span>"
            new_text += text[prev_match_end:m.start()] + output_text
            prev_match_end = m.end()
        # remember to fill in the remaining text after last regex match!
        new_text += text[prev_match_end:]
        return new_text


class CaptionedFigureBlockProcessor(BlockProcessor):
    """
    Markdown:
        ```
        \begin_captioned_figure\begin_caption\end_caption\end_captioned_figure
        ```
    Generated HTML:
        ```
        <figure class="md-captioned-figure"><figcaption class="md-captioned-figure__caption"></figcaption></figure>
        ```
    """

    RE_FIGURE_START = r"\\begin_captioned_figure$"
    RE_FIGURE_END = r"\\end_captioned_figure$"
    RE_CAPTION_START = r"\\begin_caption$"
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
                # build HTML for caption
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
                # build HTML for figure
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
        \begin_cited_blockquote\begin_citation\end_citation\end_cited_blockquote
        ```
    Generated HTML:
        ```
        <blockquote class="md-cited-blockquote"></blockquote><cite class="md-cited-blockquote-cite"></cite>
        ```
    """

    RE_BLOCKQUOTE_START = r"\\begin_cited_blockquote$"
    RE_BLOCKQUOTE_END = r"\\end_cited_blockquote$"
    RE_CITATION_START = r"\\begin_citation$"
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
                # build HTML for citation
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
                # build HTML for blockquote
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
        Default `type`:
        ```
        \begin_dropdown\begin_summary\end_summary\end_dropdown
        ```

        Else:
        ```
        \begin_dropdown_[type]\begin_summary\end_summary\end_dropdown_[type]
        ```
    Generated HTML:
        ```
        <details class="md-dropdown md-dropdown--[type]"><summary class="md-dropdown__summary last-child-no-mb"></summary>
        <div class="md-dropdown__content last-child-no-mb"></div></details>
        ```
    """

    RE_DROPDOWN_START_CHOICES = {
        "default": r"\\begin_dropdown$",
        "pf": r"\\begin_dropdown_pf$",
    }
    RE_DROPDOWN_END_CHOICES = {
        "default": r"\\end_dropdown$",
        "pf": r"\\end_dropdown_pf$",
    }
    RE_SUMMARY_START = r"\\begin_summary$"
    RE_SUMMARY_END = r"\\end_summary$"
    RE_DROPDOWN_START = None
    RE_DROPDOWN_END = None
    TYPE = None
    
    def test(self, parent, block):
        for type, regex in self.RE_DROPDOWN_START_CHOICES.items():
            if re.match(regex, block):
                self.TYPE = type
                self.RE_DROPDOWN_START = regex
                self.RE_DROPDOWN_END = self.RE_DROPDOWN_END_CHOICES[type]
                return True
        return False

    def run(self, parent, blocks):
        if not self.RE_DROPDOWN_START or not self.RE_DROPDOWN_END or not self.TYPE:
            return False

        org_blocks = list(blocks)
        # remove dropdown starting delimiter
        blocks[0] = re.sub(self.RE_DROPDOWN_START, "", blocks[0])

        # remove summary starting delimiter that must immediately follow dropdown's starting delimiter
        # if no starting delimiter for summary, restore and do nothing
        has_summary = True
        if not re.search(self.RE_SUMMARY_START, blocks[1]):
            has_summary = False
            # `pf` dropdowns get default summary value, so it's optional
            if self.TYPE != "pf":
                blocks.clear() # `blocks = org_blocks` doesn't work even though `org_blocks` is literally a copy
                blocks.extend(org_blocks)
                return False
        blocks[1] = re.sub(self.RE_SUMMARY_START, "", blocks[1])

        # find and remove summary ending delimiter, and extract element
        elem_summary = None
        # fill in default summary value for `pf`
        if self.TYPE == "pf" and not has_summary:
            elem_summary = etree.Element("summary")
            elem_summary.set("class", "md-dropdown__summary last-child-no-mb")
            elem_summary.text = "Proof."
        if has_summary:
            for i, block in enumerate(blocks):
                if re.search(self.RE_SUMMARY_END, block):
                    # remove ending delimiter
                    blocks[i] = re.sub(self.RE_SUMMARY_END, "", block)
                    # build HTML for summary
                    elem_summary = etree.Element("summary")
                    elem_summary.set("class", "md-dropdown__summary last-child-no-mb")
                    self.parser.parseBlocks(elem_summary, blocks[0:i + 1])
                    # remove used blocks
                    for _ in range(0, i + 1):
                        blocks.pop(0)
                    break

        # if no ending delimiter for summary (and summary is not optional), restore and do nothing
        if elem_summary is None:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove dropdown ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.RE_DROPDOWN_END, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_DROPDOWN_END, "", block)
                # build HTML for dropdown
                elem_details = etree.SubElement(parent, "details")
                elem_details.set("class", f"md-dropdown md-dropdown--{self.TYPE}")
                elem_details.append(elem_summary)
                elem_details_content = etree.SubElement(elem_details, "div")
                elem_details_content.set("class", "md-dropdown__content last-child-no-mb")
                self.parser.parseBlocks(elem_details_content, blocks[0:i + 1])
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
        Default `type`:
        ```
        \begin_textbox\end_textbox
        ```

        Else:
        ```
        \begin_textbox_[type]\end_textbox_[type]
        ```
    Generated HTML:
        ```
        <table class="md-textbox md-textbox--[type]"><tbody><tr><td colspan="1" rowspan="1"></td></tr></tbody></table>
        ```
    """

    # TODO: if publishing these extensions, let these dicts be defined as kwargs in extension config
    RE_START_CHOICES = {
        "default": r"\\begin_textbox$",
        "coro": r"\\begin_textbox_coro$",
        "defn": r"\\begin_textbox_defn$",
        "prop": r"\\begin_textbox_prop$",
        "thm": r"\\begin_textbox_thm$"
    }
    RE_END_CHOICES = {
        "default": r"\\end_textbox$",
        "coro": r"\\end_textbox_coro$",
        "defn": r"\\end_textbox_defn$",
        "prop": r"\\end_textbox_prop$",
        "thm": r"\\end_textbox_thm$"
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
                elem_table = etree.SubElement(parent, "table")
                elem_table.set("class", f"md-textbox md-textbox--{self.TYPE}")
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

        regex = r"{{\s*([0-9,]+)\s*}}"
        md.postprocessors.register(CounterPostProcessor(
            regex, md, add_html_elem=True, html_id_prefix="md-counter-", html_class="md-counter"), "counter", 105)


class CustomBlockExtensions(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(CaptionedFigureBlockProcessor(md.parser), "captioned_figure", 105)
        md.parser.blockprocessors.register(CitedBlockquoteBlockProcessor(md.parser), "cited_blockquote", 105)
        md.parser.blockprocessors.register(DropdownBlockProcessor(md.parser), "dropdown", 105)
        md.parser.blockprocessors.register(TextboxBlockProcessor(md.parser), "textbox", 105)
