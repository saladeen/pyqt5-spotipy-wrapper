from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.dragging = False

        self.drag_direction = None
        

    def mousePressEvent(self, event):
        # Splitting up if statements to deal with direction of resize
        # Basically tests if the click event is within 10 pixels of the window edge

        x, y = event.pos().x(), event.pos().y()
        w, h = self.width(), self.height()

        if x < 10 and y < 10:
            self.dragging = True
            self.drag_direction = "left/up"
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        elif x < 10 and y > h-10:
            self.dragging = True
            self.drag_direction = "left/down"
            QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
        elif x > w-10 and y < 10:
            self.dragging = True
            self.drag_direction = "right/up"
            QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
        elif x > w-10 and y > h-10:
            self.dragging = True
            self.drag_direction = "right/down"
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)

        # Testing if click is within 10px of the window edge and not within 10px of the corners
        elif x < 10 and (10 < y < h-10):
            self.dragging = True
            self.drag_direction = "left"
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        elif y < 10 and (10 < x < w-10):
            self.dragging = True
            self.drag_direction = "up"
            QApplication.setOverrideCursor(Qt.SizeVerCursor)
        elif x > w-10 and (10 < y < h-10):
            self.dragging = True
            self.drag_direction = "right"
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        elif y > h-10 and (10 < x < w-10):
            self.dragging = True
            self.drag_direction = "down"
            QApplication.setOverrideCursor(Qt.SizeVerCursor)

    def mouseMoveEvent(self, event):
        if self.dragging:
            mouse_x, mouse_y = event.pos().x(), event.pos().y()
            pos_x, pos_y = self.pos().x(), self.pos().y()

            if self.drag_direction == "right/down": 
                self.resize(mouse_x, mouse_y)
            elif self.drag_direction == "left/up": 
                self.resize(self.width() - mouse_x, self.height() - mouse_y)
                self.move(pos_x + mouse_x, pos_y + mouse_y)
            elif self.drag_direction == "right/up":
                self.resize(mouse_x, self.height() - mouse_y)
                self.move(pos_x, pos_y + mouse_y)
            elif self.drag_direction == "left/down":
                self.resize(self.width() - mouse_x, mouse_y) 
                self.move(pos_x + mouse_x, pos_y)
            elif self.drag_direction == "up":
                self.resize(self.width(), self.height() - mouse_y)
                self.move(pos_x, pos_y + mouse_y)
            elif self.drag_direction == "right":
                self.resize(mouse_x, self.height())
            elif self.drag_direction == "down":
                self.resize(self.width(), mouse_y)
            elif self.drag_direction == "left":
                self.resize(self.width() - mouse_x, self.height())
                self.move(pos_x + mouse_x, pos_y)


    def mouseReleaseEvent(self, event): 
        self.dragging = False
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        #Not ideal but restoreOverrideCursor() isnt super reliable
