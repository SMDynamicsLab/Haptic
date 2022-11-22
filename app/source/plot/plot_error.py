import numpy as np
from numpy import trapz
import math
from scipy.spatial.transform import Rotation
from numpy.linalg import norm


def rotate_trial_data(trial_data, angle):
    if angle is 0:
        return trial_data
    elif angle is 180:
        trial_data['x'] = -trial_data['x']
        trial_data['y'] = -trial_data['y']
        return trial_data

    # Resto posicion del centro antes de rotarlo (alrededor del centro)
    center_position = trial_data.iloc[0][['x', 'y', 'z']]
    trial_data['x'] = trial_data['x'] - center_position['x']
    trial_data['y'] = trial_data['y'] - center_position['y']
    trial_data['z'] = trial_data['y'] - center_position['z']    
    # Rotacion
    theta = math.radians(angle)  # 0 es arriba en la sim
    axis = [0, 0, 1]  # z
    axis = axis / norm(axis)
    rot = Rotation.from_rotvec(theta * axis)
    trial_data['pos_rot'] = [rot.apply([x, y, z]) for x, y, z in zip(trial_data.x, trial_data.y, trial_data.z)]
    # Sumo el centro nuevamente
    trial_data['x'] = [x for [x, y, z] in trial_data.pos_rot]
    trial_data['y'] = [y for [x, y, z] in trial_data.pos_rot]
    trial_data['z'] = [z for [x, y, z] in trial_data.pos_rot]
    trial_data['x'] = trial_data['x'] + center_position['x']
    trial_data['y'] = trial_data['y'] + center_position['y'] 
    trial_data['z'] = trial_data['y'] + center_position['z']
    trial_data.drop('pos_rot', axis=1, inplace=True)
    return trial_data

import matplotlib.pyplot as plt
def calculate_error_area(trial_data, angle):
    data = trial_data.copy()
    data.sort_values(by=['timeMs'], inplace=True)
    data = rotate_trial_data(data, angle)
    x = [data.iloc[0].x, data.iloc[-1].x]
    y = [data.iloc[0].y, data.iloc[-1].y]
    coefficients = np.polyfit(x, y, 1)
    polynomial = np.poly1d(coefficients)
    error_curve = data.y - polynomial(data.x)
    area_error = trapz(error_curve, x=data.x)
    area_error_abs = trapz(np.abs(error_curve), x=data.x)
    if area_error_abs<0:
        raise Exception("area_error_abs<0")
    return area_error, area_error_abs
