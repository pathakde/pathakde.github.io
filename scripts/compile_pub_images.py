from dotenv import find_dotenv, load_dotenv


from loguru import logger

import frontmatter

import os
import requests
from pathlib import Path

from natsort import natsorted

import json

from dataclasses import dataclass

@dataclass
class Figure:
    url: str
    image_path: str


def get_figures(bibcode: str, api_key: str) -> list[Figure]:
    res = requests.get(
        f"https://api.adsabs.harvard.edu/v1/graphics/{bibcode}",
        headers={"accept": "application/json", "authorization": f"Bearer {api_key}"},
    )

    if res.ok:
        def get_highres_link(obj):
            figure = obj["images"][0]
            
            thumbnail = figure["thumbnail"]
            highres = figure["highres"] # link to astroexplorer

            highres_file = highres.split("/")[-1] + "_hr.jpg"
            highres_link = "/".join(thumbnail.split("/")[:-1]) + "/" + highres_file

            return Figure(url=highres, image_path=highres_link)

        figures = res.json()["figures"]
        return list(map(get_highres_link, figures))
    else:
        return res.text


def get_bibcodes(dir_path) -> list[str]:
    # for every file in _publications,
    # get bibcode from frontmatter
    bibcodes = []
    for file in dir_path.glob('*.md'):
        metadata = frontmatter.load(file).metadata
        bibcode = metadata.get("bibcode")
        if bibcode:
            bibcodes.append(bibcode)

    return bibcodes


def make_figures_dir(bibcode: str) -> str:
    SCRIPT_DIR = Path(__file__).resolve().parent
    figures_dir_path = (
        SCRIPT_DIR / ".." / "images" / "publications" / bibcode / "figures"
    )
    figures_dir_path.mkdir(parents=True, exist_ok=True)

    return figures_dir_path



def make_publications_data_dir(bibcode: str) -> str:
    SCRIPT_DIR = Path(__file__).resolve().parent
    dir_path = (
        SCRIPT_DIR / ".." / "_data" / "publications" / bibcode
    )
    dir_path.mkdir(parents=True, exist_ok=True)

    return dir_path


def get_publications_dir() -> str:
    SCRIPT_DIR = Path(__file__).resolve().parent
    publications_dir_path = (
        SCRIPT_DIR / ".." / "_publications"
    )

    return publications_dir_path


def download_graphic(link: str, dir_path):
    response = requests.get(link)

    save_path = dir_path / link.split("/")[-1]
    # Check if the download was successful before saving
    if response.ok:
        with open(save_path, "wb") as file:
            file.write(response.content)


def write_figures_json(figures: list[Figure], save_path):
    bad_links = []
    for figure in figures:
        link = figure.image_path
        response = requests.head(link, allow_redirects=True, timeout=5)
        if not response.ok:
            bad_links.append({
                "url": link,
            })
    
    if bad_links:
        return bad_links

    data = {
        "figures": list(
            map(
                lambda f: {
                    "url": f.url,
                    "image_path": f.image_path,
                    "caption": "",
                },
                natsorted(figures, key=lambda f: f.url),
            )
        )
    }

    with open(save_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def has_no_images(directory_path):
    # Define common image extensions (lowercase for normalization)
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    
    dir_path = Path(directory_path)
    
    # Iterate through all files in the directory
    for file_path in dir_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            return False  # Found an image, so it *does* have image files
            
    return True  # Iterated through all files and found no images


def main():
    if not find_dotenv():
        logger.error(".env file is missing :(")
        return
    load_dotenv()

    ADS_API_KEY = os.environ.get("ADS_API_KEY")
    DOWNLOAD_FIGURES = os.environ.get("DOWNLOAD_FIGURES").lower() == "true"
    if not ADS_API_KEY:
        logger.error("ADS_API_KEY is not set :(")
        return

    publications_dir = get_publications_dir()
    for bibcode in get_bibcodes(publications_dir):
        logger.debug("========")
        logger.debug(f"bibcode={bibcode}")

        figures = get_figures(bibcode, ADS_API_KEY)

        # Download figures
        figures_dir_path = make_figures_dir(bibcode)
        if DOWNLOAD_FIGURES and has_no_images(figures_dir_path):
            logger.debug("downloading figures...")

            for figure in figures:
                download_graphic(figure.image_path, figures_dir_path)

            logger.debug("downloading figures...done")

        # Write figures.json
        publications_data_dir = make_publications_data_dir(bibcode)
        figures_json_file_path = publications_data_dir / "figures.json"

        if figures and not figures_json_file_path.is_file():
            logger.debug("writing figures.json metadata...")

            bad_links = write_figures_json(figures, figures_json_file_path)
            if bad_links:
                logger.error("some links weren't retrievable: {bad_links}", bad_links=bad_links)

            logger.debug("writing figures.json metadata...done")

if __name__ == "__main__":
    main()
