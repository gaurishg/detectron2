from process_mydata import Data
import argparse
from typing import NamedTuple
from pathlib import Path
import json
import random


class ArgParserNamespace(NamedTuple):
    valsize: int
    filename: str


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--valsize", type=int, default=20)
    parser.add_argument("--filename", type=str)
    return parser


def remove_excess_annotations(data: Data):
    image_ids = set(im["id"] for im in data["images"])
    data["annotations"] = [anno for anno in data["annotations"] if anno["image_id"] in image_ids]


def main():
    args = get_parser().parse_args() # type: ArgParserNamespace
    print(args)
    valsize = args.valsize
    filename = args.filename
    filepath = Path(filename)

    data: Data = json.loads(filepath.read_text())
    images = data['images']
    n_images = len(images)
    random.shuffle(images)

    trainsize = 100 - valsize
    n_train_images = (n_images * trainsize) // 100
    train_images = images[:n_train_images]
    val_images = images[n_train_images:]

    train_data: Data = {
        "images": train_images,
        "categories": data["categories"],
        "annotations": data["annotations"],
        "info": data["info"]
    }

    val_data: Data = {
        "images": val_images,
        "categories": data["categories"],
        "annotations": data["annotations"],
        "info": data["info"]
    }

    remove_excess_annotations(train_data)
    remove_excess_annotations(val_data)

    train_path = filepath.parent / 'train.json'
    val_path = filepath.parent / 'val.json'
    
    with train_path.open('w') as f_handle:
        json.dump(train_data, f_handle, indent=4)
    
    with val_path.open('w') as f_handle:
        json.dump(val_data, f_handle, indent=4)


if __name__ == '__main__':
    main()