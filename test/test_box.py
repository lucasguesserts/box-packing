import pytest
import numpy as np
from box_packing import *

@pytest.fixture(scope="module")
def value():
    return 1

@pytest.fixture(scope="module")
def dims():
    length = 1
    width = 2
    height = 3
    return length, width, height

def test_rotation(dims):
    rotation = Rotation(*dims)
    assert np.all( rotation.dimension == dims )
    assert rotation.area == 2
    assert rotation.volume == 6
    assert rotation == Rotation(*dims)
    return

def test_box(dims):
    id = 7
    box = Box(id, *dims)
    assert box.id == id
    assert np.all(box.rotation == [
        Rotation(3, 2, 1),
        Rotation(2, 3, 1),
        Rotation(1, 3, 2),
        Rotation(3, 1, 2),
        Rotation(1, 2, 3),
        Rotation(2, 1, 3),
    ])
    assert box.volume == 6
    return

def test_pallet_add_box_success():
    pallet_dims = [2, 3, 3]
    rotation_dims = [1, 2, 3]
    pallet = Pallet(*pallet_dims)
    assert pallet.filled_volume() == 0
    rotation = Rotation(*rotation_dims)
    box_id = 7
    location = np.array([0, 0, 0], dtype=np.int_)
    assert pallet.add(box_id, rotation, location)
    assert np.all( pallet.space[
            location[0]:(location[0]+rotation.dimension[0]),
            location[1]:(location[1]+rotation.dimension[1]),
            location[2]:(location[2]+rotation.dimension[2])
        ] == box_id)
    assert pallet.filled_volume() == 6
    assert pallet.total_volume() == 18
    assert np.all( pallet.added_boxes == [
        [box_id, *rotation.dimension, *location]
    ])
    return

def test_pallet_add_box_failure():
    pallet_dims = [2, 3, 3]
    rotation_dims = [1, 2, 4]
    pallet = Pallet(*pallet_dims)
    rotation = Rotation(*rotation_dims)
    box_id = 7
    location = [0, 0, 0]
    assert not pallet.add(box_id, rotation, location)
    assert np.all( pallet.space == 0 )
    assert pallet.filled_volume() == 0
    assert pallet.total_volume() == 18
    assert np.all( pallet.added_boxes == [] )
    return

def test_pallet_add_boxes_at_the_same_place():
    pallet_dims = [2, 3, 3]
    rotation_dims = [1, 2, 3]
    pallet = Pallet(*pallet_dims)
    rotation = Rotation(*rotation_dims)
    box_id = [7, 3, 4]
    location = [
        [0, 0, 0],
        [1, 0, 0]
    ]
    assert pallet.add(box_id[0], rotation, location[0])
    assert pallet.add(box_id[1], rotation, location[1])
    assert not pallet.add(box_id[2], rotation, [0,0,0])
    assert not pallet.add(box_id[2], rotation, [0,1,0])
    assert not pallet.add(box_id[2], rotation, [0,2,0])
    assert not pallet.add(box_id[2], rotation, [0,0,1])
    assert not pallet.add(box_id[2], rotation, [0,0,2])
    for i in range(2):
        assert np.all( pallet.space[
                location[i][0]:(location[i][0]+rotation.dimension[0]),
                location[i][1]:(location[i][1]+rotation.dimension[1]),
                location[i][2]:(location[i][2]+rotation.dimension[2])
            ] == box_id[i])
    assert pallet.filled_volume() == 12
    assert np.all( pallet.added_boxes == [
        [box_id[0], *rotation.dimension, *location[0]],
        [box_id[1], *rotation.dimension, *location[1]],
    ])
    return

def test_box_list_init():
    box_list = BoxList([
        [1, [1, 3, 4], 5], # V = 12
        [6, [4, 6, 2], 2], # V = 48
        [3, [7, 3, 5], 0], # V = 105
        [4, [2, 5, 9], 4], # V = 90
        [8, [6, 3, 1], 0], # V = 18
    ])
    # Check ordering
    ## 0
    assert box_list.box(0).id == 3
    assert np.all( box_list.box(0).dimension == [7, 3, 5] )
    ## 2
    assert box_list.box(2).id == 6
    assert np.all( box_list.box(2).dimension == [4, 6, 2] )
    # Available boxes
    assert box_list.available_boxes() == [1, 2, 4]
    # Reducing counter
    box_list.reduce_counter(2)
    box_list.reduce_counter(2)
    assert box_list.count(2) == 0
#   box_list =
#      [
#          [ Box(3_id, 7, 3, 5), 0_count ]
#          [ Box(4_id, 2, 5, 9), 4_count ]
#          [ Box(6_id, 4, 6, 2), 2_count ]
#          [ Box(8_id, 6, 3, 1), 0_count ]
#          [ Box(1_id, 1, 3, 4), 5_count ]
#      ]
    return

def test_fill_pallet_full_use_all_boxes():
    # One 4x4x4 box will be put in the beginning
    # and then all the other spaces available will be filled
    # with the 1x1x1 boxes.
    pallet = Pallet(5, 5, 5) # V = 125
    box_list = BoxList([
        [2, [1, 1, 1], 61], # V = 1
        [6, [4, 4, 4], 1], # V = 64
    ])
    pallet.fill(box_list)
    assert np.all( pallet.space[0:4,0:4,0:4] == 6)
    assert np.sum(pallet.space) == 6*4**3 + 2*(5**3-4**3)
    assert box_list.count(0) == 0
    assert box_list.count(1) == 0
    assert pallet.filled_volume() == 125
    assert pallet.total_volume() == 125
    assert np.all( pallet.added_boxes[:2] == [
        [6, *(4,4,4), *[0,0,0]],
        [2, *(1,1,1), *[0,0,4]],
    ])

def test_fill_pallet_full_dont_use_all_boxes():
    # One 4x4x4 box will be put in the beginning
    # and then all the other spaces available will be filled
    # with the 1x1x1 and 2x1x1 boxes.
    # All 2x1x1 boxes will be used.
    # Not all 1x1x1 boxes will be used.
    # The 3x2x1 and 2x2x1 boxes will not be used.
    pallet = Pallet(5, 5, 5) # V = 125
    box_list = BoxList([
        [2, [1, 1, 1], 100], # V = 1
        [6, [2, 1, 1], 8], # V = 2
        [3, [3, 2, 2], 4], # V = 6
        [7, [4, 4, 4], 2], # V = 64
    ])
    pallet.fill(box_list)
    assert np.all( pallet.space[0:4,0:4,0:4] == 7)
    assert np.all( pallet.space[0:2,4,0:2] == 6)
    assert np.all( pallet.space[0:2,0:2,4] == 6)
    assert np.all( pallet.space[np.invert(np.logical_or(pallet.space==7,pallet.space==6))] == 2 )
    assert np.sum(pallet.space) == 7*1*(4*4*4) + 6*8*(2*1*1) + 2*((5*5*5)-1*(4*4*4)-8*(2*1*1))*(1*1*1) # idx * count_in_pallet * volume
    assert box_list.count(0) == 1
    assert box_list.count(1) == 4
    assert box_list.count(2) == 0
    assert box_list.count(3) == 55
    assert pallet.filled_volume() == 125

def test_fill_pallet_full_dont_use_all_space():
    # One 4x4x4 box will be put in the beginning
    # and then all the other spaces available will be filled
    # with the 1x1x1 and 2x1x1 boxes.
    # All 2x1x1 boxes will be used.
    # Not all 1x1x1 boxes will be used.
    # The 3x2x1 and 2x2x1 boxes will not be used.
    pallet = Pallet(5, 5, 5) # V = 125
    box_list = BoxList([
        [2, [1, 1, 1], 10], # V = 1
        [3, [3, 2, 2], 4], # V = 6
        [7, [4, 4, 4], 2], # V = 64
    ])
    pallet.fill(box_list)
    assert np.all( pallet.space[0:4,0:4,0:4] == 7)
    assert np.all( pallet.space[np.invert(np.logical_or(pallet.space==7,pallet.space==2))] == 0 )
    assert np.sum(pallet.space) == 7*1*(4*4*4) + 2*10*(1*1*1) # idx * count_in_pallet * volume
    assert box_list.count(0) == 1
    assert box_list.count(1) == 4
    assert box_list.count(2) == 0
    assert pallet.filled_volume() == 1*(4*4*4) + 10*(1*1*1) # count_in_pallet * volume
