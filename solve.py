import json
import os
import sys

import pandas as pd

from box_packing import *


def json_data_to_input_data(json_data):
    return [
        Pallet(
            json_data["large_object"]["length"],
            json_data["large_object"]["width"],
            json_data["large_object"]["height"],
        ),
        BoxList(
            [
                [
                    index + 1,
                    [
                        box["length"],
                        box["width"],
                        box["height"],
                    ],
                    box["quantity"],
                ]
                for index, box in enumerate(json_data["small_items"])
            ]
        ),
    ]


def pallet_summary(pallet):
    df = pd.DataFrame(
        {
            "Used Space": [pallet.filled_volume()],
            "Fraction of the total space used": [
                pallet.filled_volume() / pallet.total_volume()
            ],
            "Pallet total volume": [pallet.total_volume()],
            "Pallet length": [pallet.dimension[0]],
            "Pallet width": [pallet.dimension[1]],
            "Pallet height": [pallet.dimension[2]],
        }
    )
    print(df.transpose())
    return


def pallet_output(pallet, output_file_path):
    output = pallet.make_output()
    with open(output_file_path, "w") as file:
        json.dump(output, file, indent=2)
    return


if __name__ == "__main__":
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    output_path = os.path.dirname(output_file_path)
    os.makedirs(output_path, exist_ok=True)
    with open(input_file_path, "r") as file:
        json_data = json.load(file)
    pallet, box_list = json_data_to_input_data(json_data)
    pallet.fill(box_list)
    pallet_summary(pallet)
    pallet_output(pallet, output_file_path)
