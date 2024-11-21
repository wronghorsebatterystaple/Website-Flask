import re
import xml.etree.ElementTree as etree
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor


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

    RE_SUMMARY_START = r"\\begin{summary}$"
    RE_SUMMARY_END = r"\\end{summary}$"
    re_dropdown_start = None
    re_dropdown_end = None
    typ = None

    def __init__(
            self, *args, types: dict, html_class: str="", summary_html_class: str="", content_html_class: str="",
            math_counter: bool=False, math_thm_heading: bool=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.types = types
        self.html_class = html_class
        self.summary_html_class = summary_html_class
        self.content_html_class = content_html_class
        self.math_counter = math_counter
        self.math_thm_heading = math_thm_heading

        self.RE_DROPDOWN_START_CHOICES = {}
        self.RE_DROPDOWN_END_CHOICES = {}
        for typ in self.types:
            if self.math_thm_heading:
                self.RE_DROPDOWN_START_CHOICES[typ] = rf"\\begin{{{typ}}}(?:\[(.+?)\])?(?:\[\[(.+?)\]\])?$"
            else:
                self.RE_DROPDOWN_START_CHOICES[typ] = rf"\\begin{{{typ}}}$"
            self.RE_DROPDOWN_END_CHOICES[typ] = rf"\\end{{{typ}}}$"
    
    def test(self, parent, block):
        for typ, regex in self.RE_DROPDOWN_START_CHOICES.items():
            if re.match(regex, block):
                self.typ = typ
                self.re_dropdown_start = regex
                self.re_dropdown_end = self.RE_DROPDOWN_END_CHOICES[typ]
                return True
        return False

    def run(self, parent, blocks):
        if self.re_dropdown_start is None or self.re_dropdown_end is None or self.typ is None:
            return False

        typ_opts = self.types[typ]
        org_blocks = list(blocks)
        # remove dropdown starting delimiter
        re_dropdown_start_match = None
        thm_heading_texxt
        # save theorem heading stuff like optional theorem name if applicable
        if self.math_thm_heading:
            re_dropdown_start_match = re.search(self.re_dropdown_start, blocks[0])
            if re_dropdown_start_match is None: # because this should've been prereq in `test()`!
                return False
        blocks[0] = re.sub(self.re_dropdown_start, "", blocks[0])

        # remove summary starting delimiter that must immediately follow dropdown's starting delimiter
        # if no starting delimiter for summary and no default, restore and do nothing
        if not re.search(self.RE_SUMMARY_START, blocks[1]):
            if typ_opts.get("name") is None:
                blocks.clear() # `blocks = org_blocks` doesn't work even though `org_blocks` is literally a copy
                blocks.extend(org_blocks)
                return False
        blocks[1] = re.sub(self.RE_SUMMARY_START, "", blocks[1])

        # fill in default summary value if applicable
        elem_summary = etree.Element("summary")
        elem_summary.set("class", self.summary_html_class)
        has_valid_summary = False
        default_summary = typ_opts.get("name") 
        if default_summary is not None:
            has_valid_summary = True
            elem_summary.text = default_summary
            # fill in math counter by using my `counter` extension's syntax
            if self.math_counter:
                counter = typ_opts.get("counter")
                if counter is not None:
                    elem_summary.text += f" {{{{{counter}}}}}"
            # fill in math theorem heading by using my `thm_heading` extension's syntax
            if self.math_thm_heading:
                overrides_heading = typ_opts.get("overrides_heading")
                if overrides_heading and re_dropdown_start_match.group(1) is not None:
                    elem_summary.text = re.dropdown_start_match.group(1)

                elem_summary.text = "{[" + elem_summary.text + "]}"
                if not overrides_heading and re_dropdown_start_match.group(1) is not None:
                    elem_summary.text += "[" + re_dropdown_start_match.group(1) + "]"
                if re_dropdown_start_match.group(2) is not None:
                    elem_summary.text += "[[" + re_dropdown_start_match.group(2) + "]]"

        # find and remove summary ending delimiter, and extract element
        for i, block in enumerate(blocks):
            # if we haven't found summary ending delimiter but have found the overall dropdown ending delimiter, then
            # don't keep going; maybe the summary was omitted since it could've been optional
            if re.search(self.re_dropdown_end, block):
                break
            if re.search(self.RE_SUMMARY_END, block):
                has_valid_summary = True
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_SUMMARY_END, "", block)
                # build HTML for summary
                self.parser.parseBlocks(elem_summary, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                break

        # if no valid summary (e.g. no ending delimiter with no default), restore and do nothing
        if not has_valid_summary:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove dropdown ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.re_dropdown_end, block):
                # remove ending delimiter
                blocks[i] = re.sub(self.re_dropdown_end, "", block)
                # build HTML for dropdown
                elem_details = etree.SubElement(parent, "details")
                elem_details.set("class", f"{self.html_class} {typ_opts.get('html_class', '')}")
                elem_details.append(elem_summary)
                elem_details_content = etree.SubElement(elem_details, "div")
                elem_details_content.set("class", self.content_html_class)
                self.parser.parseBlocks(elem_details_content, blocks[0:i + 1])
                # remove used blocks
                for _ in range(0, i + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter for dropdown, restore and do nothing
        blocks.clear()
        blocks.extend(org_blocks)
        return False


class DropdownExtension(Extension):
    def extendMarkdown(self, md):
        types = {
            "dropdown": {"html_class": "md-dropdown--default"}
        }
        md.parser.blockprocessors.register(
                Dropdown(md.parser, types=types, html_class="md-dropdown",
                        summary_html_class="md-dropdown__summary last-child-no-mb",
                        content_html_class="md-dropdown__content last-child-no-mb"),
                "dropdown", 105)


def makeExtension(**kwargs):
    return DropdownExtension(**kwargs)
