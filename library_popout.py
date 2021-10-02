from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget
from PyQt5.QtCore import Qt, pyqtSignal
import window_toolbar
import testwindow

class LibraryWindow(testwindow.TestWindow):
    library_song_change = pyqtSignal()

    def __init__(self, data, sp):
        super().__init__()
        # 'data' obj: likes, like_uris, albums, album_uris, playlists, playlist_uris
        self.sp = sp

        
        self.bar = window_toolbar.MenuBar(self, "Library")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.offset = None
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.bar)

        self.tab_widget = QTabWidget()

        self.tab_widget.setStyleSheet("""
QTabWidget::pane{
    border-top: 2px solid #1db954;
}

QTabBar::tab {
    background: #212121;
    padding-right: 15px;
    padding-left: 15px;
    padding-top: 5px;
    padding-bottom: 5px;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background: #121212;
}

QTabBar::tab:!selected {
    margin-top: 2px; /* make non-selected tabs look smaller */
}""")  
        self.likes = QWidget()
        self.saved_albums = QWidget()
        self.playlists = QWidget()
        # intentionally ignoring all support for podcasts, fuck 'em

        likes_layout = QVBoxLayout(self.likes)
        likes_layout.setAlignment(Qt.AlignTop)

        albums_layout = QVBoxLayout(self.saved_albums)
        albums_layout.setAlignment(Qt.AlignTop)

        playlist_layout = QVBoxLayout(self.playlists)
        playlist_layout.setAlignment(Qt.AlignTop)

        for i in range(0, len(data[0])):
            self.create_button(data[0][i], likes_layout).clicked.connect(lambda useless, i=i: self.play_song_clicked(data[1][i]))
        for i in range(0, len(data[2])):
            self.create_button(data[2][i], albums_layout).clicked.connect(lambda useless, i=i: self.play_album_playlist_clicked(data[3][i]))
        for i in range(0, len(data[4])):
            self.create_button(data[4][i], playlist_layout).clicked.connect(lambda useless, i=i: self.play_album_playlist_clicked(data[5][i]))
        
        self.tab_widget.addTab(self.likes, "Likes")
        self.tab_widget.addTab(self.saved_albums, "Albums")
        self.tab_widget.addTab(self.playlists, "Playlists")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        self.setStyleSheet("""
    *{  
        background: #121212;
        color: #b3b3b3;
        font-size: 20px;
        font-family: Berlin Sans FB; }
QSizeGrip{
    background-image: url(icons8-resize-25-flipped.png);
    width: 25px;
    icon-size: 25px; }
QPushButton{
    font-size: 14px;
    text-align: left;
    border: none;
}
QPushButton:hover{
    background-color: #535353;
}
QPushButton:checked{
    color: #1db954;
}
        """)

        self.setWindowTitle("Library")

        self.show()

    def create_button(self, label, layout):
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        layout.addWidget(btn)
        return btn

    def play_song_clicked(self, uri):
        # gonna have to pass a Spotipy object and call song change from here, signal is to update other windows' UI
        self.sp.play_song_by_context_artist(uri) # need to rename, just uses URI as opposed to context + offset
        self.library_song_change.emit()

    def play_album_playlist_clicked(self, uri):
        self.sp.play_song_by_context(offset=0, context_uri=uri)
        self.library_song_change.emit()