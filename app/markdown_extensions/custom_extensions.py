from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor, SimpleTagInlineProcessor
from markdown.preprocessors import Preprocessor

import re
import xml.etree.ElementTree as etree


# TODO: if publishing, let user define html classes like with counter

class CaptionedFigure(BlockProcessor):
    """
    A figure with a caption underneath. Useful for images, but the figure content doesn't have to be an image.

    Usage:
        ```

        \begin{captioned_figure}

        <figure content>

        \begin{caption}

        <caption>

        \end{caption}

        \end{captioned_figure}

        ```
        - HTML output:
            ```
            <figure class="md-captioned-figure">
              [figure content]
              <figcaption class="md-captioned-figure__caption">
                [caption]
              </figcaption>
            </figure>
            ```
        - Note that the `caption` block can be placed anywhere within the `captioned_figure` block
    """

    RE_FIGURE_START = r"\\begin{captioned_figure}$"
    RE_FIGURE_END = r"\\end{captioned_figure}$"
    RE_CAPTION_START = r"\\begin{caption}$"
    RE_CAPTION_END = r"\\end{caption}$"

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


# TODO: release all these extensions as separate packages? how to package multiple in one like extra?
# TODO: if releasing Counter, test with no adding html/varied params, also linking to counter via URL fragment
class Counter(Preprocessor):
    # TODO: if publishing, verify example
    """
    A counter that is intended to reproduce LaTeX theorem counter functionality by allowing you to specify increments
    for each "counter section".
        - "Counter sections" are the typically period-separated numbers in theorem counters. For example, in
          `Theorem 1.2.4`, the counter sections are 1, 2, and 4.

    Functionality:
        - Increments each section of the counter by specified amount
        - Resets all child counters section to 0 after incrementing a counter
        - Displays only as many counter sections as provided in the Markdown

    Usage:
        ```
        {{<section 1 change>,<section 2 change>,<...>}}
        ```

    Example usage:
        - Markdown:
            ```
            Section {{1}}
            Subsection {{0,1,0}} (displays as many sections as given)
            Lemma {{0,0,0,1}}
            Theorem {{0,0,1}} (the fourth counter section is reset here). Let \(s\) be a lorem ipsum.
            Mental Breakdown {{0,0,0,3}}
            I have no idea what this means {{1,2,0,3,9}}
            ```
        - Output:
            ```
            Section 1
            Subsection 1.1.0 (displays as many sections as given)
            Lemma 1.1.1.1
            Theorem 1.1.2 (the fourth counter section is reset here). Let \(s\) be a lorem ipsum.
            Mental Breakdown 1.1.2.3
            I have no idea what this means 2.3.2.6.9
            ```
    """

    def __init__(self, md, regex, add_html_elem=False, html_id_prefix="", html_class="", *args, **kwargs):
        super().__init__(md, *args, **kwargs)
        self.regex = regex
        self.add_html_elem = add_html_elem
        self.html_id_prefix = html_id_prefix
        self.html_class = html_class
        self.counter = []

    def run(self, lines):
        new_lines = []
        for line in lines:
            new_line = ""
            prev_match_end = 0

            for m in re.finditer(self.regex, line):
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
                output_counter_text = ".".join(output_counter)
                if self.add_html_elem:
                    output_counter_text = \
                            f"<span id=\"{self.html_id_prefix}{'-'.join(output_counter)}\" class=\"{self.html_class}\">" \
                            + output_counter_text \
                            + "</span>"
                new_line += line[prev_match_end:m.start()] + output_counter_text
                prev_match_end = m.end()
            # remember to fill in the remaining text after last regex match!
            new_line += line[prev_match_end:]
            new_lines.append(new_line)
        return new_lines


class CitedBlockquote(BlockProcessor):
    """
    A blockquote with a citation underneath. Note that the citation goes in a line below the blockquote, so this is
    not designed for formal in-text citations.

    Usage:
        ```
        
        \begin{cited_blockquote}
        
        <quote>

        \begin{citation}

        <citation>

        \end{citation}

        \end{cited_blockquote}

        ```
        - HTML output:
            ```
            <blockquote class="md-cited-blockquote">
              <quote>
            </blockquote>
            <cite class="md-cited-blockquote__cite">
              <citation>
            </cite>
            ```
        - Note that the `citation` block can be placed anywhere within the `cited_blockquote` block
    """

    RE_BLOCKQUOTE_START = r"\\begin{cited_blockquote}$"
    RE_BLOCKQUOTE_END = r"\\end{cited_blockquote}$"
    RE_CITATION_START = r"\\begin{citation}$"
    RE_CITATION_END = r"\\end{citation}$"

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
                elem_citation.set("class", "md-cited-blockquote__cite")
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


class Dropdown(BlockProcessor):
    """
    A dropdown that can be toggled open or closed, with only a summary (preview) portion shown when closed.

    Usage:
        ```

        \begin{<type>}

        \begin{summary}
        
        <summary>

        \end{summary}

        <collapsible content>

        \end{<type>}

        ```
        - HTML output:
            ```
            <details class="md-dropdown md-dropdown--[type]">
              <summary class="md-dropdown__summary last-child-no-mb">
                [summary]
              </summary>
              <div class="md-dropdown__content last-child-no-mb">
                [collapsible content]
              </div>
            </details>
            ```
    """

    RE_DROPDOWN_START_CHOICES = {
        "default": r"\\begin{dropdown}$",
        "exer": r"\\begin{exer}$",
        "pf": r"\\begin{pf}$",
        "rmk": r"\\begin{rmk}$"
    }
    RE_DROPDOWN_END_CHOICES = {
        "default": r"\\end{dropdown}$",
        "exer": r"\\end{exer}$",
        "pf": r"\\end{pf}$",
        "rmk": r"\\end{rmk}$"
    }
    RE_SUMMARY_START = r"\\begin{summary}$"
    RE_SUMMARY_END = r"\\end{summary}$"
    RE_DROPDOWN_START = None
    RE_DROPDOWN_END = None
    TYPE = None
    DEFAULT_SUMMARIES = {
        "pf": "{[Proof]}", # syntax for later processing by `theorem_heading` custom extension
        "rmk": "{[Remark]}"
    }
    
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
            # these dropdowns get default summary value, so it's optional
            if self.TYPE not in self.DEFAULT_SUMMARIES:
                blocks.clear() # `blocks = org_blocks` doesn't work even though `org_blocks` is literally a copy
                blocks.extend(org_blocks)
                return False
        blocks[1] = re.sub(self.RE_SUMMARY_START, "", blocks[1])

        # find and remove summary ending delimiter, and extract element
        elem_summary = None
        # fill in default summary value for these
        if self.TYPE in self.DEFAULT_SUMMARIES and not has_summary:
            elem_summary = etree.Element("summary")
            elem_summary.set("class", "md-dropdown__summary last-child-no-mb")
            elem_summary.text = self.DEFAULT_SUMMARIES[self.TYPE]
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


class Textbox(BlockProcessor):
    """
    A textbox (1-cell table).

    Usage:
        ```

        \begin{<type>}
        
        <content>

        \end{<type>}

        ```
        - HTML output:
            ```
            <table class="md-textbox md-textbox--[type] last-child-no-mb">
              <tbody>
                <tr>
                  <td colspan="1" rowspan="1">
                  [content]
                  </td>
                </tr>
              </tbody>
            </table>
            ```
    """

    # TODO: if publishing these extensions, let these dicts be defined as kwargs in extension config
    RE_START_CHOICES = {
        "default": r"\\begin{textbox}$",
        "coro": r"\\begin{coro}$",
        "defn": r"\\begin{defn}$",
        "impt": r"\\begin{impt}$",
        "notat": r"\\begin{notat}$",
        "prop": r"\\begin{prop}$",
        "thm": r"\\begin{thm}$"
    }
    RE_END_CHOICES = {
        "default": r"\\end{textbox}$",
        "coro": r"\\end{coro}$",
        "defn": r"\\end{defn}$",
        "impt": r"\\end{impt}$",
        "notat": r"\\end{notat}$",
        "prop": r"\\end{prop}$",
        "thm": r"\\end{thm}$"
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
                elem_table.set("class", f"md-textbox md-textbox--{self.TYPE} last-child-no-mb")
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


class TheoremHeading(InlineProcessor):
    """
    A theorem heading that allows you to add custom styling and can generate linkable HTML `id`s.

    Usage:
        ```
        {[<theorem heading>]}{<optional theorem name>}[<optional hidden theorem name>]
        ```
        - HTML output:
            ```
            <span id="[optional theorem name/optional hidden theorem name]" class="md-theorem-heading">
              [theorem heading]
            </span>
            [optional theorem name]
            ```
        - `<optional hidden theorem name>` only adds an HTML `id`, and is not displayed. It is ignored if
          `<optional theorem name>` is provided.
    """

    def handleMatch(self, m, current_text_block):
        elem = etree.Element("span")
        elem.text = m.group(1)
        if m.group(2):
            elem.text += f" ({m.group(2)})"
            elem.set("id", TheoremHeading.format_for_html(m.group(2)))
        elif m.group(3):
            elem.set("id", TheoremHeading.format_for_html(m.group(3)))
        elem.set("class", "md-theorem-heading")
        return elem, m.start(0), m.end(0)

    @staticmethod
    def format_for_html(s):
        s = ("-".join(s.split())).lower() 
        s = s[:-1].replace(".", "-") + s[-1] # replace periods except possibly last one with dashes (e.g. thm counter)
        s = re.sub(r"[^A-Za-z0-9-]", r"", s)
        return s


class CustomInlineExtensions(Extension):
    def extendMarkdown(self, md):
        """
        Underlines text.

        Usage:
            ```
            __<text>__
            ```
        """
        regex = r"()__([\S\s]+?)__"
        md.inlinePatterns.register(SimpleTagInlineProcessor(regex, "u"), "underline", 105)

        """
        Strikes through text.
        
        Usage:
            ```
            ~~<text>~~
            ```
        """
        regex = r"()~~([\S\s]+?)~~"
        md.inlinePatterns.register(SimpleTagInlineProcessor(regex, "del"), "strikethrough", 105)

        regex = r"{{([0-9,]+)}}"
        md.preprocessors.register(Counter(md, regex, add_html_elem=True, html_id_prefix=""), "counter", 105)

        regex = r"{\[(.+?)\]}(?:{(.+?)})?(?:\[(.+?)\])?"
        md.inlinePatterns.register(TheoremHeading(regex, md), "theorem_heading", 105)


class CustomBlockExtensions(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(CaptionedFigure(md.parser), "captioned_figure", 105)
        md.parser.blockprocessors.register(CitedBlockquote(md.parser), "cited_blockquote", 105)
        md.parser.blockprocessors.register(Dropdown(md.parser), "dropdown", 105)
        md.parser.blockprocessors.register(Textbox(md.parser), "textbox", 105)
