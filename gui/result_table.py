from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
)


class ResultTable(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.all_results = []

        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()

        filter_layout.addWidget(
            QLabel("Bereichsnummer:")
        )

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(
            "z. B. 3"
        )

        filter_layout.addWidget(
            self.filter_input
        )

        self.filter_button = QPushButton(
            "Filtern"
        )

        self.filter_button.clicked.connect(
            self.apply_filter
        )

        filter_layout.addWidget(
            self.filter_button
        )

        self.show_all_button = QPushButton(
            "Alle anzeigen"
        )

        self.show_all_button.clicked.connect(
            self.show_all
        )

        filter_layout.addWidget(
            self.show_all_button
        )

        layout.addLayout(filter_layout)

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(
            [
                "Bereich",
                "Gültige Pixel",
                "Grüne Pixel",
                "Grünanteil",
                "Nicht Grün",
            ]
        )

        layout.addWidget(
            self.table
        )

    def set_results(self, results):
        self.all_results = results

        self.display_results(
            results
        )

    def display_results(self, results):
        self.table.setRowCount(
            len(results)
        )

        for row, result in enumerate(results):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(result["region_id"])
                )
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(result["total_pixels"])
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(result["green_pixels"])
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    f"{result['green_percentage']:.2f} %"
                )
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    f"{result['non_green_percentage']:.2f} %"
                )
            )

        self.table.resizeColumnsToContents()

    def apply_filter(self):
        text = self.filter_input.text().strip()

        if not text:
            self.show_all()
            return

        try:
            region_id = int(text)
        except ValueError:
            return

        filtered_results = [
            result
            for result in self.all_results
            if result["region_id"] == region_id
        ]

        self.display_results(
            filtered_results
        )

    def show_all(self):
        self.filter_input.clear()

        self.display_results(
            self.all_results
        )