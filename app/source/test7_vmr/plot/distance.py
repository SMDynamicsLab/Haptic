import numpy as np


def distance(data):
    df = data.reset_index(drop=True)
    p1 = df.iloc[:-1]
    p2 = df.iloc[1:]
    p2 = p2.reset_index(drop=True)
    ds = p2 - p1
    d = np.sqrt(ds.x ** 2 + ds.y ** 2)
    return d.sum()


def total_distance(data):
    df = data.reset_index(drop=True)
    p1 = df.iloc[0]
    p2 = df.iloc[-1]
    ds = p2 - p1
    d = np.sqrt(ds.x ** 2 + ds.y ** 2)
    return d
