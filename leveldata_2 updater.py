import pickle
world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 1],
    [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 2, 2, 2, 0, 2, 2, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 0, 0, 7, 2, 0, 0, 3, 7, 0, 0, 1],
    [1, 1, 2, 4, 2, 1, 0, 2, 2, 2, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 2, 1],
    [1, 0, 0, 0, 0, 2, 2, 4, 2, 4, 2, 1, 1],
    [1, 2, 2, 2, 4, 1, 1, 5, 1, 5, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

with open("leveldata_2", "wb") as pickle_file:
    pickle.dump(world_data, pickle_file)