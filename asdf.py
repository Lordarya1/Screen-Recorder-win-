import cv2
import pyautogui
import numpy as np
import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
from PyQt6.QtGui import QIcon

class RecorderThread(QThread):
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    recording_paused = pyqtSignal()
    recording_resumed = pyqtSignal()

    def __init__(self, output_path, parent=None):
        super().__init__(parent)
        self.output_path = output_path
        self.is_recording = False
        self.is_paused = False
        self.out = None

    def run(self):
        self.is_recording = True
        screen = pyautogui.screenshot
        screen_width, screen_height = pyautogui.size()

        # کدک MP4
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.out = cv2.VideoWriter(self.output_path, fourcc, 20.0, (screen_width, screen_height))
        self.recording_started.emit()

        while self.is_recording:
            if not self.is_paused:
                img = np.array(screen())
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                self.out.write(img)
                cv2.waitKey(1)

        self.out.release()
        self.recording_stopped.emit()

    def stop_recording(self):
        self.is_recording = False
        self.quit()

    def pause_recording(self):
        if not self.is_paused:
            self.is_paused = True
            self.recording_paused.emit()

    def resume_recording(self):
        if self.is_paused:
            self.is_paused = False
            self.recording_resumed.emit()

class RecorderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Recorder")
        self.setGeometry(50, 50, 50, 50)

        layout = QVBoxLayout()

        # افزودن برچسب نمایش مسیر ذخیره‌سازی
        self.path_label = QLabel("Path: C:\\Users\\Omidi\\Desktop\\output.mp4")
        layout.addWidget(self.path_label)

        # دکمه شروع ضبط با آیکون
        self.start_button = QPushButton(self)
        self.start_button.setIcon(QIcon("icons8-start-48.png"))  # فایل تصویر دکمه شروع
        self.start_button.setIconSize(self.start_button.size())  # سایز دکمه
        self.start_button.setStyleSheet("""
            QPushButton {
                border-radius: 50%;
                background-color: #4CAF50;
                width: 40px;
                height: 40px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_button)

        # دکمه توقف ضبط با آیکون
        self.stop_button = QPushButton(self)
        self.stop_button.setIcon(QIcon("icons8-stop-48.png"))  # فایل تصویر دکمه توقف
        self.stop_button.setIconSize(self.stop_button.size())
        self.stop_button.setStyleSheet("""
            QPushButton {
                border-radius: 50%;
                background-color: #f44336;
                width: 40px;
                height: 40px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_button)

        # دکمه Pause/Resume با آیکون
        self.pause_button = QPushButton(self)
        self.pause_button.setIcon(QIcon("icons8-pause-48.png"))  # فایل تصویر دکمه Pause
        self.pause_button.setIconSize(self.pause_button.size())
        self.pause_button.setStyleSheet("""
            QPushButton {
                border-radius: 50%;
                background-color: #2196F3;
                width: 40px;
                height: 40px;
                padding: 0;
            }
            QPushButton:hover {
                background-color:rgb(9, 75, 129);
            }
        """)
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_button)

        # دکمه برای تغییر مسیر ذخیره‌سازی با آیکون
        self.change_path_button = QPushButton(self)
        self.change_path_button.setIcon(QIcon("icons8-save.gif"))  # فایل تصویر دکمه تغییر مسیر
        self.change_path_button.setIconSize(self.change_path_button.size())
        self.change_path_button.setStyleSheet("""
            QPushButton {
                border-radius: 50%;
                background-color: #FFC107;
                width: 40px;
                height: 40px;
                padding: 0;
            }
            QPushButton:hover {
                background-color:rgb(193, 146, 6);
            }
        """)
        self.change_path_button.clicked.connect(self.change_path)
        layout.addWidget(self.change_path_button)

        self.setLayout(layout)

        # تعریف مسیر ذخیره‌سازی پیش‌فرض
        self.output_path = r"C:\Users\Omidi\Desktop\output.mp4"

        self.recorder_thread = RecorderThread(self.output_path)
        self.recorder_thread.recording_started.connect(self.on_recording_started)
        self.recorder_thread.recording_stopped.connect(self.on_recording_stopped)
        self.recorder_thread.recording_paused.connect(self.on_recording_paused)
        self.recorder_thread.recording_resumed.connect(self.on_recording_resumed)

    def start_recording(self):
        self.recorder_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.pause_button.setEnabled(True)

    def stop_recording(self):
        self.recorder_thread.stop_recording()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)

    def toggle_pause(self):
        if self.recorder_thread.is_paused:
            self.recorder_thread.resume_recording()
        else:
            self.recorder_thread.pause_recording()

    def change_path(self):
        folder = QFileDialog.getSaveFileName(self, "Save File", self.output_path, "MP4 Files (*.mp4)")[0]
        if folder:
            self.output_path = folder
            self.path_label.setText(f"Path: {self.output_path}")
            # ایجاد thread جدید برای مسیر ذخیره‌سازی جدید
            self.recorder_thread = RecorderThread(self.output_path)

    def on_recording_started(self):
        print("Recording started.")

    def on_recording_stopped(self):
        print("Recording stopped.")

    def on_recording_paused(self):
        print("Recording paused.")
        self.pause_button.setIcon(QIcon("resume_icon.png"))  # تغییر آیکون به Resume

    def on_recording_resumed(self):
        print("Recording resumed.")
        self.pause_button.setIcon(QIcon("pause_icon.png"))  # تغییر آیکون به Pause

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecorderApp()
    window.show()
    sys.exit(app.exec())
