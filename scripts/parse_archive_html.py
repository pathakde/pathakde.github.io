from dataclasses import dataclass

import nh3
from bs4 import BeautifulSoup

# nh3 whitelist
# 1. Define complete MathML tags (Presentation & Container layouts)
MATHML_TAGS = {
    "annotation",
    "math",
    "merror",
    "mfrac",
    "mi",
    "mmultiscripts",
    "mn",
    "mo",
    "mover",
    "mpadded",
    "mphantom",
    "mroot",
    "mrow",
    "ms",
    "mspace",
    "msqrt",
    "mstyle",
    "msub",
    "msubsup",
    "msup",
    "mtable",
    "mtd",
    "mtext",
    "mtr",
    "munder",
    "munderover",
    "semantics",
}

# 2. Define global attributes safe across all MathML elements
MATHML_GLOBAL_ATTRIBUTES = {"alttext", "dir", "displaystyle", "id", "scriptlevel"}

# 3. Combine with nh3 defaults so standard HTML elements do not break
ALLOWED_TAGS = nh3.ALLOWED_TAGS | MATHML_TAGS

# Base dictionary containing default safe HTML attributes
ALLOWED_ATTRIBUTES = {**nh3.ALLOWED_ATTRIBUTES}

# 4. Map specific formatting attributes to MathML tags
mathml_attribute_mapping = {
    "annotation": {"encoding"},
    "math": {"display"},
    "mfrac": {"linethickness"},
    "mo": {
        "fence",
        "form",
        "largeop",
        "lspace",
        "maxsize",
        "minsize",
        "movablelimits",
        "rspace",
        "separator",
        "stretchy",
        "symmetric",
    },
    "mover": {"accent"},
    "mpadded": {"width", "height", "depth", "lspace", "voffset"},
    "mspace": {
        "width",
        "height",
        "depth",
    },
    "mtd": {
        "rowspan",
        "columnspan",
    },
    "mtr": {"rowalign", "columnalign"},
    "munder": {"accentunder"},
    "munderover": {"accent", "accentunder"},
}

# Populate final dictionary with both global and tag-specific attributes
for tag in MATHML_TAGS:
    specific_attrs = mathml_attribute_mapping.get(tag, set())
    # Merge global MathML attributes with the tag-specific ones
    ALLOWED_ATTRIBUTES[tag] = MATHML_GLOBAL_ATTRIBUTES | specific_attrs


@dataclass
class ArxivFigure:
    id: str
    content: str
    caption: str


def parse_figure_html(html_content: str, arxiv_id: str) -> list[ArxivFigure]:
    soup = BeautifulSoup(html_content, "html.parser")
    figures = soup.find_all(name="figure")

    arxiv_figures: list[ArxivFigure] = []

    for figure in figures:
        # find outer most figcaption (that's also not nested in another figure)
        fig_caption = figure.find("figcaption", recursive=False)
        if fig_caption and not fig_caption.text.startswith("Figure"):
            continue

        # Wrap non-caption contents in an anchor tag
        arxiv_anchor = None
        children = figure.find_all(recursive=False)
        for child in children:
            name = child.name
            if name != "figcaption":
                if arxiv_anchor is None:
                    arxiv_anchor = soup.new_tag(
                        "a", href=f"{arxiv_id}#{figure.get("id")}"
                    )
                    child.wrap(arxiv_anchor)
                else:
                    arxiv_anchor.append(child)

        # prepend a refs with /html/ so that they properly click out to arxiv
        for anchor in figure.find_all("a"):
            href = anchor.get("href")
            if href:
                if "://" not in href and not href.startswith("/"):
                    anchor["href"] = "/html/" + href

        # prepend img srcs with /html/ so that they properly point out to arxiv
        for img in figure.find_all("img"):
            src = img.get("src")
            if src:
                if "://" not in src and not src.startswith("/"):
                    img["src"] = "/html/" + src

        cleaned_figure = nh3.clean(
            str(figure),
            url_relative=("rewrite_with_base", "https://arxiv.org"),
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
        )

        cleaned_soup = BeautifulSoup(cleaned_figure, "html.parser")

        cleaned_figure_tag = cleaned_soup.find("figure")
        cleaned_content = cleaned_figure_tag.find("a", recursive=False)
        cleaned_caption = cleaned_figure_tag.find("figcaption", recursive=False)

        arxiv_figures.append(
            ArxivFigure(
                id=arxiv_id,
                content=str(cleaned_content) if cleaned_content else "",
                caption=str(cleaned_caption.unwrap()) if cleaned_caption else "",
            )
        )

    return arxiv_figures
