from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import (
    QPixmap,
    QPen,
    QBrush,
    QColor,
    QPolygonF,
    QPainterPath
)
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QGraphicsPolygonItem,
    QGraphicsEllipseItem,
    QGraphicsSimpleTextItem,
)

from graphics.region import Region



class ImageView(QGraphicsView):
    region_created = Signal(object)

    MODE_NAVIGATION = "navigation"
    MODE_DRAW_REGION = "draw_region"
    MODE_DRAW_DEADZONE = "draw_deadzone"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)

        self.image_item = None

        self.zoom_factor = 1.15

        self.mode = self.MODE_NAVIGATION
        self.selected_region = None
        self.current_deadzone_region = None

        self.regions = []

        self.current_points = []
        self.current_point_items = []
        self.current_line_items = []

        self.next_region_id = 1

        self.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.setBackgroundBrush(
            Qt.GlobalColor.darkGray
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setDragMode(
            QGraphicsView.DragMode.NoDrag
        )

        self.is_panning = False
        self.pan_start = None

    def load_image(self, file_path):
        pixmap = QPixmap(file_path)

        if pixmap.isNull():
            return False

        self.graphics_scene.clear()

        self.image_item = self.graphics_scene.addPixmap(
            pixmap
        )

        self.image_item.setZValue(-100)

        self.graphics_scene.setSceneRect(
            pixmap.rect()
        )

        self.fitInView(
            self.image_item,
            Qt.AspectRatioMode.KeepAspectRatio
        )

        self.regions.clear()
        self.current_points.clear()
        self.current_point_items.clear()
        self.current_line_items.clear()

        self.next_region_id = 1

        self.set_mode_navigation()

        return True

    def set_mode_navigation(self):
        self.cancel_current_polygon()

        self.mode = self.MODE_NAVIGATION

        self.setDragMode(
            QGraphicsView.DragMode.ScrollHandDrag
        )

        self.setCursor(
            Qt.CursorShape.ArrowCursor
        )

    def set_mode_draw_region(self):
        if self.image_item is None:
            return False

        self.cancel_current_polygon()

        self.mode = self.MODE_DRAW_REGION

        self.setDragMode(
            QGraphicsView.DragMode.NoDrag
        )

        self.setCursor(
            Qt.CursorShape.CrossCursor
        )

        return True

    def wheelEvent(self, event):
        if self.image_item is None:
            return

        if event.angleDelta().y() > 0:
            factor = self.zoom_factor
        else:
            factor = 1 / self.zoom_factor

        self.scale(
            factor,
            factor
        )

    def mousePressEvent(self, event):
        self.setFocus()

        # Rechte Maustaste = Bild verschieben
        if event.button() == Qt.MouseButton.RightButton:
            self.is_panning = True
            self.pan_start = event.position()

            self.setCursor(
                Qt.CursorShape.ClosedHandCursor
            )

            return

        # Polygonpunkt setzen
        if (
                self.mode in (
                self.MODE_DRAW_REGION,
                self.MODE_DRAW_DEADZONE,
        )
                and event.button() == Qt.MouseButton.LeftButton
        ):
            scene_pos = self.mapToScene(
                event.position().toPoint()
            )

            if self.mode == self.MODE_DRAW_REGION:

                if self.point_inside_image(scene_pos):
                    self.add_polygon_point(scene_pos)

            elif self.mode == self.MODE_DRAW_DEADZONE:

                if self.point_inside_selected_region(scene_pos):
                    self.add_polygon_point(scene_pos)

            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_panning and self.pan_start is not None:
            delta = event.position() - self.pan_start
            self.pan_start = event.position()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value()
                - int(delta.x())
            )

            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value()
                - int(delta.y())
            )

            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (
                event.button() == Qt.MouseButton.RightButton
                and self.is_panning
        ):
            self.is_panning = False
            self.pan_start = None

            if self.mode == self.MODE_DRAW_REGION:
                self.setCursor(
                    Qt.CursorShape.CrossCursor
                )
            else:
                self.setCursor(
                    Qt.CursorShape.ArrowCursor
                )

            return

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if (
                self.mode in (
                self.MODE_DRAW_REGION,
                self.MODE_DRAW_DEADZONE,
        )
                and event.button() == Qt.MouseButton.LeftButton
        ):
            if len(self.current_points) >= 3:

                if self.mode == self.MODE_DRAW_REGION:
                    self.finish_polygon()

                elif self.mode == self.MODE_DRAW_DEADZONE:
                    self.finish_deadzone()

            return

        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_current_polygon()
            return

        if event.key() in (
                Qt.Key.Key_Backspace,
                Qt.Key.Key_Delete,
        ):
            self.remove_last_polygon_point()
            return

        super().keyPressEvent(event)

    def point_inside_image(self, scene_pos):
        if self.image_item is None:
            return False

        return self.image_item.boundingRect().contains(
            scene_pos
        )

    def add_polygon_point(self, scene_pos):
        point = QPointF(
            scene_pos.x(),
            scene_pos.y()
        )

        self.current_points.append(point)

        radius = 4

        point_item = QGraphicsEllipseItem(
            point.x() - radius,
            point.y() - radius,
            radius * 2,
            radius * 2,
        )

        point_item.setPen(
            QPen(
                QColor(255, 255, 0),
                1
            )
        )

        point_item.setBrush(
            QBrush(
                QColor(255, 255, 0)
            )
        )

        point_item.setZValue(20)

        self.graphics_scene.addItem(
            point_item
        )

        self.current_point_items.append(
            point_item
        )

        if len(self.current_points) >= 2:
            previous = self.current_points[-2]

            line_item = self.graphics_scene.addLine(
                previous.x(),
                previous.y(),
                point.x(),
                point.y(),
                QPen(
                    QColor(255, 255, 0),
                    2
                )
            )

            line_item.setZValue(15)

            self.current_line_items.append(
                line_item
            )

    def finish_polygon(self):
        if len(self.current_points) < 3:
            return

        polygon = QPolygonF(
            self.current_points
        )

        polygon_item = QGraphicsPolygonItem(
            polygon
        )

        polygon_item.setPen(
            QPen(
                QColor(0, 255, 0),
                2
            )
        )

        polygon_item.setBrush(
            QBrush(
                QColor(0, 255, 0, 40)
            )
        )

        polygon_item.setZValue(10)

        self.graphics_scene.addItem(
            polygon_item
        )

        region = Region(
            region_id=self.next_region_id,
            points=[
                (point.x(), point.y())
                for point in self.current_points
            ],
        )

        self.regions.append(region)

        self.add_region_label(
            region
        )

        self.next_region_id += 1

        self.clear_temporary_polygon()

        self.region_created.emit(
            region
        )

    def add_region_label(self, region):
        if not region.points:
            return

        x_values = [
            point[0]
            for point in region.points
        ]

        y_values = [
            point[1]
            for point in region.points
        ]

        center_x = sum(x_values) / len(x_values)
        center_y = sum(y_values) / len(y_values)

        label = QGraphicsSimpleTextItem(
            str(region.region_id)
        )

        # Lila Farbe
        label.setBrush(
            QBrush(
                QColor(180, 0, 180)
            )
        )

        # Größere Schrift
        font = label.font()
        font.setPointSize(150)
        font.setBold(True)

        label.setFont(font)

        # Text zentrieren
        bounding_rect = label.boundingRect()

        label.setPos(
            center_x - bounding_rect.width() / 2,
            center_y - bounding_rect.height() / 2
        )

        label.setZValue(30)

        self.graphics_scene.addItem(
            label
        )

    def clear_temporary_polygon(self):
        for item in self.current_point_items:
            self.graphics_scene.removeItem(item)

        for item in self.current_line_items:
            self.graphics_scene.removeItem(item)

        self.current_points.clear()
        self.current_point_items.clear()
        self.current_line_items.clear()

    def cancel_current_polygon(self):
        self.clear_temporary_polygon()

    def remove_last_polygon_point(self):
        if not self.current_points:
            return

        # Letzten Punkt aus der Punktliste entfernen
        self.current_points.pop()

        # Letzten sichtbaren Punkt entfernen
        if self.current_point_items:
            point_item = self.current_point_items.pop()
            self.graphics_scene.removeItem(point_item)

        # Die letzte Verbindungslinie entfernen
        if self.current_line_items:
            line_item = self.current_line_items.pop()
            self.graphics_scene.removeItem(line_item)

    def select_region(self, region_id):
        for region in self.regions:
            if region.region_id == region_id:
                self.selected_region = region
                return True

        self.selected_region = None
        return False

    def set_mode_draw_deadzone(self):
        if self.image_item is None:
            return False

        if self.selected_region is None:
            return False

        self.cancel_current_polygon()

        self.mode = self.MODE_DRAW_DEADZONE
        self.current_deadzone_region = self.selected_region

        self.setDragMode(
            QGraphicsView.DragMode.NoDrag
        )

        self.setCursor(
            Qt.CursorShape.CrossCursor
        )

        return True

    def finish_deadzone(self):
        if len(self.current_points) < 3:
            return

        if self.current_deadzone_region is None:
            return

        polygon = QPolygonF(
            self.current_points
        )

        # Schwarze Fläche für die Dead Zone
        deadzone_item = QGraphicsPolygonItem(
            polygon
        )

        deadzone_item.setPen(
            QPen(
                QColor(255, 255, 255),
                1
            )
        )

        deadzone_item.setBrush(
            QBrush(
                QColor(0, 0, 0, 220)
            )
        )

        deadzone_item.setZValue(25)

        self.graphics_scene.addItem(
            deadzone_item
        )

        deadzone_points = [
            (point.x(), point.y())
            for point in self.current_points
        ]

        self.current_deadzone_region.dead_zones.append(
            deadzone_points
        )

        self.clear_temporary_polygon()

        self.set_mode_navigation()

    def point_inside_selected_region(self, scene_pos):
        if self.selected_region is None:
            return False

        polygon = QPolygonF(
            [
                QPointF(x, y)
                for x, y in self.selected_region.points
            ]
        )

        path = QPainterPath()
        path.addPolygon(polygon)

        return path.contains(scene_pos)

    def show_cv_image(self, image):
        if image is None:
            return False

        height, width, channels = image.shape

        bytes_per_line = channels * width

        rgb_image = image[:, :, ::-1].copy()

        from PySide6.QtGui import QImage

        qimage = QImage(
            rgb_image.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        ).copy()

        pixmap = QPixmap.fromImage(qimage)

        self.graphics_scene.clear()

        self.image_item = self.graphics_scene.addPixmap(
            pixmap
        )

        self.image_item.setZValue(-100)

        self.graphics_scene.setSceneRect(
            pixmap.rect()
        )

        self.fitInView(
            self.image_item,
            Qt.AspectRatioMode.KeepAspectRatio
        )

        return True