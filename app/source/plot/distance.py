import numpy as np


def distance(data):
    df = data.reset_index(drop=True)
    p1 = df.iloc[:-1][['x','y']]
    p2 = df.iloc[1:][['x','y']]
    p2 = p2.reset_index(drop=True)
    ds = p2 - p1
    d = np.sqrt(ds.x ** 2 + ds.y ** 2)
    return d.sum()

def distance_vect(data):
    df = data.reset_index(drop=True)
    p1 = df.iloc[:-1][['x','y']]
    p2 = df.iloc[1:][['x','y']]
    p2 = p2.reset_index(drop=True)
    ds = p2 - p1  
    return ds  

def total_distance(data):
    df = data.reset_index(drop=True)
    p1 = df.iloc[0][['x','y']]
    p2 = df.iloc[-1][['x','y']]
    ds = p2 - p1
    d = np.sqrt(ds.x ** 2 + ds.y ** 2)
    return d
