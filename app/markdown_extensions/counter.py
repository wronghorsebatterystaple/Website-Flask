import re
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


# TODO: if releasing Counter, test with no adding html/varied params, also linking to counter via URL fragment
class Counter(Postprocessor):
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

    def __init__(self, md, regex, *args, add_html_elem=False, html_id_prefix="", html_class="", **kwargs):
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
            output_counter_text = ".".join(output_counter)
            if self.add_html_elem:
                output_counter_text = \
                        f"<span id=\"{self.html_id_prefix}{'-'.join(output_counter)}\" class=\"{self.html_class}\">" \
                        + output_counter_text \
                        + "</span>"
            new_text += text[prev_match_end:m.start()] + output_counter_text
            prev_match_end = m.end()
        # fill in the remaining text after last regex match!
        new_text += text[prev_match_end:]
        return new_text


class CounterExtension(Extension):
    def extendMarkdown(self, md):
        regex = r"{{([0-9,]+)}}"
        md.postprocessors.register(Counter(md, regex, add_html_elem=True, html_id_prefix=""), "counter", 105)
        # registering resets state between uses of `markdown.Markdown` object (see docs)
        md.registerExtension(self)


def makeExtension(**kwargs):
    return CounterExtension(**kwargs)
