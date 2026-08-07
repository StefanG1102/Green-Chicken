import cv2
import numpy as np


class ImageAnalyzer:
    # =========================================================
    # GRÜNFILTER-PROFILE
    # =========================================================
    #
    # light:
    # Erkennt breitere Grüntöne.
    #
    # medium:
    # Etwas strenger und reduziert Fehlklassifikationen.
    # =========================================================

    GREEN_FILTERS = {
        "light": {
            "h_min": 25,
            "h_max": 95,
            "s_min": 35,
            "v_min": 20,
        },

        "medium": {
            "h_min": 30,
            "h_max": 85,
            "s_min": 55,
            "v_min": 30,
        },
    }

    # =========================================================
    # INITIALISIERUNG
    # =========================================================

    def __init__(self, image_path, filter_mode="medium"):
        self.image_path = image_path
        self.filter_mode = filter_mode

        self.image = cv2.imread(image_path)

        if self.image is None:
            raise ValueError(
                f"Bild konnte nicht geladen werden: {image_path}"
            )

        self.hsv_image = cv2.cvtColor(
            self.image,
            cv2.COLOR_BGR2HSV
        )

        # Falls ein ungültiger Filter übergeben wurde,
        # verwenden wir automatisch "medium".
        if self.filter_mode not in self.GREEN_FILTERS:
            self.filter_mode = "medium"

        self.green_filter = self.GREEN_FILTERS[
            self.filter_mode
        ]

    # =========================================================
    # ALLE BEREICHE ANALYSIEREN
    # =========================================================

    def analyze_all_regions(self, regions):
        results = []

        for region in regions:
            result = self.analyze_region(region)
            results.append(result)

        return results

    # =========================================================
    # EINEN BEREICH ANALYSIEREN
    # =========================================================

    def analyze_region(self, region):
        height, width = self.image.shape[:2]

        # -----------------------------------------------------
        # Bereichsmaske erzeugen
        # -----------------------------------------------------

        region_mask = np.zeros(
            (height, width),
            dtype=np.uint8
        )

        if len(region.points) < 3:
            return self.empty_result(region.region_id)

        polygon = np.array(
            region.points,
            dtype=np.int32
        )

        cv2.fillPoly(
            region_mask,
            [polygon],
            255
        )

        # -----------------------------------------------------
        # Dead Zones aus Bereich entfernen
        # -----------------------------------------------------

        for dead_zone in region.dead_zones:
            if len(dead_zone) < 3:
                continue

            dead_polygon = np.array(
                dead_zone,
                dtype=np.int32
            )

            cv2.fillPoly(
                region_mask,
                [dead_polygon],
                0
            )

        # -----------------------------------------------------
        # Gültige Pixel bestimmen
        # -----------------------------------------------------

        valid_mask = region_mask > 0

        total_pixels = int(
            np.count_nonzero(valid_mask)
        )

        if total_pixels == 0:
            return self.empty_result(
                region.region_id
            )

        # -----------------------------------------------------
        # Grünmaske erstellen
        # -----------------------------------------------------

        green_mask = self.create_green_mask()

        # -----------------------------------------------------
        # Nur grüne Pixel innerhalb des Bereiches
        # -----------------------------------------------------

        green_inside_region = (
            valid_mask
            & (green_mask > 0)
        )

        green_pixels = int(
            np.count_nonzero(
                green_inside_region
            )
        )

        # -----------------------------------------------------
        # Nicht-grüne Pixel
        # -----------------------------------------------------

        non_green_pixels = (
            total_pixels
            - green_pixels
        )

        # -----------------------------------------------------
        # Prozentwerte
        # -----------------------------------------------------

        green_percentage = (
            green_pixels
            / total_pixels
            * 100.0
        )

        non_green_percentage = (
            non_green_pixels
            / total_pixels
            * 100.0
        )

        # -----------------------------------------------------
        # Ergebnis
        # -----------------------------------------------------

        return {
            "region_id": region.region_id,
            "total_pixels": total_pixels,
            "green_pixels": green_pixels,
            "non_green_pixels": non_green_pixels,
            "green_percentage": green_percentage,
            "non_green_percentage": non_green_percentage,
            "filter_mode": self.filter_mode,
        }

    # =========================================================
    # LEERES ERGEBNIS
    # =========================================================

    def empty_result(self, region_id):
        return {
            "region_id": region_id,
            "total_pixels": 0,
            "green_pixels": 0,
            "non_green_pixels": 0,
            "green_percentage": 0.0,
            "non_green_percentage": 0.0,
            "filter_mode": self.filter_mode,
        }

    # =========================================================
    # GRÜNMASKE ERZEUGEN
    # =========================================================

    def create_green_mask(self):
        h_min = self.green_filter["h_min"]
        h_max = self.green_filter["h_max"]
        s_min = self.green_filter["s_min"]
        v_min = self.green_filter["v_min"]

        lower_green = np.array(
            [
                h_min,
                s_min,
                v_min,
            ],
            dtype=np.uint8
        )

        upper_green = np.array(
            [
                h_max,
                255,
                255,
            ],
            dtype=np.uint8
        )

        green_mask = cv2.inRange(
            self.hsv_image,
            lower_green,
            upper_green
        )

        return green_mask

    # =========================================================
    # ANALYSEBILD ERZEUGEN
    # =========================================================

    def create_analysis_image(self, regions):
        # Komplett schwarzes Ergebnisbild
        result_image = np.zeros_like(
            self.image
        )

        # Grünmaske einmal berechnen
        green_mask = self.create_green_mask()

        for region in regions:
            if len(region.points) < 3:
                continue

            # -------------------------------------------------
            # Bereichsmaske
            # -------------------------------------------------

            region_mask = np.zeros(
                self.image.shape[:2],
                dtype=np.uint8
            )

            polygon = np.array(
                region.points,
                dtype=np.int32
            )

            cv2.fillPoly(
                region_mask,
                [polygon],
                255
            )

            # -------------------------------------------------
            # Dead Zones entfernen
            # -------------------------------------------------

            for dead_zone in region.dead_zones:
                if len(dead_zone) < 3:
                    continue

                dead_polygon = np.array(
                    dead_zone,
                    dtype=np.int32
                )

                cv2.fillPoly(
                    region_mask,
                    [dead_polygon],
                    0
                )

            # -------------------------------------------------
            # Gültige Fläche
            # -------------------------------------------------

            valid_mask = region_mask > 0

            # -------------------------------------------------
            # Grüne Pixel innerhalb des Bereiches
            # -------------------------------------------------

            green_inside = (
                valid_mask
                & (green_mask > 0)
            )

            # OpenCV verwendet BGR
            # Reines Grün = (0, 255, 0)
            result_image[
                green_inside
            ] = (0, 255, 0)

            # -------------------------------------------------
            # Bereichsgrenze weiß zeichnen
            # -------------------------------------------------

            cv2.polylines(
                result_image,
                [polygon],
                True,
                (255, 255, 255),
                2
            )

            # -------------------------------------------------
            # Dead-Zone-Grenzen zeichnen
            # -------------------------------------------------

            for dead_zone in region.dead_zones:
                if len(dead_zone) < 3:
                    continue

                dead_polygon = np.array(
                    dead_zone,
                    dtype=np.int32
                )

                cv2.polylines(
                    result_image,
                    [dead_polygon],
                    True,
                    (100, 100, 100),
                    1
                )

            # -------------------------------------------------
            # Bereichsnummer bestimmen
            # -------------------------------------------------

            x_values = [
                point[0]
                for point in region.points
            ]

            y_values = [
                point[1]
                for point in region.points
            ]

            center_x = int(
                sum(x_values)
                / len(x_values)
            )

            center_y = int(
                sum(y_values)
                / len(y_values)
            )

            # -------------------------------------------------
            # Bereichsnummer groß und lila anzeigen
            # -------------------------------------------------

            text = str(region.region_id)

            font = cv2.FONT_HERSHEY_SIMPLEX

            font_scale = 3.0
            thickness = 4

            # OpenCV verwendet BGR, nicht RGB
            purple = (255, 0, 255)

            # Größe des Textes bestimmen
            (text_width, text_height), baseline = cv2.getTextSize(
                text,
                font,
                font_scale,
                thickness
            )

            # Text so positionieren, dass die Nummer
            # ungefähr mittig im Bereich sitzt
            text_x = int(
                center_x - text_width / 2
            )

            text_y = int(
                center_y + text_height / 2
            )

            cv2.putText(
                result_image,
                text,
                (text_x, text_y),
                font,
                font_scale,
                purple,
                thickness,
                cv2.LINE_AA
            )

        return result_image

    # =========================================================
    # AKTUELLEN FILTER AUSLESEN
    # =========================================================

    def get_filter_name(self):
        if self.filter_mode == "light":
            return "Leicht"

        return "Mittel"

    # =========================================================
    # FILTERWERTE AUSLESEN
    # =========================================================

    def get_filter_values(self):
        return {
            "mode": self.filter_mode,
            "name": self.get_filter_name(),
            "h_min": self.green_filter["h_min"],
            "h_max": self.green_filter["h_max"],
            "s_min": self.green_filter["s_min"],
            "v_min": self.green_filter["v_min"],
        }