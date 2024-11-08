# Personal-Website

# Setup if it's ever needed

I hope I'm not reading this because I bricked a machine again.

1. Set up Docker, MySQL, and Nginx on host machine
    - MySQL data directory should be in the bind-mounted directory specified in [deployment/docker/compose.yaml](deployment/docker/compose.yaml)
        - Recover database data from backups
    - Make sure default key for SSH and for GitHub pushing has no passcode if planning to use automatic db/image backup scripts. No hack pls
2. `git clone`
    - Make sure all files and folders in the entire project are owned by the user that Docker runs its containers as (see [deployment/systemd-reference/personal-website.service](deployment/systemd-reference/personal-website.service))
3. Install packages:
    - Install Python modules from [requirements.txt](requirements.txt) by running `pip install -r requirements.txt` (ideally within a virtualenv)
    - Install JS modules from [app/static/package.json](app/static/package.json) by running `npm install` in the [app/static/](app/static/) directory
4. Add back gitignored files:
    - `.env`: randomly generated `SECRET_KEY` and SQLAlchemy `DATABASE_URL` for connecting to MySQL from host
        - `DATABASE_URL` should be something like `mysql+pymysql://[db username]:[db password]@[hostname]:[port]/[database name]?charset=utf8mb4`
    - `deployment/docker/flask/envs/.env`: same as `.env` but with `DATABASE_URL` modified to connect to the MySQL Docker container (i.e. the `hostname` part of the URL is the name of the MySQL container *service* in [deployment/docker/compose.yaml](deployment/docker/compose.yaml), in this case `mysql`)
    - `deployment/docker/mysql/envs/.mysqlenv`: nothing yet (no environment variables if bind-mounting existing MySQL data directory)
    - `deployment/backup-scripts/db_backup_config.sh`: set the variables referenced in [deployment/backup-scripts/db_backup.sh](deployment/backup-scripts/db_backup.sh)
    - `app/static/css/custom_bootstrap.css` and `app/static/css/custom_bootstrap.css.map`: run `npm compile_bootstrap` from within the [app/static/](app/static/) folder
5. Navigate to [deployment/docker/](deployment/docker/) and run `deploy.sh` (or use a `systemd` service, for example [deployment/systemd-reference/personal-website.service](deployment/systemd-reference/personal-website.service))

# Developer notes to compensate for possibly scuffed coding practices

### IMPORTANT:
- Always make sure [.gitignore](.gitignore) is up to date with the correct paths and items!
- Always make sure access control is correct (see overview below)!
- Always make sure [config.py](config.py) is updated and has the correct filename/path (some Python files import it directly as a module)!
- Always make sure backup scripts in [deployment/backup-scripts/](deployment/backup-scripts/) have the correct paths and configs!
- Always make sure this README is updated!
- Always make sure Cloudflare firewall rules etc. still use the right URLs!

### Deployment maintenance:
- Sync/keep up-to-date according to comments and common sense:
    - [deployment/docker/compose.yaml](deployment/docker/compose.yaml)
    - Dockerfiles
    - Docker entrypoint scripts
    - Docker environment variables
    - [deployment/backup-scripts/db_backup_config.sh](deployment/backup-scripts/db_backup_config.sh) configs (not commented; sync all of them!)
    - Backup scripts
    - `systemd` services
- To connect to the MySQL instance running in Docker from the host:
    - Make sure the MySQL port (default 3306) is exposed from Docker and there is a `.env` file on the host with `DATABASE_URL` pointing to `localhost`
    - Use `mysql --protocol=tcp` to connect so it doesn't try to use a Unix socket; make sure to use the MySQL user that has `%` as its host (because that means it can connect from any host, whereas `localhost` would mean that it can only connect from within the Docker container)
- To change [app/models.py](app/models.py):
    - Edit [app/models.py](app/models.py) on the host
        - IMPORTANT: if renaming columns, you will probably have to edit the Alembic script in [migrations/versions/](migrations/versions/) to use `alter_column()`! `existing_type` is a required argument; reference [migrations/versions/79665802aa08_rename_blogpage_title_and_subtitle_to_.py](migrations/versions/79665802aa08_rename_blogpage_title_and_subtitle_to_.py).
    - Run `flask db migrate` on the host in the Python venv; this requires MySQL connectivity from the host
    - Run `flask db upgrade` on the host in the Python venv or restart the Docker containers

### Access control notes:
- Currently based on the expectation that all endpoints are access-controlled server-side, thus it doesn't matter as much if client-side updates visuals etc. on session expiry in a timely manner. The admin controls can still be there if interacting with them all requires logging in on the server-side. This is good because my client-side is an absolute dumpster fire of vanilla JS and JQuery.

### Adding new blogpages:
- Add to database (reference current database entries)
    - Add a developer/backrooms blogpage too with its `blogpage_id` being the negative of the public one
    - `blogpage_id` is always an integer except for the commented cases in [config.py](config.py), where they must be strings to avoid confusion with negative values and list/dictionary accessing
- Update [config.py](config.py):
    - Update `BLOGPAGE_ID_TO_PATH` with the same paths that you gave the new blogpage and its developer blogpage in the database; this is used for blueprint initialization (we can't access database before app context is fully created)
    - Update `URLS_LOGIN_REQUIRED` with the backrooms blogpage
- Create new static directories for it in [app/blog/static/blogpage/](app/blog/static/blogpage/) from the [template](app/blog/static/blogpage/blogpage_template/), and update other static directory names if necessary
    - Remember that since HTML templates are the same for every blogpage, things like font or background image customizations must be done through static files like CSS, which are imported individually per blogpage
    - If overriding default background image, change `backgroundImgOverrideName` in a JS file belonging to this new blueprint
        - This is handled rather clumsily by [app/blog/static/blogpage/js/try_override_background_img.js](app/blog/static/blogpage/js/try_override_background_img.js) by updating `URL_backgroundImgOverride`, which is finally used by [app/static/js/set_background_img.js](app/static/js/set_background_img.js) to update the `CSSStyleSheet` `backgroundImgStyleSheet`

### Changing blogpage IDs/blogpage static paths:
- Change the static directories, obviously
- Update paths in [config.py](config.py)
- Update Markdown expansion/collapse regex in [app/models.py](app/models.py)
- Update image paths in [app/admin/routes.py](app/admin/routes.py). This is important to make sure we don't accidentally delete/move important files!
- Update static paths for all linked JS/CSS in templates
- Update image paths for all existing images in db

### Adding new forms:
- GET forms:
    - These should not modify server-side state!
    - Usage guidelines:
        - Do not implement a CSRF Token hidden field to avoid leaking token in the URL (per OWASP guidelines). This means that we shouldn't use the `boostrap_wtf.quick_form()` macro for GET forms!
    - Refer to [app/blog/static/blogpage/js/goto_page_form.js](app/blog/static/blogpage/js/goto_page_form.js) and its associated [app/blog/templates/blog/blogpage/index.html](app/blog/templates/blog/blogpage/index.html) for an example of a GET form
- POST forms:
    - All other forms
    - Usage guidelines:
        - Must be Ajax, using `fetchWrapper()` in [app/static/js/ajax_util.js](app/static/js/ajax_util.js) and sending FormData (since the CSRF error handling is designed only for FormData). See `doAjaxResponseBase()` in the same file for documentation on the basic, always-supported JSON keys that the backend can return.
    - Refer to [app/static/js/session_util.js](app/static/js/session_util.js), [app/admin/static/js/form_submit.js](app/admin/static/js/form_submit.js), and [app/blog/static/blogpage/js/comments.js](app/blog/static/blogpage/js/comments.js) for examples of POST forms
- Always add HTML classes `auth-true`/`auth-false` (for showing/hiding elements) when needed

### Updating HTML custom errors:
- Update [config.py](config.py)
- Update [app/routes.py](app/routes.py) error handlers if necessary
- Update `fetchWrapper()` in [app/static/js/ajax_util.js](app/static/js/ajax_util.js)

### Other notes:
- `url_for()` to a blueprint (trusted destination!) should always be used with `_external=True` in both HTML templates and Flask to simplify the cross-origin nature of having a blog subdomain
- Try not to modify any of the `forms.py`s, as some JS might rely on hardcoded values of the form fields. I don't do frontend, ok?

# Blog writer notes

### Markdown syntax and custom syntax:
- Make sure to check out `Python-Markdown` official extensions' [documentations](https://python-markdown.github.io/extensions/)
- Inline:
    - `__[text]__` to underline
    - `~~[text]~~` to strikethrough
    - `{{[section 1 change],[section 2 change],…}}` for a counter that increments each section by the specified amount, and displays as many sections as given (similar to LaTeX theorem counters)
- Blocks (all delimiters must be surrounded by a blank line on both sides; not allowed in comments due to potential bugs):
    - `\begin{[block type]}` and `end{[block type]}`, surrounded by a blank line on both sides, puts everything in between in the specified `[block type]`
    - Available `[block type]`s:
        - `captioned_figure`: a figure, usually but not necessarily an image, with a caption underneath
            - Requires nested `caption` block inside
        - `cited_blockquote`: a blockquote with a citation underneath
            - Requires nested `citation` block inside
        - `dropdown`: an expandable/collapsible dropdown
            - Alternative styles:
                - `exer`: exercise
                - `pf`: proof
            - All `[type]`s except `exer` and `pf` requires nested `summary` block inside specifying the preview text when the dropdown is collapsed (`pf` gets a default `summary` block)
        - `textbox`: a textbox (1-cell table)
            - Alternative styles:
                - `coro`: corollary
                - `defn`: definition
                - `prop`: proposition
                - `thm`: theorem
    - See docstrings in [app/markdown_extensions/custom_extensions.py](app/markdown_extensions/custom_extensions.py) for more detailed usage instructions
    - Not allowed in non-admin comments due to potential bugs and crashes and 500 Internal Server Errors
- Images:
    - Only give the filename for images in Markdown; the full path will be automatically expanded (won't work if you put in full path because I'm bad at regex!!!)

### Other syntax notes:
- Raw HTML (including with attributes!) will be rendered, which is useful for additional styling or in environments where Markdown equivalents may not always work (footnotes, tables, blockquotes etc.). Examples:
    - `<span></span>` with pretty much any custom CSS styling you want (or with existing styling classes, once CSP is able to block inline `style` attributes)
    - `<pre><code></code></pre>` with `<br>` newlines for multiline code blocks in a table, as raw newlines would interfere with the table syntax
    - `<small></small>` for small text
    - `<p></p>` for paragraphs and line breaks (note: not supported in footnotes; use `<br><br>` instead)
        - E.g. lists, which have had the space between it and the previous paragraph removed by default
    - `<br>` for line breaks that aren't new paragraphs and don't leave extra space, like between lines in a stanza, and `<br>` surrounded by two empty lines for more space than a normal paragraph, like between stanzas

### Tables:
- Uses [Markdown tables](https://www.tablesgenerator.com/markdown_tables#) with "Compact mode" and "Line breaks as \<br\>" checked
- For merged cells, use the [Attribute Lists](https://python-markdown.github.io/extensions/attr_list/) extension to set `colspan`. To keep valid table syntax, put `<span></span> {: hidden }` in cells that have been merged into other ones.

# Cookie explanation from empirical observations and devtools

Comparing Flask's built-in session cookie with `PERMANENT_SESSION_LIFETIME` config vs. Flask-Login's remember me cookie with `REMEMBER_COOKIE_DURATION` config (this website currently uses the first row for no persistent cookies):

|  | Session cookie stored in: | Remember cookie stored in: | `PERMANENT_SESSION_LIFETIME` effect on session cookie | `REMEMBER_COOKIE_DURATION` effect on remember cookie | User experience when `PERMANENT_SESSION_LIFETIME` reached | User experience when `REMEMBER_COOKIE_DURATION` reached |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `session.permanent=False, remember=False` | Memory (non-persistent) | - | [Invalidated by Flask](https://stackoverflow.com/a/55055558) ([docs](https://flask.palletsprojects.com/en/3.0.x/config/#PERMANENT_SESSION_LIFETIME)) | - | Logged out | - |
| `session.permanent=True, remember=False` | Disk (persistent) | - | Expires & is deleted | - | Logged out | - |
| `session.permanent=False, remember=True` | Memory (non-persistent) | Disk (persistent) | Invalidated by Flask | Expires & is deleted | Logged out | Logged out if browser closed |
| `session.permanent=True, remember=True` | Disk (persistent) | Disk (persistent) | Expires & is deleted | Expires & is deleted | Logged out | Logged out if browser closed |
