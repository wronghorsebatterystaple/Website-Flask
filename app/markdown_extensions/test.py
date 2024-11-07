from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

import re
import xml.etree.ElementTree as etree


class CounterInlineProcessor(InlineProcessor):
    def __init__(self, pattern, md=None):
        super().__init__(pattern, md)
        self.counter = []

    def handleMatch(self, m, data):
        input_counter = m.group(1)
        parsed_counter = input_counter.split(",")
        while len(parsed_counter) > len(self.counter):
            self.counter.append(0)

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
        elem = etree.Element("span")
        elem.set("id", f"md-counter-{'-'.join(output_counter)}")
        elem.set("class", "md-counter")
        elem.text = ".".join(output_counter)
        return elem, m.start(0), m.end(0)


class CustomInlineExtensions(Extension):
    def extendMarkdown(self, md):
        regex = r"{{\s*([0-9,]+)\s*}}"
        md.inlinePatterns.register(CounterInlineProcessor(regex, md), "counter", 105)
