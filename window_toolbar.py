from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QIcon

class MenuBar(QWidget):
    def __init__(self, parent, title_string: str): # parent must extend QWidget
        super(MenuBar, self).__init__()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.setStyleSheet("""
            *{
                font: Berlin Sans FB;
                color: white;
                font-size: 20px;
                border: none;
            }
            QPushButton::hover{
                background-color: #535353;
            }
            QPushButton{
                text-align: none; /* this fixes the icon alignment inherited */
            }
        """)
        self.title = QLabel(title_string)
        
        self.min_button = QPushButton()
        self.min_button.setFixedSize(25, 25)
        self.min_button.setIcon(QIcon("icons/minimize25.png"))
        self.min_button.setFlat(True)
        self.min_button.clicked.connect(self.min_clicked)

        self.close_button = QPushButton()
        self.close_button.setFixedSize(25, 25)
        self.close_button.setIcon(QIcon("icons/close25px.png"))
        self.close_button.setFlat(True)
        self.close_button.clicked.connect(self.close_clicked)

        self.title.setFixedHeight(25)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.min_button)
        self.layout.addWidget(self.close_button)
        
        self.setLayout(self.layout)

    def close_clicked(self):
        self.parent.close()

    def min_clicked(self):
        self.parent.showMinimized()

    def mousePressEvent(self, event):
        self.parent.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.parent.offset is not None:
            self.parent.move(self.parent.pos() + event.pos() - self.parent.offset)

    def mouseReleaseEvent(self, QMouseEvent):
        self.parent.offset = None
