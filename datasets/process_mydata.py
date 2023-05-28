from typing import TypedDict, List, DefaultDict, NamedTuple
import argparse
from pathlib import Path
import json


class Image(TypedDict):
    width: int
    height: int
    id: int
    file_name: str


class Category(TypedDict):
    id: int
    name: str


class Annotation(TypedDict, total=False):
    id: int
    image_id: int
    category_id: int
    segmentation: List[List[float]]
    bbox: List[float]
    ignore: int
    iscrowd: int
    area: float


class Info(TypedDict):
    year: int
    version: str
    description: str
    contributor: str
    url: str
    date_created: str


class Data(TypedDict):
    images: List[Image]
    categories: List[Category]
    annotations: List[Annotation]
    info: Info


class ArgParserType(NamedTuple):
    filename: str
    image_start: int
    anno_start: int

def get_parser():
    parser = argparse.ArgumentParser(description="process the data made from label studio")
    parser.add_argument("--filename", help="path to config file")
    parser.add_argument("--image_start", type=int, help="image id to start")
    parser.add_argument("--anno_start", type=int)
    return parser


def main():
    args = get_parser().parse_args() # type: ArgParserType
    print(args)
    filename: str = args.filename
    filepath = Path(filename)
    image_start = args.image_start
    anno_start = args.anno_start

    data: Data = json.loads(filepath.read_text())
    old2new_image_id = DefaultDict[int, int]()
    old2new_cat_id = {4: 1, 5: 2, 6: 3}
    for im in data['images']:
        old2new_image_id[im["id"]] = image_start
        im['id'] = image_start
        image_start += 1
    data["categories"] = [
        {
            "id": 1,
            "name": "switch-left"
        },
        {
            "id": 2,
            "name": "switch-right"
        },
        {
            "id": 3,
            "name": "switch-unknown"
        }
    ]

    annotations: List[Annotation] = []
    anno_id = anno_start
    for anno in data["annotations"]:
        if anno["category_id"] in [4, 5, 6]:
            anno['id'] = anno_id
            anno_id += 1
            anno['category_id'] = old2new_cat_id[anno['category_id']]
            anno['image_id'] = old2new_image_id[anno["image_id"]]
            annotations.append(anno)
    data['annotations'] = annotations

    with filepath.open('w') as f_handle:
        json.dump(data, f_handle, indent=4)

if __name__ == '__main__':
    main()