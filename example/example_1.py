import json
import os

import pandas as pd

from box_packing import *

OUTPUT_DIR = "results/"
TABLE_FILE_NAME = "best_solution_exercise_1_detailed.csv"
SUMMARY_FILE_NAME = "best_solution_exercise_1_summary.csv"
OUTPUT_FILE_NAME = "best_solution_exercise_1.json"

TABLE_FILE_PATH = os.path.join(OUTPUT_DIR, TABLE_FILE_NAME)
SUMMARY_FILE_PATH = os.path.join(OUTPUT_DIR, SUMMARY_FILE_NAME)
OUTPUT_FILE_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILE_NAME)


def main():
    possible_solutions = []
    for pallet_dimensions in itertools.permutations([18, 22, 19], 3):
        pallet = Pallet(*pallet_dimensions)
        box_list = BoxList(
            [
                [1, [1, 1, 1], 100],
                [2, [1, 4, 6], 2],
                [3, [5, 4, 3], 5],
                [4, [6, 1, 6], 3],
                [5, [1, 5, 3], 1],
                [6, [4, 5, 1], 6],
            ]
        )
        pallet.fill(box_list)
        possible_solutions.append([pallet, box_list])
    best_solution_summary(possible_solutions)
    return


def box_list_summary(box_list):
    print(" ")
    print("Box list summary:")
    print(box_list)
    return


def pallet_summary(pallet):
    print(" ")
    print("Pallet summary:")
    print("\tPallet dimension: {}".format(pallet.dimension))
    print(
        "\tUsed space: {:d} ({:3.2f} from a total of {:d})".format(
            pallet.filled_volume(),
            100 * pallet.filled_volume() / pallet.total_volume(),
            pallet.total_volume(),
        )
    )
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
    df.to_csv(SUMMARY_FILE_PATH, index=False)
    return


def pallet_addition_list(pallet):
    df = pd.DataFrame(
        data=pallet.added_boxes,
        columns=[
            "box id",
            "length",
            "width",
            "height",
            "position x",
            "position y",
            "position z",
        ],
    )
    df.to_csv(TABLE_FILE_PATH, index=False)
    return


def pallet_output(pallet):
    output = pallet.make_output()
    with open(OUTPUT_FILE_PATH, "w") as file:
        json.dump(output, file, indent=2)
    return


def best_solution_summary(possible_solutions):
    sorted(
        possible_solutions,
        key=(lambda a_solution: a_solution[0].filled_volume()),
        reverse=True,
    )
    print("\n\nBEST SOLUTION:")
    pallet, box_list = possible_solutions[0]
    box_list_summary(box_list)
    pallet_summary(pallet)
    pallet_addition_list(pallet)
    pallet_output(pallet)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    main()
