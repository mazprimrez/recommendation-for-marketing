import numpy as np

def get_likelihood(row, selected_product):
    score = list(map(row.get, selected_product))
    return np.round(np.mean(score) * 100.00, 4)