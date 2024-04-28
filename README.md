# Flask-Website

[Main page](https://anonymousrand.xyz)

[Blog page](https://blog.anonymousrand.xyz) (don't click this one)

Huge thanks to [Miguel Grinberg's Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) and also [Noran Saber Abdelfattah's Flask blog guide](https://medium.com/@noransaber685/building-a-flask-blog-a-step-by-step-guide-for-beginners-8bffe925cd0e), otherwise this project would've taken longer to get going and would probably have *bad practice* scribbled all over it.

And thank you to GitHub for free image "backups" in my static folders <3

# Developer notes to compensate for possibly scuffed code

#### Adding new blogpages:
- Register new copy of `blogpage` blueprint with proper blog id/name in `app/__init__.py`
- Update `config.py`
- Update directory names in static paths

#### Adding new forms:
- Make sure that all POST forms should be Ajax using FormData and should handle the custom error(s) defined in `config.py`
  - Ref. `app/static/js/session_util.js`, `app/admin/static/admin/js/form_submit.js`, `app/blog/static/blog/blogpage/js/comments.js`
- Always add HTML classes `login-req-post` and `auth-true`/`auth-false` when needed

#### Updating HTML custom errors:
- Update `config.py`
- Update `app/routes.py` error handlers
- Update `app/static/js/handle_custom_errors.js`

# Blog writer notes

- Tables:
  - Use [Markdown tables](https://www.tablesgenerator.com/markdown_tables#) whenever possible, with "Compact mode" and "Line breaks as \<br\>" checked
  - Use [reStructuredText grid tables](https://tableconvert.com/restructuredtext-generator) with "Force separate lines" checked for features such as:
    - Merged cells
      - In order to merge cells, replace intermediate '|' characters generated by the website with a space (every line has to be the same number of chars long for reStructuredText grid tables!)
  - Syntax notes:
    - Insert any inline tag like `<span>` with attribute `data-col-width="[something]%"` inside any cell to control width for its column

- Other syntax:
  - Raw HTML can be put in Markdown and rendered, such as:
      - `<center></center>` for centering individual cells in a table
      - `<pre><code></code></pre>` for code blocks in a table
      - `<small></small>` for small text
  - `__[text]__` to underline
  - `~~[text]~~` to strikethrough
  - `\thm` and `\endthm` followed/preceded by a blank line respectively to highlight everything inside as a navy blue blockquote

- Other considerations:
  - Use `<br>` for line breaks that aren't new paragraphs and don't leave extra space, like between lines in a stanza

# Other useless notes
CSS property order (currently-used properties):
- "Specific":
  - `content`
  - `opacity`
  - `color`
  - `background-color`
  - `font-size`
  - `text-decoration`
  - Other specific ones like `overflow-x`
- "General":
  - `width`
  - `min-width`
  - `max-width`
  - `height`
  - `border`
  - `border-width`
  - `border-radius`
  - `margin`
    - `left`
    - `right`
    - `top`
    - `bottom`
  - `padding`
    - `left`
    - `right`
    - `top`
    - `bottom`
