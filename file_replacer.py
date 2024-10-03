import os
import shutil
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QFileDialog, QMessageBox, QScrollArea, QFrame, QGridLayout, QFormLayout
from PyQt6.QtCore import Qt, QSettings
import configparser

config = configparser.ConfigParser()
config_file = 'config.ini'

class FileReplaceTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_config()

        settings = QSettings('config.ini', QSettings.Format.IniFormat)
        self.resize(settings.value('size', self.size()))
        self.move(settings.value('pos', self.pos()))

    def initUI(self):
        self.setWindowTitle('文件替换工具')
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(100, 60, 100, 60)
        self.layout.setSpacing(20)

        # Target path
        self.target_path_layout = QHBoxLayout()
        self.target_path_label = QLabel('目标路径:')
        self.target_path_entry = QLineEdit()
        self.browse_button = QPushButton('浏览')
        self.browse_button.setFixedSize(100, 40)  # Set button size
        self.browse_button.clicked.connect(lambda: self.select_file(self.target_path_entry, is_directory=True))
        self.target_path_layout.addWidget(self.target_path_label)
        self.target_path_layout.addWidget(self.target_path_entry)
        self.target_path_layout.addWidget(self.browse_button)
        self.layout.addLayout(self.target_path_layout)

        # Replace files frame
        self.replace_files_frame = QFrame()
        self.replace_files_layout = QVBoxLayout()
        self.replace_files_frame.setLayout(self.replace_files_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.replace_files_frame)
        self.layout.addWidget(self.scroll_area)

        self.replace_file_entries = []

        # Buttons
        self.buttons_layout = QFormLayout()  # Use QFormLayout for more flexible positioning
        self.buttons_layout.setVerticalSpacing(20)  # Set vertical spacing

        self.add_file_button = QPushButton('添加组件')
        self.add_file_button.setFixedSize(200, 50)  # Set button size
        self.add_file_button.clicked.connect(self.add_replace_file_entry)

        self.remove_file_button = QPushButton('删除组件')
        self.remove_file_button.setFixedSize(200, 50)  # Set button size
        self.remove_file_button.clicked.connect(self.remove_replace_file_entry)

        self.replace_all_button = QPushButton('替换所有文件')
        self.replace_all_button.setFixedSize(300, 50)  # Set button size
        self.replace_all_button.clicked.connect(self.replace_all_files)

        # Add buttons to the form layout
        buttons_hbox = QHBoxLayout()
        buttons_hbox.setSpacing(100)
        buttons_hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_hbox.addWidget(self.add_file_button)
        buttons_hbox.addWidget(self.remove_file_button)
        self.buttons_layout.addRow(buttons_hbox)

        replace_button_hbox = QHBoxLayout()
        replace_button_hbox.addWidget(self.replace_all_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.buttons_layout.addRow(replace_button_hbox)

        self.layout.addLayout(self.buttons_layout)

        self.setLayout(self.layout)

    def load_config(self):
        if os.path.exists(config_file):
            config.read(config_file)
            self.target_path_entry.setText(config.get('DEFAULT', 'audio_path', fallback=''))
            num_files = config.getint('DEFAULT', 'num_files', fallback=1)
            for i in range(num_files):
                self.add_replace_file_entry()
                self.replace_file_entries[i][1].setText(config.get('DEFAULT', f'replace_file{i+1}', fallback=''))

    def save_config(self):
        config['DEFAULT'] = {
            'audio_path': self.target_path_entry.text(),
            'num_files': len(self.replace_file_entries)
        }
        for i in range(len(self.replace_file_entries)):
            config['DEFAULT'][f'replace_file{i+1}'] = self.replace_file_entries[i][1].text()
        with open(config_file, 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def select_file(self, entry, is_directory=False):
        if is_directory:
            file_path = QFileDialog.getExistingDirectory(self, '选择目录')
        else:
            file_path = QFileDialog.getOpenFileName(self, '选择文件')[0]
        entry.setText(file_path)
        self.save_config()

    def replace_all_files(self):
        audio_path = self.target_path_entry.text()
        success = True

        for _, entry, _ in self.replace_file_entries:
            replace_file = entry.text()
            if replace_file:
                dest_file = os.path.join(audio_path, os.path.basename(replace_file))
                try:
                    self.copy_and_replace(replace_file, dest_file)
                except Exception as e:
                    success = False
                    QMessageBox.critical(self, '错误', f'替换文件失败: {e}')

        if success:
            QMessageBox.information(self, '成功', '所有文件替换成功')

    def copy_and_replace(self, src, dest):
        if os.path.exists(dest):
            os.remove(dest)
        shutil.copy2(src, dest)
        print(f'Copied {src} to {dest}')

    def add_replace_file_entry(self):
        row = len(self.replace_file_entries)
        entry_layout = QHBoxLayout()
        label = QLabel(f'替换文件{row + 1}:')
        entry = QLineEdit()
        button = QPushButton('浏览')
        button.setFixedSize(100, 40)  # Set button size
        button.clicked.connect(lambda: self.select_file(entry))
        entry_layout.addWidget(label)
        entry_layout.addWidget(entry)
        entry_layout.addWidget(button)
        self.replace_files_layout.addLayout(entry_layout)
        self.replace_file_entries.append((label, entry, button))

    def remove_replace_file_entry(self):
        if self.replace_file_entries:
            label, entry, button = self.replace_file_entries.pop()
            label.deleteLater()
            entry.deleteLater()
            button.deleteLater()
        self.save_config()

    def closeEvent(self, event):
        settings = QSettings('config.ini', QSettings.Format.IniFormat)
        settings.setValue('size', self.size())
        settings.setValue('pos', self.pos())

        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = FileReplaceTool()
    main_window.show()
    sys.exit(app.exec())