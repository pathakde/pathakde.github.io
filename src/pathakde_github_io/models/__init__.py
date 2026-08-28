from dataclasses import dataclass


@dataclass
class Figure:
    id: str
    url: str
    image_path: str


@dataclass
class FigureWithCaption:
    figure: Figure
    caption: str


@dataclass
class ArxivFigure:
    id: str
    content: str
    caption: str


@dataclass
class Publication:
    bibcode: str
    in_press: str
    in_review: str
    arxiv_html: str

    def published(self):
        return not self.in_press and not self.in_review


@dataclass
class PublicationWithAbstract:
    publication: Publication
    abstract: str
