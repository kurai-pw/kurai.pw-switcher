import os
import sys
import configparser

from subprocess import Popen
from time import sleep
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
    QLineEdit,
    QWidget,
    QPushButton,
    QFrame,
    QLabel,
    QFileDialog,
    QMessageBox
)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class kuraiApp(QWidget):
    APP_WIDTH = 560
    APP_HEIGHT = 220

    APP_CSS = """
        background-color: #21201E;
    """

    LINE_CSS = """
        background-color: pink;
    """

    CLOSE_BUTTON_CSS = """
        QPushButton {
            width: 20px;
            height: 20px;
            color: #FFE7FC;
            border: none;
            font-size: 18px;
        }
        QPushButton::hover {
            color: #FFE7FC;
        }
    """

    LABEL_CSS = """
        font-size: 18px;
        color: #FFE7FC;
    """

    OSU_PATH_FIELD_CSS = """
        width: 430px;
        border: 2px solid #333;
        padding: 8px 8px;
        font-size: 12px;
        color: #FFE7FC;
    """

    SELECT_OSU_PATH_BUTTON_CSS = """
        border: 2px solid #333;
    """

    ACTION_BUTTONS_CSS = """
        font-size: 12px;
        color: #FFE7FC;
        border: 2px solid #333;
    """

    def __init__(self):
        super().__init__(None)

        self.osu_path = self.load_osu_path()
        self.server = 'bancho'

        # Objects.
        self.osu_path_qline = None
        self.switch_button = None

        self.setup_layout()


    def setup_layout(self):
        self.setWindowIcon(QtGui.QIcon(resource_path('assets/kurai.png')))
        self.setWindowTitle('osu!kurai switcher')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedWidth(self.APP_WIDTH)
        self.setFixedHeight(self.APP_HEIGHT)
        self.setStyleSheet(self.APP_CSS)

        # Load custom font.
        font = QFontDatabase.addApplicationFont(resource_path("assets/Poppins-Light.ttf"))
        font = QFontDatabase.applicationFontFamilies(font)
        font = QFont(font[0], 32)

        # Top line.
        line = QFrame(self)
        line.setGeometry(0, 0, 560, 4)
        line.setStyleSheet(self.LINE_CSS)

        close_button = QPushButton('✕', self)
        close_button.setStyleSheet(self.CLOSE_BUTTON_CSS)
        close_button.setFixedWidth(30)
        close_button.setFixedHeight(30)
        close_button.move(525, 9)
        close_button.clicked.connect(self.close_program)

        logo = QPixmap(resource_path('assets/kurai_64.png'))
        logo_label = QLabel(self)
        logo_label.setPixmap(logo)
        logo_label.setGeometry(10, 15, 64, 64)

        label = QLabel(self)
        label.setText('kurai!switcher')
        label.setStyleSheet(self.LABEL_CSS)
        label.setFont(font)
        label.setGeometry(85, 38, 150, 20)

        self.osu_path_qline = QLineEdit(self)
        self.osu_path_qline.setPlaceholderText('osu!path')
        self.osu_path_qline.setStyleSheet(self.OSU_PATH_FIELD_CSS)
        self.osu_path_qline.move(50, 100)
        self.osu_path_qline.setText(self.osu_path)

        select_osu_path = QPushButton(self)
        select_osu_path.setIcon(QIcon(resource_path('assets/folder.png')))
        select_osu_path.setIconSize(QSize(20, 20))
        select_osu_path.setFixedWidth(36)
        select_osu_path.setFixedHeight(36)
        select_osu_path.move(464, 100)
        select_osu_path.setStyleSheet(self.SELECT_OSU_PATH_BUTTON_CSS)
        select_osu_path.clicked.connect(self.file_dialog)

        self.switch_button = QPushButton('Switch to kurai' if self.server == 'bancho' else 'Switch to bancho', self)
        self.switch_button.setStyleSheet(self.ACTION_BUTTONS_CSS)
        self.switch_button.setFont(font)
        self.switch_button.setFixedWidth(200)
        self.switch_button.setFixedHeight(40)
        self.switch_button.move(50, 150)
        self.switch_button.clicked.connect(self.switch_server)

        run_osu_button = QPushButton('Run osu!', self)
        run_osu_button.setStyleSheet(self.ACTION_BUTTONS_CSS)
        run_osu_button.setFont(font)
        run_osu_button.setFixedWidth(200)
        run_osu_button.setFixedHeight(40)
        run_osu_button.move(300, 150)
        run_osu_button.clicked.connect(self.run_osu)

    def file_dialog(self):
        self.osu_path = QFileDialog.getExistingDirectory(self, "Select Directory", self.osu_path)
        self.set_osu_path()

    def set_osu_path(self):
        self.osu_path_qline.setText(self.osu_path)

    def switch_server(self):
        self.server = 'kurai' if self.server == 'bancho' else 'bancho'
        self.switch_button.setText('Switch to kurai' if self.server == 'bancho' else 'Switch to bancho')

    def run_osu(self):
        if not self.osu_path:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Error")
            error_dialog.setInformativeText('Hello')
            error_dialog.setWindowTitle("Error")
            return

        try:
            args = ''
            if self.server == 'bancho':
                args = ''
            elif self.server == 'kurai':
                args = '-devserver kurai.pw'


            # Run osu!.
            Popen([self.osu_path + '/osu!.exe'] + args.split())
        except Exception as e:
            print(e)

        self.close_program()

    def close_program(self):
        # Fade effect.
        for i in range(50):
            self.setWindowOpacity(1 - (i / 50))
            sleep(0.01)

        self.save_config(self.osu_path)

        # Close app.
        self.close()

    @staticmethod
    def load_osu_path():
        config = configparser.ConfigParser()
        config.read('kurai_config.ini')

        try:
            return config.get('settings', 'osu_path')
        except Exception as e:
            return ''


    @staticmethod
    def save_config(osu_path: str):
        config = configparser.ConfigParser()
        config.add_section('settings')
        config.set('settings', 'osu_path', osu_path)

        with open('kurai_config.ini', 'w') as config_file:  # save
            config.write(config_file)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    win = kuraiApp()
    win.show()
    sys.exit(app.exec_())
