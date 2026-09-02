import nh3
from bs4 import BeautifulSoup
from coolname import generate

from pathakde_github_io.models import ArxivFigure


def parse_figure_html(html_content: str, arxiv_id: str) -> list[ArxivFigure]:
    soup = BeautifulSoup(html_content, "html.parser")
    figures = soup.find_all(name="figure")

    arxiv_figures: list[ArxivFigure] = []

    for figure in figures:
        figure_id = figure.get("id", "")
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
                    arxiv_anchor = soup.new_tag("a", href=f"#{figure_id}")
                    child.wrap(arxiv_anchor)
                else:
                    arxiv_anchor.append(child)

        # prepend a refs with /html/ so that they properly click out to arxiv
        for anchor in figure.find_all("a"):
            href = anchor.get("href")
            if href:
                if "://" not in href and not href.startswith("/"):
                    if href.startswith("#"):
                        anchor["href"] = f"/html/{arxiv_id}{href}"
                    else:
                        anchor["href"] = f"/html/{arxiv_id}/{href}"

        # prepend img srcs with /html/ so that they properly point out to arxiv
        for img in figure.find_all("img"):
            src = img.get("src")
            if src:
                if "://" not in src and not src.startswith("/"):
                    img["src"] = "/html/" + src

        # prepend object data with /html/ so that they properly point out to arxiv
        for obj in figure.find_all("object"):
            data = obj.get("data")
            if data:
                if "://" not in data and not data.startswith("/"):
                    obj["data"] = "/html/" + data

        # replace all math tags with a simpler span
        for math in figure.find_all("math"):
            alt_text = math.get("alttext")

            if alt_text:
                math.replace_with(soup.new_string(f"\( {alt_text} \)"))

        allowed_tags = set(nh3.ALLOWED_TAGS)
        allowed_tags.add("object")

        allowed_attributes = dict(nh3.ALLOWED_ATTRIBUTES)
        allowed_attributes["object"] = {"data", "type", "width", "height", "name", "class", "id", "style"}

        cleaned_figure = nh3.clean(
            str(figure),
            url_relative=("rewrite_with_base", "https://arxiv.org"),
            tags=allowed_tags,
            attributes=allowed_attributes,
        )

        cleaned_soup = BeautifulSoup(cleaned_figure, "html.parser")
        cleaned_figure_tag = cleaned_soup.find("figure")
        cleaned_content = cleaned_figure_tag.find("a", recursive=False)
        cleaned_caption = cleaned_figure_tag.find("figcaption", recursive=False)

        arxiv_figures.append(
            ArxivFigure(
                id=figure_id if figure_id else generate(4),
                content=str(cleaned_content) if cleaned_content else "",
                caption=cleaned_caption.decode_contents() if cleaned_caption else "",
            )
        )

    return arxiv_figures
