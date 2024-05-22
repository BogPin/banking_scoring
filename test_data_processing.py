import unittest
import pandas as pd
from data_processing import load_data, segment_data, check_column_matches, clean_data, normalize_criteria

class TestDataProcessing(unittest.TestCase):
    
    def test_load_data(self):
        df = load_data('sample_data.xlsx')
        self.assertIsInstance(df, pd.DataFrame)
    
    def test_segment_data(self):
        df = pd.DataFrame({
            'Place_of_definition': ['Вказує позичальник', 'параметри, повязані з виданим продуктом', 'інше']
        })
        conditions = (df['Place_of_definition'] == 'Вказує позичальник') | (df['Place_of_definition'] == 'параметри, повязані з виданим продуктом')
        segment = segment_data(df, conditions)
        self.assertEqual(len(segment), 2)
    
    def test_check_column_matches(self):
        segment = pd.DataFrame({'Field_in_data': ['col1', 'col2']})
        data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        matches = check_column_matches(segment, data)
        self.assertEqual(matches, [0, 1])
    
    def test_clean_data(self):
        segment = pd.DataFrame({'Field_in_data': ['col1', 'col2', 'col3']})
        data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]})
        columns_to_drop = ['col3']
        cleaned_segment, cleaned_data = clean_data(segment, data, columns_to_drop)
        self.assertNotIn('col3', cleaned_segment['Field_in_data'].values)
        self.assertNotIn('col3', cleaned_data.columns)
    
    def test_normalize_criteria(self):
        data = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        criteria = pd.DataFrame({'Field_in_data': ['col1', 'col2'], 'Minimax': ['min', 'max']})
        normalized_data = normalize_criteria(data, criteria)
        self.assertEqual(normalized_data.shape, (3, 2))

if __name__ == '__main__':
    unittest.main()
