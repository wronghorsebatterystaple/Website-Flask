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


class DropdownExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(Dropdown(md.parser), "dropdown", 105)


def makeExtension(**kwargs):
    return DropdownExtension(**kwargs)
