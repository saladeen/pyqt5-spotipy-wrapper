from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
import window_toolbar
import pprint
from time import sleep
import testwindow

# TODO: add a check for whether the current song playing is in the menu, then change text color of buttons to green if it is
# this whole thing is gonna need to be refactored to return context URIs and offsets instead of song IDs

# ADD: labels for album/artist

class PopoutWindow(testwindow.TestWindow):
    song_selected = pyqtSignal()

    def __init__(self, data, sp):
        super().__init__()
        # data = [self.sp.album_name, self.sp.album_uri, self.sp.artist_name, self.sp.artist_uri, self.sp.playlist_name, self.sp.playlist_context_uri, self.sp.song_names_in_current_album, self.sp.artist_top_track_names, self.sp.playlist_song_names, self.sp.artist_top_track_ids]
        self.close_min_bar = window_toolbar.MenuBar(self, "Browse")
        self.offset = None
        self.sp = sp


        layout = QVBoxLayout(self)
        layout.addWidget(self.close_min_bar)
        self.setLayout(layout)

        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.tab_bar = QTabWidget()

        layout.addWidget(self.tab_bar)

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
QLabel{
    font-size: 45px;
    color: white;
}
        """)

        self.tab_bar.setStyleSheet("""
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
}
        """)

        self.album = QWidget()
        self.artist = QWidget()
        self.playlist = QWidget()
        self.your_library = QWidget()
        
        album_layout = QVBoxLayout(self.album)
        album_layout.setAlignment(Qt.AlignTop)
        album_name_label = QLabel(data[0])
        album_layout.addWidget(album_name_label)

        album_showed = len(data[6])
        if album_showed > 35:
            album_showed = 35
        
        for i in range(album_showed):
            self.create_btn(data[6][i], album_layout).clicked.connect(lambda stupid_bool, i=i: self.play_song_clicked(i, data[1]))


        artist_layout = QVBoxLayout(self.artist)
        artist_layout.setAlignment(Qt.AlignTop)
        artist_name_label = QLabel(data[2])
        artist_layout.addWidget(artist_name_label)

        for i in range(0, len(data[7])):
            self.create_btn(data[7][i], artist_layout).clicked.connect(lambda stupid_bool, i=i: self.play_song_clicked_artist(data[9][i]))

        playlist_layout = QVBoxLayout(self.playlist)
        playlist_layout.setAlignment(Qt.AlignTop)
        playlist_name_label = QLabel(data[4])
        playlist_layout.addWidget(playlist_name_label)

        playlist_showed = len(data[8])
        if playlist_showed > 35:
            playlist_showed = 35

        for i in range(playlist_showed):
            self.create_btn(data[8][i], playlist_layout).clicked.connect(lambda stupid_bool, i=i: self.play_song_clicked(i, data[5]))

        self.tab_bar.addTab(self.album, "Album") # (page object, label string)
        self.tab_bar.addTab(self.artist, "Artist")
        self.tab_bar.addTab(self.playlist, "Playlist")

        self.setWindowTitle("Browse")

    def create_btn(self, label, layout):
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        layout.addWidget(btn)
        return btn
        
    def play_song_clicked(self, offset, uri): 
        self.sp.play_song_by_context(offset, uri)
        self.song_selected.emit()
        
    def play_song_clicked_artist(self, uri):
        self.sp.play_song_by_context_artist(uri)
        self.song_selected.emit()
