# Template files

The files in this directory are the Jinja 2 template files that implement the UI of the microbirding app. They can be categorized as:

* **Header and footer template files**, where the header contains the main navigation bar of the app.
* **Page template files for the separate pages** in the app. They include the header and footer templates and one or more of the HTMX-resource templates.  Those files are prefixed with `page-`.
* **HTMX-resource templates** for resources served as responses to user actions in HTMX controls. Those files are prefixed with `hx-`. These templates can be seen as the UI "components" of the app.

| Template file | Comment | Status |
| --- | --- | --- |
| head.html | The head element of all pages. | Done. |
| header.html | The header, with the navigation bar, for all pages. | Done. |
| footer.html | The footer for all pages. | Done. |
| page-observations.html | The main page. | Done. |
| page-maps.hmtl | The page with maps and birding locations. | Done. |
| page-about.html | The page with information on the purpose, background etc. of the app. | TBD. |
| page-changelog.html | The changelog page. | Done. |
| page-404.html | The 404 page. | Done. |
| page-design-system | A  sort of design page where I can experiment with layout and UI | Done. |
| hx-observations-list.html | The main observations list, used by page-observations.hmtl. | Done. |

We use Jinja2 **include** as well as **macro** and **import** directives to structure and organize the Jinja2 templates. We do not use **inheritance**.
