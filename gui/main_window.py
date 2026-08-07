from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QSplitter,
)
from gui.image_view import ImageView
from analysis.analyzer import ImageAnalyzer
from gui.result_table import ResultTable
from gui.analysis_view import AnalysisView
from export.image_export import save_analysis_image
from export.table_export import save_results

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.current_image_path = None

        self.setWindowTitle("Image Analyzer")
        self.resize(1400, 900)

        self.create_menu()
        self.create_interface()

        self.statusBar().showMessage("Bereit")


        self.analysis_results = []

        self.analysis_image = None
        self.green_filter_mode = "medium"

    def create_menu(self):

        menu_bar = self.menuBar()

        # DATEI
        file_menu = menu_bar.addMenu("Datei")

        open_action = QAction("Bild öffnen", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)

        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # BEREICHE
        region_menu = menu_bar.addMenu("Bereiche")

        new_region_action = QAction(
            "Neuen Bereich erstellen",
            self
        )
        new_region_action.triggered.connect(
            self.start_region_drawing
        )

        region_menu.addAction(new_region_action)

        # DEAD ZONES
        deadzone_menu = menu_bar.addMenu("Dead Zones")

        new_deadzone_action = QAction(
            "Neue Dead Zone erstellen",
            self
        )
        new_deadzone_action.triggered.connect(
            self.start_deadzone_drawing
        )

        deadzone_menu.addAction(new_deadzone_action)

        # ANALYSE
        analysis_menu = menu_bar.addMenu("Analyse")
        # -----------------------------------------
        # Grünfilter auswählen
        # -----------------------------------------

        filter_group = QActionGroup(self)
        filter_group.setExclusive(True)

        self.light_filter_action = QAction(
            "Grünfilter: Leicht",
            self
        )

        self.light_filter_action.setCheckable(True)

        self.medium_filter_action = QAction(
            "Grünfilter: Mittel",
            self
        )

        self.medium_filter_action.setCheckable(True)

        filter_group.addAction(
            self.light_filter_action
        )

        filter_group.addAction(
            self.medium_filter_action
        )

        # Standard = Mittel
        self.medium_filter_action.setChecked(True)

        self.light_filter_action.triggered.connect(
            lambda: self.set_green_filter("light")
        )

        self.medium_filter_action.triggered.connect(
            lambda: self.set_green_filter("medium")
        )

        analysis_menu.addAction(
            self.light_filter_action
        )

        analysis_menu.addAction(
            self.medium_filter_action
        )

        analysis_menu.addSeparator()

        analyze_action = QAction(
            "Analyse starten",
            self
        )

        analyze_action.triggered.connect(
            self.start_analysis
        )

        analysis_menu.addAction(analyze_action)

        # EXPORT
        export_menu = menu_bar.addMenu("Export")

        export_image_action = QAction(
            "Analysebild speichern",
            self
        )

        export_table_action = QAction(
            "Tabelle exportieren",
            self
        )

        export_menu.addAction(export_image_action)
        export_menu.addAction(export_table_action)

        show_analysis_image_action = QAction(
            "Analysebild anzeigen",
            self
        )

        show_analysis_image_action.triggered.connect(
            self.show_analysis_image
        )

        analysis_menu.addAction(
            show_analysis_image_action
        )
        export_image_action.triggered.connect(
            self.export_analysis_image
        )

        export_table_action.triggered.connect(
            self.export_results_table
        )

    def create_interface(self):

        central_widget = QWidget()

        main_layout = QVBoxLayout(
            central_widget
        )

        # =========================================
        # Vertikaler Haupt-Splitter
        #
        # oben: Bilder
        # unten: Tabelle
        # =========================================

        vertical_splitter = QSplitter(
            Qt.Orientation.Vertical
        )

        # =========================================
        # Horizontaler Splitter für beide Bilder
        # =========================================

        image_splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        # -----------------------------------------
        # ORIGINALBILD
        # -----------------------------------------

        original_container = QWidget()

        original_layout = QVBoxLayout(
            original_container
        )

        original_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        original_label = QLabel(
            "Originalbild"
        )

        original_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        original_layout.addWidget(
            original_label
        )

        self.image_view = ImageView()

        self.image_view.region_created.connect(
            self.on_region_created
        )

        original_layout.addWidget(
            self.image_view
        )

        # -----------------------------------------
        # ANALYSEBILD
        # -----------------------------------------

        analysis_container = QWidget()

        analysis_layout = QVBoxLayout(
            analysis_container
        )

        analysis_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        analysis_label = QLabel(
            "Analysebild"
        )

        analysis_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        analysis_layout.addWidget(
            analysis_label
        )

        self.analysis_view = AnalysisView()

        analysis_layout.addWidget(
            self.analysis_view
        )

        # -----------------------------------------
        # Beide Seiten hinzufügen
        # -----------------------------------------

        image_splitter.addWidget(
            original_container
        )

        image_splitter.addWidget(
            analysis_container
        )

        image_splitter.setStretchFactor(
            0,
            1
        )

        image_splitter.setStretchFactor(
            1,
            1
        )

        # =========================================
        # Ergebnistabelle
        # =========================================

        self.result_table = ResultTable()

        vertical_splitter.addWidget(
            image_splitter
        )

        vertical_splitter.addWidget(
            self.result_table
        )

        vertical_splitter.setStretchFactor(
            0,
            4
        )

        vertical_splitter.setStretchFactor(
            1,
            1
        )

        main_layout.addWidget(
            vertical_splitter
        )

        self.setCentralWidget(
            central_widget
        )

    def open_image(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Bild auswählen",
            "",
            "Bilder (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )

        if not file_path:
            return

        self.current_image_path = file_path

        success = self.image_view.load_image(file_path)

        if not success:
            QMessageBox.critical(
                self,
                "Fehler",
                "Das Bild konnte nicht geladen werden."
            )

            return

        self.statusBar().showMessage(
            "Bild erfolgreich geladen."
        )

        self.analysis_image = None
        self.analysis_results = []

        self.analysis_view.clear_image()

        self.result_table.set_results([])

    def start_analysis(self):

        if self.current_image_path is None:
            QMessageBox.warning(
                self,
                "Kein Bild",
                "Bitte zuerst ein Bild öffnen."
            )

            return

        if not self.image_view.regions:
            QMessageBox.warning(
                self,
                "Keine Bereiche",
                "Bitte zuerst mindestens einen Bereich erstellen."
            )

            return

        try:

            analyzer = ImageAnalyzer(
                self.current_image_path,
                self.green_filter_mode
            )

            results = (
                analyzer.analyze_all_regions(
                    self.image_view.regions
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Analysefehler",
                str(error)
            )

            return

        self.result_table.set_results(
            results
        )

        self.analysis_results = results

        self.analysis_image = analyzer.create_analysis_image(
            self.image_view.regions
        )
        self.analysis_view.show_cv_image(
            self.analysis_image
        )
        print()
        print("=" * 60)
        print("GRÜNANALYSE")
        print("=" * 60)

        for result in results:
            print()
            print(
                f"Bereich {result['region_id']}"
            )

            print(
                f"Gültige Pixel: "
                f"{result['total_pixels']}"
            )

            print(
                f"Grüne Pixel: "
                f"{result['green_pixels']}"
            )

            print(
                f"Grünanteil: "
                f"{result['green_percentage']:.2f} %"
            )

            print(
                f"Nicht Grün: "
                f"{result['non_green_percentage']:.2f} %"
            )

        print()
        print("=" * 60)

        self.statusBar().showMessage(
            f"Analyse abgeschlossen: "
            f"{len(results)} Bereiche ausgewertet."
        )

    def start_region_drawing(self):
        if self.current_image_path is None:
            QMessageBox.warning(
                self,
                "Kein Bild",
                "Bitte zuerst ein Bild öffnen."
            )
            return

        success = self.image_view.set_mode_draw_region()

        if success:
            self.statusBar().showMessage(
                "Bereich zeichnen: Punkte setzen, Doppelklick zum Abschließen, ESC zum Abbrechen."
            )

    def on_region_created(self, region):
        self.statusBar().showMessage(
            f"Bereich {region.region_id} wurde erstellt."
        )

    def start_deadzone_drawing(self):
        if self.current_image_path is None:
            QMessageBox.warning(
                self,
                "Kein Bild",
                "Bitte zuerst ein Bild öffnen."
            )
            return

        if not self.image_view.regions:
            QMessageBox.warning(
                self,
                "Keine Bereiche",
                "Bitte zuerst mindestens einen Bereich erstellen."
            )
            return

        region_id, ok = QInputDialog.getInt(
            self,
            "Bereich auswählen",
            "Für welchen Bereich soll die Dead Zone erstellt werden?",
            1,
            1,
            999999,
            1
        )

        if not ok:
            return

        success = self.image_view.select_region(
            region_id
        )

        if not success:
            QMessageBox.warning(
                self,
                "Bereich nicht gefunden",
                f"Bereich {region_id} existiert nicht."
            )
            return

        success = self.image_view.set_mode_draw_deadzone()

        if not success:
            QMessageBox.warning(
                self,
                "Dead Zone",
                "Die Dead Zone konnte nicht gestartet werden."
            )
            return

        self.statusBar().showMessage(
            f"Dead Zone für Bereich {region_id}: "
            "Punkte setzen, Doppelklick zum Abschließen."
        )

    def open_color_dialog(self):
        dialog = ColorDialog(self)

        if dialog.exec():
            self.color_definitions = (
                dialog.get_colors()
            )

            if not self.color_definitions:
                self.statusBar().showMessage(
                    "Keine Farben aktiviert."
                )
                return

            names = [
                color.name
                for color in self.color_definitions
            ]

            self.statusBar().showMessage(
                "Farben festgelegt: "
                + ", ".join(names)
            )

    def show_analysis_image(self):
        if self.analysis_image is None:
            QMessageBox.warning(
                self,
                "Kein Analysebild",
                "Bitte zuerst eine Analyse starten."
            )
            return

        self.image_view.show_cv_image(
            self.analysis_image
        )

        self.statusBar().showMessage(
            "Analysebild wird angezeigt."
        )

    def set_green_filter(self, mode):

        self.green_filter_mode = mode

        if mode == "light":

            self.statusBar().showMessage(
                "Grünfilter: Leicht"
            )

        elif mode == "medium":

            self.statusBar().showMessage(
                "Grünfilter: Mittel"
            )

    def export_analysis_image(self):

        if self.analysis_image is None:
            QMessageBox.warning(
                self,
                "Kein Analysebild",
                "Bitte zuerst eine Analyse durchführen."
            )

            return

        file_path, selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                "Analysebild speichern",
                "Analysebild.png",
                (
                    "PNG-Bild (*.png);;"
                    "JPEG-Bild (*.jpg *.jpeg)"
                )
            )
        )

        if not file_path:
            return

        # Falls der Benutzer keine Endung eingibt
        if not (
                file_path.lower().endswith(".png")
                or file_path.lower().endswith(".jpg")
                or file_path.lower().endswith(".jpeg")
        ):

            if "JPEG" in selected_filter:
                file_path += ".jpg"

            else:
                file_path += ".png"

        try:

            save_analysis_image(
                self.analysis_image,
                file_path
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Exportfehler",
                str(error)
            )

            return

        QMessageBox.information(
            self,
            "Export abgeschlossen",
            (
                "Das Analysebild wurde "
                "erfolgreich gespeichert."
            )
        )

        self.statusBar().showMessage(
            f"Analysebild gespeichert: {file_path}"
        )

    def export_results_table(self):

        if not self.analysis_results:
            QMessageBox.warning(
                self,
                "Keine Ergebnisse",
                "Bitte zuerst eine Analyse durchführen."
            )

            return

        file_path, selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                "Ergebnistabelle speichern",
                "Gruenanalyse.xlsx",
                (
                    "Excel-Datei (*.xlsx);;"
                    "CSV-Datei (*.csv)"
                )
            )
        )

        if not file_path:
            return

        # Falls keine Dateiendung angegeben wurde
        if not (
                file_path.lower().endswith(".xlsx")
                or file_path.lower().endswith(".csv")
        ):

            if "CSV" in selected_filter:
                file_path += ".csv"

            else:
                file_path += ".xlsx"

        try:

            save_results(
                self.analysis_results,
                file_path
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Exportfehler",
                str(error)
            )

            return

        QMessageBox.information(
            self,
            "Export abgeschlossen",
            (
                "Die Ergebnistabelle wurde "
                "erfolgreich gespeichert."
            )
        )

        self.statusBar().showMessage(
            f"Tabelle gespeichert: {file_path}"
        )