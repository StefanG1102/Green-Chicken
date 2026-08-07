from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
)


class AnalysisView(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.graphics_scene = QGraphicsScene(self)
        self.setScene(self.graphics_scene)

        self.image_item = None

        self.zoom_factor = 1.15

        self.setBackgroundBrush(
            Qt.GlobalColor.darkGray
        )

        self.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setDragMode(
            QGraphicsView.DragMode.ScrollHandDrag
        )

    def clear_image(self):
        self.graphics_scene.clear()
        self.image_item = None

    def show_cv_image(self, image):
        if image is None:
            return False

        height, width, channels = image.shape

        rgb_image = image[:, :, ::-1].copy()

        bytes_per_line = channels * width

        qimage = QImage(
            rgb_image.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        ).copy()

        pixmap = QPixmap.fromImage(
            qimage
        )

        self.graphics_scene.clear()

        self.image_item = (
            self.graphics_scene.addPixmap(
                pixmap
            )
        )

        self.graphics_scene.setSceneRect(
            pixmap.rect()
        )

        self.fitInView(
            self.image_item,
            Qt.AspectRatioMode.KeepAspectRatio
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