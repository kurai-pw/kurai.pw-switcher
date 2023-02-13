import os
import sys
import configparser

from subprocess import Popen, check_call
from time import sleep
from webbrowser import open as webbrowser_open
from PyQt5.QtCore import Qt, QSize
# from PyQt5.QtCore.Qt import FramelessWindowHint, CursorShape
# from PyQt5.QtCore.Qt. import PointingHandCursor
from PyQt5.QtGui import QIcon, QFont, QFontDatabase, QCursor
from PyQt5.QtWidgets import (
    QApplication,
    QLineEdit,
    QWidget,
    QPushButton,
    QFrame,
    QLabel,
    QFileDialog
)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class CSS:
    """
    Class with the app CSS.
    """

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

    LOGO_CSS = """
        border: none;
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

    ERROR_MESSAGE_CSS = """
        color: red;
        font-size: 12px;
    """

    APP_VERSION_CSS = """
        color: #444444;
        font-size: 14px;
    """


class kuraiApp(QWidget):
    """
    Switcher app based on PyQt5.
    """

    APP_WIDTH = 560
    APP_HEIGHT = 220

    APP_VERSION = 'v1.1a'

    SERVER_DOMAIN = 'kurai.pw'
    SERVER_URL = 'https://kurai.pw/'

    # .ini config file name
    CONFIG_FILE_NAME = '.kurai_config.ini'

    def __init__(self):
        super().__init__(None)
        self.CSS = CSS()

        self.osu_path = self.load_osu_path()
        self.server = 'bancho'

        # Objects.
        self.osu_path_qline = None
        self.switch_button = None

        # Variable used to drag the window.
        self.offset = 0

        self.fonts = self.load_fonts()
        self.setup_layout()

    @staticmethod
    def load_fonts():
        """
        Load custom font.
        """

        light_font = QFontDatabase.addApplicationFont(resource_path("assets/Poppins-Light.ttf"))
        light_font = QFontDatabase.applicationFontFamilies(light_font)

        regular_font = QFontDatabase.addApplicationFont(resource_path("assets/Poppins-Regular.ttf"))
        regular_font = QFontDatabase.applicationFontFamilies(regular_font)

        return {
            'light': QFont(light_font[0], 32),
            'regular': QFont(regular_font[0], 32)
        }

    def setup_layout(self):
        """
        Creating UI objects.
        """

        # Windows settings.
        self.setWindowIcon(QIcon(resource_path('assets/kurai.png')))
        self.setWindowTitle('osu!kurai switcher')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedWidth(self.APP_WIDTH)
        self.setFixedHeight(self.APP_HEIGHT)
        self.setStyleSheet(self.CSS.APP_CSS)

        # Top line.
        line = QFrame(self)
        line.setGeometry(0, 0, 560, 4)
        line.setStyleSheet(self.CSS.LINE_CSS)

        # Logo icon object.
        logo = QPushButton(self)
        logo.setIcon(QIcon(resource_path('assets/kurai_64.png')))
        logo.setIconSize(QSize(64, 64))
        logo.setFixedWidth(64)
        logo.setFixedHeight(64)
        logo.setGeometry(10, 15, 64, 64)
        logo.setStyleSheet(self.CSS.LOGO_CSS)
        logo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        logo.clicked.connect(lambda: webbrowser_open(self.SERVER_URL))

        # Logo label that contain logo icon.
        logo_label = QLabel(self)
        logo_label.setText('kurai!switcher')
        logo_label.setStyleSheet(self.CSS.LABEL_CSS)
        logo_label.setFont(self.fonts['light'])
        logo_label.setGeometry(85, 38, 150, 20)

        # osu! path line.
        self.osu_path_qline = QLineEdit(self)
        self.osu_path_qline.setPlaceholderText('osu!path')
        self.osu_path_qline.setStyleSheet(self.CSS.OSU_PATH_FIELD_CSS)
        self.osu_path_qline.setGeometry(50, 100, 418, 36)
        self.osu_path_qline.setText(self.osu_path)
        self.osu_path_qline.textChanged.connect(self.set_osu_path)

        # Specify osu! path by select directory (icon-button).
        select_osu_path = QPushButton(self)
        select_osu_path.setIcon(QIcon(resource_path('assets/folder.png')))
        select_osu_path.setIconSize(QSize(20, 20))
        select_osu_path.setFixedWidth(36)
        select_osu_path.setFixedHeight(36)
        select_osu_path.move(464, 100)
        select_osu_path.setStyleSheet(self.CSS.SELECT_OSU_PATH_BUTTON_CSS)
        select_osu_path.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        select_osu_path.clicked.connect(self.file_dialog)

        # Switch server button.
        self.switch_button = QPushButton('Switch to kurai' if self.server == 'bancho' else 'Switch to bancho', self)
        self.switch_button.setStyleSheet(self.CSS.ACTION_BUTTONS_CSS)
        self.switch_button.setFont(self.fonts['regular'])
        self.switch_button.setFixedWidth(200)
        self.switch_button.setFixedHeight(40)
        self.switch_button.move(50, 150)
        self.switch_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.switch_button.clicked.connect(self.switch_server)

        # Run osu button.
        run_osu_button = QPushButton('Run osu!', self)
        run_osu_button.setStyleSheet(self.CSS.ACTION_BUTTONS_CSS)
        run_osu_button.setFont(self.fonts['regular'])
        run_osu_button.setFixedWidth(200)
        run_osu_button.setFixedHeight(40)
        run_osu_button.move(300, 150)
        run_osu_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        run_osu_button.clicked.connect(self.run_osu)

        # Close button.
        close_button = QPushButton('✕', self)
        close_button.setStyleSheet(self.CSS.CLOSE_BUTTON_CSS)
        close_button.setFixedWidth(30)
        close_button.setFixedHeight(30)
        close_button.move(525, 9)
        close_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_button.clicked.connect(self.close_program)

        # Version text.
        version_label = QLabel(self)
        version_label.setText(self.APP_VERSION)
        version_label.setStyleSheet(self.CSS.APP_VERSION_CSS)
        version_label.setFont(self.fonts['regular'])
        version_label.setGeometry(4, 203, 128, 16)

    def file_dialog(self):
        self.set_osu_path(QFileDialog.getExistingDirectory(self, "Select Directory", self.osu_path))
        self.update_osu_path_text()

    def set_osu_path(self, path: str):
        self.osu_path = path
        print(path)

    def update_osu_path_text(self):
        """
        Update QLine object text @var self.osu_path_qline.
        """
        self.osu_path_qline.setText(self.osu_path)

    def switch_server(self):
        self.server = 'kurai' if self.server == 'bancho' else 'bancho'
        self.switch_button.setText('Switch to kurai' if self.server == 'bancho' else 'Switch to bancho')

    def run_osu(self):
        if not self.osu_path:
            self.throw_error()

        try:
            args = ''
            if self.server == 'bancho':
                args = ''
            elif self.server == 'kurai':
                args = f'-devserver {self.SERVER_DOMAIN}'

            # Run osu!.
            Popen([self.osu_path + '/osu!.exe'] + args.split())
        except Exception as e:
            pass # @TODO Add error message.

        self.close_program()

    def close_program(self):
        # Fade effect.
        for i in range(50):
            self.setWindowOpacity(1 - (i / 50))
            sleep(0.01)

        self.save_config(self.osu_path)

        # Close app.
        self.close()

    def load_osu_path(self):
        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE_NAME)

        try:
            return config.get('settings', 'osu_path')
        except Exception as e:
            return ''

    def save_config(self, osu_path: str):
        config = configparser.ConfigParser()
        config.add_section('settings')
        config.set('settings', 'osu_path', osu_path)

        with open(self.CONFIG_FILE_NAME, 'w') as config_file:  # save
            config.write(config_file)

        # Make config file invisible.
        check_call(['attrib', '+H', self.CONFIG_FILE_NAME])

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
