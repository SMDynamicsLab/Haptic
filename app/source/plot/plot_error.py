import numpy as np
from numpy import trapz
import math
from scipy.spatial.transform import Rotation
from numpy.linalg import norm


def rotate_trial_data(trial_data, angle):
    theta = math.radians(angle)  # 0 es arriba en la sim
    axis = [0, 0, 1]  # z
    axis = axis / norm(axis)
    rot = Rotation.from_rotvec(theta * axis)
    trial_data['pos_rot'] = [rot.apply([x, y, z]) for x, y, z in zip(trial_data.x, trial_data.y, trial_data.z)]
    trial_data['x'] = [x for [x, y, z] in trial_data.pos_rot]
    trial_data['y'] = [y for [x, y, z] in trial_data.pos_rot]
    trial_data['z'] = [z for [x, y, z] in trial_data.pos_rot]
    trial_data.drop('pos_rot', axis=1, inplace=True)
    return trial_data


def calculate_error_area(trial_data, angle):
    trial_data = rotate_trial_data(trial_data, angle)
    x = [trial_data.iloc[0].x, trial_data.iloc[-1].x]
    y = [trial_data.iloc[0].y, trial_data.iloc[-1].y]
    coefficients = np.polyfit(x, y, 1)
    polynomial = np.poly1d(coefficients)
    error_curve = trial_data.y - polynomial(trial_data.x)
    area_error = trapz(error_curve, x=trial_data.x)
    area_error_abs = trapz(np.abs(error_curve), x=trial_data.x)
    return area_error, area_error_abs
