import sys
import logging
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableView, QGridLayout, QTextEdit, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from data_processing import load_data, analyze_data_structure, segment_data, check_column_matches, clean_data, normalize_criteria
from scoring import calculate_scoring, format_integro_text


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MainWindow(QMainWindow):
    """
    Main application window for the scoring analysis tool.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """
        Initialize the user interface of the main window.
        """
        self.setWindowTitle('Скорінговий аналіз')
        self.setGeometry(100, 100, 1200, 800)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        input_layout = QHBoxLayout()
        
        self.num_persons_label = QLabel('Кількість осіб для перевірки:')
        input_layout.addWidget(self.num_persons_label)
        
        self.num_persons_input = QLineEdit(self)
        self.num_persons_input.textChanged.connect(self.update_graph_and_text)
        input_layout.addWidget(self.num_persons_input)
        
        self.load_data_button = QPushButton('Завантажити та проаналізувати дані', self)
        self.load_data_button.clicked.connect(self.load_and_analyze_data)
        input_layout.addWidget(self.load_data_button)
        
        self.info_button = QPushButton('?', self)
        self.info_button.clicked.connect(self.show_info)
        input_layout.addWidget(self.info_button)
        
        main_layout.addLayout(input_layout)
        
        grid_layout = QGridLayout()
        
        self.plot_label = QLabel('Графік інтегрованої оцінки:')
        grid_layout.addWidget(self.plot_label, 0, 0)
        self.plot_widget = QWidget(self)
        self.plot_layout = QVBoxLayout(self.plot_widget)
        self.canvas = None
        self.toolbar = None
        grid_layout.addWidget(self.plot_widget, 1, 0)
        
        self.sample_data_label = QLabel('Зразок даних:')
        grid_layout.addWidget(self.sample_data_label, 0, 1)
        self.sample_data_view = QTableView(self)
        grid_layout.addWidget(self.sample_data_view, 1, 1)
        
        self.data_description_label = QLabel('Опис даних:')
        grid_layout.addWidget(self.data_description_label, 2, 0)
        self.data_description_view = QTableView(self)
        grid_layout.addWidget(self.data_description_view, 3, 0)
        
        self.integro_text_label = QLabel('Інтегровані оцінки:')
        grid_layout.addWidget(self.integro_text_label, 2, 1)
        self.integro_text = QTextEdit(self)
        self.integro_text.setReadOnly(True)
        grid_layout.addWidget(self.integro_text, 3, 1)
        
        main_layout.addLayout(grid_layout)
        self.setCentralWidget(main_widget)
    
    def load_and_analyze_data(self):
        """
        Load and analyze data from Excel files.
        """
        logging.info("Loading and analyzing data.")
        self.sample_data = load_data('sample_data.xlsx', parse_dates=['birth_date'])
        self.data_description = load_data('data_description.xlsx')
        
        analyze_data_structure(self.sample_data)
        
        segment_conditions = (self.data_description['Place_of_definition'] == 'Вказує позичальник') | \
                             (self.data_description['Place_of_definition'] == 'параметри, повязані з виданим продуктом')
        self.client_bank_segment = segment_data(self.data_description, segment_conditions)
        
        self.column_matches = check_column_matches(self.client_bank_segment, self.sample_data)
        self.matching_segment = self.client_bank_segment.iloc[self.column_matches]
        
        columns_to_drop = [
            'fact_addr_start_date', 'position_id', 'employment_date',
            'has_prior_employment', 'prior_employment_start_date',
            'prior_employment_end_date', 'income_frequency_other'
        ]
        self.cleaned_segment, self.cleaned_data = clean_data(self.matching_segment, self.sample_data, columns_to_drop)
        
        self.cleaned_segment.to_excel('d_segment_data_description_cleaning.xlsx')
        self.cleaned_data.to_excel('d_segment_sample_cleaning.xlsx')
        
        self.display_table(self.sample_data, self.sample_data_view)
        self.display_table(self.data_description, self.data_description_view)
        
        self.update_graph_and_text()
    
    def display_table(self, data, view):
        """
        Display a DataFrame in a QTableView.
        """
        model = QStandardItemModel()
        for column in data.columns:
            model.setHorizontalHeaderItem(data.columns.get_loc(column), QStandardItem(column))
        
        for row in range(data.shape[0]):
            for column in range(data.shape[1]):
                item = QStandardItem(str(data.iloc[row, column]))
                model.setItem(row, column, item)
        
        view.setModel(model)
    
    def display_integro_text(self, integro_scores):
        """
        Display the formatted integro scores in the QTextEdit.
        """
        formatted_text = format_integro_text(integro_scores)
        self.integro_text.setPlainText(formatted_text)
    
    def plot_graph(self, num_persons):
        """
        Plot the scoring graph.
        """
        if not hasattr(self, 'cleaned_data'):
            return
        
        minimax_criteria = load_data('d_segment_data_description_cleaning_minimax.xlsx')
        valid_criteria = minimax_criteria[minimax_criteria['Minimax'].isin(['min', 'max'])]
        valid_criteria.index = range(len(valid_criteria))
        
        selected_columns = valid_criteria['Field_in_data'].tolist()
        selected_data = self.cleaned_data[selected_columns]
        
        selected_data.to_excel('d_segment_sample_minimax.xlsx')
        valid_criteria.to_excel('d_segment_data_description_minimax.xlsx')
        
        normalized_data = normalize_criteria(selected_data, valid_criteria)
        np.savetxt('d_segment_sample_minimax_Normal.txt', normalized_data)
        
        integro_scores, canvas, ax, fig, line1 = calculate_scoring(normalized_data, len(valid_criteria), num_persons)
        np.savetxt('Integro_Scor.txt', integro_scores)
        
        if self.canvas is not None:
            self.plot_layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.toolbar.deleteLater()
        
        self.canvas = canvas
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.canvas)
        
        self.annot = ax.annotate("", xy=(0,0), xytext=(20,20),
                                 textcoords="offset points",
                                 bbox=dict(boxstyle="round", fc="w"),
                                 arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        def update_annot(ind):
            x, y = line1.get_data()
            self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
            text = f"ID: {ind['ind'][0] + 1}\nScore: {y[ind["ind"][0]]:.18e}"
            self.annot.set_text(text)
            self.annot.get_bbox_patch().set_alpha(0.4)
        
        def hover(event):
            vis = self.annot.get_visible()
            if event.inaxes == ax:
                cont, ind = line1.contains(event)
                if cont:
                    update_annot(ind)
                    self.annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        self.annot.set_visible(False)
                        fig.canvas.draw_idle()
        
        fig.canvas.mpl_connect("motion_notify_event", hover)
        
        self.display_integro_text(integro_scores)
    
    def update_graph_and_text(self):
        """
        Update the graph and text when the number of persons changes.
        """
        num_persons_text = self.num_persons_input.text()
        if num_persons_text.isdigit():
            num_persons = int(num_persons_text)
            self.plot_graph(num_persons)

    def show_info(self):
        """
        Show information about the project, supervisor, and developer.
        """
        info_text = (
            "1. Тема.\n"
            "Програмна система банківського скорингу за методами машинного навчанням без вчителя.\n\n"
            "2. Науковий керівник.\n"
            "кандидат технічних наук, доцент, доцент кафедри Корочкін Олександр Володимирович\n\n"
            "3. Розробник.\n"
            "Студент групи ІП-04 Пінчук Богдан Денисович"
        )
        QMessageBox.information(self, "Інформація", info_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
