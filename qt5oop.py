import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import PyQt5
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt, QTimer, QTime, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMenu, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QAction, QProgressBar, QSlider, QTabWidget
from time import sleep
import subprocess
import popout
import spotify_requests
import window_toolbar
import library_popout

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Spotify Rapper Clientele")

        self.sp = spotify_requests.Spotify()

        self.layout = QVBoxLayout()

        self.offset = None

        self.setStyleSheet("""
        background: #121212;
        QPushButton{
            border: none; 
            icon-size: 50px; 
            width: 50px;
        };
        QPushButton::hover{
            background-color: #535353;
        };
        QMenu{
            background: #121212;
        }
        """)
        
        # idk
        self.move(0, 0)

        # window menu bar
        menu_bar = window_toolbar.MenuBar(self, "Spotify Wrapper Client")
        self.layout.addWidget(menu_bar)
        

        # album cover art
        image = QPixmap("album.png")
        self.cover_art = QLabel()
        self.cover_art.setStyleSheet("margin-top: 15px; margin-left: 15px; margin-right: 15px; margin-bottom: 0px; border: 5px solid white")
        self.cover_art.setPixmap(image)
        self.layout.addWidget(self.cover_art)

        # artist and song name

        self.artist_info = QLabel(self.sp.display_string)
        self.artist_info.setStyleSheet("font-family: Berlin Sans FB; color: #b3b3b3; font-size: 20px")
        self.artist_info.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.artist_info)


        # timer
        self.create_track_timer()
        
        self.track_progress_area = TrackProgressArea(self.track_current_progress, self.track_total)
        self.track_progress_area.track_progress_bar.sliderPressed.connect(lambda: self.track_timer.stop())
        self.track_progress_area.track_progress_bar.sliderReleased.connect(lambda: self.scrub_track())
        self.layout.addWidget(self.track_progress_area)

        # control buttons & parent widget/layour for them
        controls = QWidget()
        c_layout = QHBoxLayout()
        c_layout.setAlignment(Qt.AlignCenter)


        self.play_pause = self.create_pushbutton("icons/pause50.png", 50)
        if not self.sp.is_playing:
            self.play_pause.setIcon(QIcon("icons/play50.png"))
            self.track_timer.stop()
        self.play_pause.clicked.connect(self.play_pause_func)

        previous = self.create_pushbutton("icons/previous50.png", 50)
        previous.clicked.connect(self.previous_func)
        skip = self.create_pushbutton("icons/skip50.png", 50)
        skip.clicked.connect(self.skip_func)

        self.shuffle = self.create_pushbutton("icons/whiteshuffle30.png", 30)
        if self.sp.shuffle_state:
            self.shuffle.setIcon(QIcon("icons/greenshuffle30.png"))
        self.shuffle.setStyleSheet("*{border: none; icon-size: 30px; width: 30px} *:hover{background-color: #535353}")
        self.shuffle.clicked.connect(self.shuffle_func)

        menu_button = self.create_pushbutton("icons/menu30.png", 30)
        
        menu_button.setStyleSheet("*{border: none; icon-size: 30px; width: 30px} *:hover{background-color: #535353}")

        self.test_menu = QMenu()
        self.test_menu.setStyleSheet("background: #121212; color: white;")
        self.pb_menu_option = QAction('Playback')
        self.lib_menu_option = QAction('Library')
        
        self.test_menu.addAction(self.pb_menu_option)
        self.test_menu.addAction(self.lib_menu_option)
        menu_button.setMenu(self.test_menu)
        
        self.pb_menu_option.triggered.connect(lambda action: self.open_popout())
        self.lib_menu_option.triggered.connect(lambda action: self.open_library())
        
        
        self.like_button = self.create_pushbutton("icons/whiteheart30.png", 30)
        self.like_button.setStyleSheet("*{border: none; icon-size: 30px; width: 30px} *:hover{background-color: #535353}")
        if self.sp.is_liked:
            self.like_button.setIcon(QIcon("icons/greenheart30.png"))
        self.like_button.clicked.connect(self.like_func)

        self.volume_bar = VolumeBar(self.sp.volume)
        self.volume_bar.valueChanged.connect(self.change_volume)

        c_layout.addWidget(self.like_button)
        c_layout.addWidget(previous)
        c_layout.addWidget(self.play_pause)
        c_layout.addWidget(skip)
        c_layout.addWidget(self.shuffle)
        c_layout.addWidget(menu_button)
        c_layout.addWidget(self.volume_bar)
        

        controls.setLayout(c_layout)
        controls.setStyleSheet("background-color: #212121")

        self.layout.addWidget(controls)

        self.setLayout(self.layout)
        self.setStyleSheet("background: #121212")
        self.setWindowFlags(Qt.FramelessWindowHint)

    
    def update_album_artist_title(self):
        self.sp.update_playstate()
        self.sp.request_parse_song_data()
        self.cover_art.setPixmap(QPixmap("album.png"))
        self.artist_info.setText(self.sp.display_string)
        if self.sp.is_liked:
            self.like_button.setIcon(QIcon("icons/greenheart30.png"))
        else:
            self.like_button.setIcon(QIcon("icons/whiteheart30.png"))
        

    def create_pushbutton(self, icon_filepath, size):
        button = QPushButton()
        button.setFixedSize(QSize(size, size))
        button.setStyleSheet("*{border: none; icon-size: 50px; width: 50px} *:hover{background-color: #535353}")
        button.setIcon(QIcon(icon_filepath))
        button.setFlat(True)
        return button

    def create_track_timer(self):
        self.track_current_progress = self.sp.progress 
        self.track_total = self.sp.duration

        self.track_timer = QTimer(self)
        self.track_timer.timeout.connect(self.increment_timer)
        self.track_timer.start(1000)

    def increment_timer(self):
        self.track_current_progress = self.track_current_progress + 1000
        self.track_progress_area.update_all(self.track_current_progress)
        if self.track_current_progress >= self.track_total:
            self.update_album_artist_title()
            self.track_total = self.sp.duration
            self.track_current_progress = self.sp.progress
            self.track_progress_area.next_song(self.track_current_progress, self.track_total)


    def scrub_track(self):
        position = self.track_progress_area.track_progress_bar.value()
        self.sp.set_progress(position)
        self.track_progress_area.update_all(position)
        self.track_current_progress = position
        # lambda function stops timer when pressed
        self.track_timer = QTimer(self)
        self.track_timer.timeout.connect(self.increment_timer)
        self.track_timer.start(1000)


    def play_pause_func(self):
        self.sp.update_playstate()
        if self.sp.is_playing:
            self.sp.pause()
            self.play_pause.setIcon(QIcon("icons/play50.png"))
            self.track_timer.stop()
        else:
            self.sp.play()
            self.play_pause.setIcon(QIcon("icons/pause50.png"))
            self.track_timer.start(1000)

    def sync_playback(self):
        self.update_album_artist_title()
        if self.sp.is_playing:
            self.play_pause.setIcon(QIcon("icons/pause50.png"))
        else:
            self.play_pause.setIcon(QIcon("icons/play50.png"))
        if self.sp.shuffle_state:
            self.shuffle.setIcon(QIcon("icons/greenshuffle30.png"))
        else:
            self.shuffle.setIcon(QIcon("icons/whiteshuffle30.png"))
        self.track_progress_area.next_song(self.sp.progress, self.sp.duration)
        self.track_timer.stop()
        self.create_track_timer()
    
    def skip_func(self):
        self.sp.skip()
        sleep(0.2)
        self.update_album_artist_title()
        self.track_progress_area.next_song(self.sp.progress, self.sp.duration)
        self.track_timer.stop()
        self.create_track_timer()
        
    def previous_func(self):
        self.sp.previous()
        sleep(0.2)
        self.update_album_artist_title()
        self.track_progress_area.next_song(self.sp.progress, self.sp.duration)
        self.track_timer.stop()
        self.create_track_timer()
        
    def shuffle_func(self):
        if self.sp.shuffle_state:
            self.sp.shuffle(False)
            self.sp.shuffle_state = False
            self.shuffle.setIcon(QIcon("icons/whiteshuffle30.png"))
        else:
            self.sp.shuffle(True)
            self.sp.shuffle_state = True
            self.shuffle.setIcon(QIcon("icons/greenshuffle30.png"))

    def like_func(self):
        if self.sp.is_liked:
            self.sp.unlike()
            self.sp.is_liked = False
            self.like_button.setIcon(QIcon("icons/whiteheart30.png"))
        else: 
            self.sp.like() 
            self.sp.is_liked = True
            self.like_button.setIcon(QIcon("icons/greenheart30.png"))

    def change_volume(self):
        vol = self.volume_bar.value()
        self.sp.set_volume(vol)

    def open_popout(self):
        # sending: album name, artist name, playlist name, album song names/ids, artist song names/ids, playlist song names/ids.
        self.sp.request_parse_user_data()
        # Need to pass a spotify instance so it can make commands
        data = [self.sp.album_name, self.sp.album_uri, self.sp.artist_name, self.sp.artist_uri, self.sp.playlist_name, self.sp.playlist_context_uri, self.sp.song_names_in_current_album, self.sp.artist_top_track_names, self.sp.playlist_song_names, self.sp.artist_top_track_uris]
        self.popout = popout.PopoutWindow(data, self.sp)
        self.popout.song_selected.connect(self.wait_then_sync)
        self.popout.show()

    def wait_then_sync(self):
        sleep(0.5) # doing this bc otherwise I get Nones from API calls
        self.sync_playback()

    def open_library(self):
        self.sp.request_parse_library_data()
        data = [self.sp.user_likes, self.sp.user_likes_uris, self.sp.saved_albums, self.sp.saved_album_uris, self.sp.saved_playlists, self.sp.saved_playlists_uris]
        self.lib = library_popout.LibraryWindow(data, self.sp)
        self.lib.library_song_change.connect(self.wait_then_sync)
        self.lib.show()

class TrackProgressArea(QWidget):
    def __init__(self, current, total):
        super().__init__() 
        self.track_progress_bar = SliderProgress(current, total)
        layout = QVBoxLayout()
        layout.addWidget(self.track_progress_bar)

        self.bar_label = QLabel(self) #may not need inheritance, we'll see
        self.bar_label.setStyleSheet("color: white")
        self.bar_label.setAlignment(Qt.AlignCenter)

        self.time_total = QTime(0, 0, 0, 0)
        self.time_total = self.time_total.addMSecs(total)
        self.time_current = QTime(0, 0, 0, 0)
        self.time_current = self.time_current.addMSecs(current)
        

        self.display_string = self.time_current.toString("mm:ss") + " / " + self.time_total.toString("mm:ss")
        self.bar_label.setText(self.display_string)

        layout.addWidget(self.bar_label)

        self.setLayout(layout)
        # this will contain the progress bar, a label, and timer methods
        # need to figure out methods for time formatting
    
    def update_all(self, progress):
        self.time_current = QTime(0, 0, 0, 0)
        self.time_current = self.time_current.addMSecs(progress)
        self.display_string = self.time_current.toString("mm:ss") + " / " + self.time_total.toString("mm:ss")
        self.bar_label.setText(self.display_string)
        self.track_progress_bar.update_progress(progress)

    def next_song(self, progress, total):
        self.time_current = QTime(0, 0, 0, 0)
        self.time_current = self.time_current.addMSecs(progress)
        self.time_total = QTime(0, 0, 0, 0)
        self.time_total = self.time_total.addMSecs(total)
        self.display_string = self.time_current.toString("mm:ss") + " / " + self.time_total.toString("mm:ss")
        self.bar_label.setText(self.display_string)
        self.track_progress_bar.next_song(progress, total)

    def get_position(self) -> int:
        return self.track_progress_bar.get_position()
        
        

class SliderProgress(QSlider):

    def __init__(self, current, total):
        super().__init__()
        self.setMaximum(total)
        self.setMinimum(0)
        self.setValue(current)
        self.setOrientation(Qt.Horizontal)
        self.setStyleSheet("""
QSlider::groove:horizontal {
    background: white;
    height: 10px;
    border-radius: 4px;
}

QSlider::sub-page:horizontal {
    background: white;
    height: 10px;
    border-radius: 4px;
    border: 1px solid #212121
}

QSlider::add-page:horizontal {
    background: #121212;
    height: 10px;
    border-radius: 4px;
    border: 1px solid #212121
}

QSlider::handle:horizontal {
    background: white;
    width: 10px;
    border: 1px solid white;
    border-radius: 2px;
}
QSlider::handle:horizontal:hover{
    border: 1px solid #1db954
}
        """)

    def update_progress(self, progress):
        self.setValue(progress)
    def next_song(self, progress, duration):
        self.setValue(progress)
        self.setMaximum(duration)
    def get_position(self) -> int:
        return self.value()

    
class VolumeBar(QSlider):
    def __init__(self, volume_initial):
        super().__init__()
        self.setMaximum(100)
        self.setMinimum(0)
        self.setOrientation(Qt.Vertical)
        self.setValue(volume_initial)
        self.setStyleSheet("""
            QSlider::groove:vertical{
                background: #121212;
                width: 10px;
            }
            QSlider::handle:vertical{
                background: #b3b3b3;
                width 10px;
                height: 10px;
                border-radius: 2px;
            }
            QSlider::add-page:vertical{
                background: white;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())


# General ideas
# Grey out options that are not available in certain playback modes (shuffle, volume are only two i think?) (:disabled)
# Attribute the two icons i didnt create by myself (heart/shuffle)
# Paginated results, add 'next page' button to popouts that will request next (up to) 50 results and display them

#Bugs
# No support for multiple artists
# Not really supporting podcasts whatsoever
