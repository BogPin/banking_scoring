import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_data(file_path, parse_dates=None):
    """
    Load data from an Excel file.

    Parameters:
    file_path (str): Path to the Excel file.
    parse_dates (list): List of columns to parse as dates.

    Returns:
    pd.DataFrame: Loaded data.
    """
    logging.info(f"Loading data from {file_path}")
    return pd.read_excel(file_path, parse_dates=parse_dates)


def analyze_data_structure(df):
    """
    Print the structure and missing values of the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame to analyze.
    """
    logging.info("Analyzing data structure.")
    print('-------------  назви стовпців DataFrame  -----------')
    print(df.columns)
    print('---------  типи даних стовпців DataFrame  -----------')
    print(df.dtypes)
    print('---------  пропущені значення стовпців (суми)  ------')
    print(df.isnull().sum())


def segment_data(df, conditions):
    """
    Segment data based on given conditions.

    Parameters:
    df (pd.DataFrame): DataFrame to segment.
    conditions (pd.Series): Boolean conditions for segmentation.

    Returns:
    pd.DataFrame: Segmented data.
    """
    logging.info("Segmenting data.")
    segment = df[conditions]
    segment.index = range(len(segment))
    return segment


def check_column_matches(segment, data):
    """
    Check for column matches between segment and data.

    Parameters:
    segment (pd.DataFrame): Segment data.
    data (pd.DataFrame): Full data.

    Returns:
    list: List of matching column indices.
    """
    logging.info("Checking column matches.")
    segment_columns = segment['Field_in_data']
    is_subset = set(segment_columns).issubset(data.columns)
    print('УВАГА! сегмент columns за співпадінням:', 'Flag_True' if is_subset else 'Flag_False')
    
    matches = [i for i, col in enumerate(segment_columns) if col in data.columns]
    print('Індекси співпадінь', matches)
    return matches


def clean_data(segment, data, columns_to_drop):
    """
    Clean data by removing specified columns.

    Parameters:
    segment (pd.DataFrame): Segment data.
    data (pd.DataFrame): Full data.
    columns_to_drop (list): List of columns to drop.

    Returns:
    tuple: Cleaned segment and data.
    """
    logging.info("Cleaning data.")
    cleaned_segment = segment.loc[~segment['Field_in_data'].isin(columns_to_drop)]
    cleaned_segment.index = range(len(cleaned_segment))
    cleaned_data = data.drop(columns=columns_to_drop)
    cleaned_data.index = range(len(cleaned_data))
    return cleaned_segment, cleaned_data


def normalize_criteria(data, criteria, delta=0.3):
    """
    Normalize criteria based on given delta.

    Parameters:
    data (pd.DataFrame): Data to normalize.
    criteria (pd.DataFrame): Criteria for normalization.
    delta (float): Normalization delta.

    Returns:
    np.ndarray: Normalized data.
    """
    logging.info("Normalizing criteria.")
    m, n = data.shape
    normalized_data = np.zeros((m, n))
    for j in range(n):
        column = criteria['Field_in_data'][j]
        if criteria['Minimax'][j] == 'min':
            max_value = data[column].max() + 2 * delta
            normalized_data[:, j] = (delta + data[column]) / max_value
        else:
            min_value = data[column].max() + 2 * delta
            normalized_data[:, j] = 1 / (delta + data[column]) / min_value
    return normalized_data
