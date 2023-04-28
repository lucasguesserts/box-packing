import itertools

import numpy as np


class Box:
    def __init__(self, id, length, width, height):
        self.id = np.int_(id)
        if self.id <= 0:
            raise ValueError("Boxes Ids must be positive (neither null nor negative)")
        self.dimension = np.array([length, width, height], dtype=np.int_)
        self.volume = np.product(self.dimension)
        self.rotation = [
            Rotation(*p) for p in list(set(itertools.permutations(self.dimension, 3)))
        ]
        self.rotation = sorted(self.rotation, key=lambda r: r.area, reverse=True)
        return

    def __str__(self):
        return "Box({}_id, {}, {}, {})".format(self.id, *[d for d in self.dimension])


class Rotation:
    def __init__(self, x, y, z):
        self.dimension = np.array([x, y, z], dtype=np.int_)
        self.area = x * y
        self.volume = np.product(self.dimension)
        return

    def __str__(self):
        return "Rotation({}, {}, {})".format(*[d for d in self.dimension])

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return np.all(self.dimension == other.dimension)


class Pallet:
    def __init__(self, length, width, height):
        self.dimension = np.array([length, width, height], dtype=np.int_)
        self.space = np.zeros(self.dimension, dtype=np.int_)
        self.added_boxes = []
        return

    def add(self, box_id, rotation, coordinates):
        success = False
        if self._rotation_is_in_pallet(rotation, coordinates):
            rotation_space = self._rotation_space(rotation, coordinates)
            if self._is_space_empty(rotation_space):
                self.space[rotation_space] = box_id
                self.added_boxes.append([box_id, *rotation.dimension, *coordinates])
                success = True
        return success

    def filled_volume(self):
        return np.count_nonzero(self.space > 0)

    def total_volume(self):
        return np.product(self.dimension)

    def _rotation_space(self, rotation, coordinates):
        return (
            slice(coordinates[0], coordinates[0] + rotation.dimension[0]),
            slice(coordinates[1], coordinates[1] + rotation.dimension[1]),
            slice(coordinates[2], coordinates[2] + rotation.dimension[2]),
        )

    def _rotation_is_in_pallet(self, rotation, coordinates):
        """Constrain: box has to be within pallet's dimention"""
        return np.all((coordinates + rotation.dimension - self.dimension) <= 0)

    def _is_space_empty(self, rotation_space):
        return np.all(self.space[rotation_space] == 0)

    def fill(self, box_list):
        for x, y, z in [
            (x, y, z)
            for x in range(self.dimension[0])
            for y in range(self.dimension[1])
            for z in range(self.dimension[2])
        ]:
            if self.space[x, y, z] == 0:  # space available
                for idx in box_list.available_boxes():  # get a box type
                    for rotation in box_list.box(
                        idx
                    ).rotation:  # get a rotation of the box
                        if self.add(
                            box_list.box(idx).id, rotation, [x, y, z]
                        ):  # try to add the rotation at that space
                            box_list.reduce_counter(idx)
                            break
                    else:  # for loop
                        continue  # no rotation fits => go to next box
                    break  # a rotation was fit in the pallet => break the idx loop
        return


class BoxList:
    def __init__(self, box_list_initializer):
        self.listing = []
        for box_id, box_dimension, box_count in box_list_initializer:
            self.listing.append([Box(box_id, *box_dimension), box_count])
        self.listing = sorted(
            self.listing, key=lambda entry: entry[0].volume, reverse=True
        )  # big boxes first
        self.listing = np.array(self.listing)  # I can use numpy features
        return

    def box(self, idx):
        return self.listing[idx][0]

    def count(self, idx):
        return self.listing[idx][1]

    def available_boxes(self):
        availability_list = []
        for idx in range(len(self.listing)):
            if self.count(idx) > 0:
                availability_list.append(idx)
        return availability_list

    def reduce_counter(self, idx):
        if self.count(idx) == 0:
            raise ValueError("Attempting to use a box which is not available.")
        self.listing[idx][1] -= 1
        return

    def __str__(self):
        to_str = ""
        to_str += "[\n"
        for idx in range(len(self.listing)):
            to_str += "\t[ {}, {}_count ]\n".format(self.box(idx), self.count(idx))
        to_str += "]\n"
        return to_str
