import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def calculate_scoring(normalized_data, n, num_persons):
    """
    Calculate integrated multi-criteria score.

    Parameters:
    normalized_data (np.ndarray): Normalized data.
    n (int): Number of criteria.
    num_persons (int): Number of persons.

    Returns:
    tuple: Integro scores, canvas, axis, figure, line.
    """
    logging.info("Calculating Voronin scoring.")
    k = min(num_persons, len(normalized_data))
    integro = np.zeros(k)
    scor = np.zeros(k)
    for i in range(k):
        integro[i] = sum((1 - normalized_data[i, j]) ** -1 for j in range(n))
        scor[i] = 1000  # threshold for credit decision
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.set_title('Integro_Scor')
    line1, = ax.plot(integro, label='Integro', picker=5)  # enable picking on the line
    line2, = ax.plot(scor, label='Scor', picker=5)  # enable picking on the line
    ax.set_xlabel('Клієнти')  # Додано підпис осі X
    ax.set_ylabel('Скорингова оцінка')  # Додано підпис осі Y
    ax.legend()
    canvas = FigureCanvas(fig)
    return integro, canvas, ax, fig, line1


def format_integro_text(integro_scores):
    """
    Format integro scores with line numbers.

    Parameters:
    integro_scores (np.ndarray): Integro scores.

    Returns:
    str: Formatted integro scores.
    """
    logging.info("Formatting integro scores.")
    lines = [f"{i+1}: {score:.18e}" for i, score in enumerate(integro_scores)]
    return "\n".join(lines)
