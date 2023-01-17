import sys
from PySide2.QtCore import Qt, QTimer, QTextStream, QFile, QIODevice
from PySide2.QtGui import QKeySequence, QFontMetrics, QPixmap
from PySide2.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QSlider, QVBoxLayout, QWidget)

class TextPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sokudoku Reader")
        self.setWindowIcon(QPixmap("res/images/Icon2.png"))

        # Initialize variables
        self.file = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_next_words)
        self.paused = False
        self.word_index = 0
        self.words = None

        # Create widgets
        self.file_select_button = QPushButton("Select File")
        self.file_select_button.clicked.connect(self.select_file)
        
        self.samples_per_minute_slider = QSlider(Qt.Horizontal)
        self.samples_per_minute_slider.valueChanged.connect(self.update_interval)
        self.samples_per_minute_slider.setMinimum(1)
        self.samples_per_minute_slider.setMaximum(1000)
        self.samples_per_minute_label = QLabel("Samples per Minute: (1-1000):   1")
        
        self.words_per_sample_slider = QSlider(Qt.Horizontal)
        self.words_per_sample_slider.valueChanged.connect(self.adjust_font)
        self.words_per_sample_slider.setMinimum(1)
        self.words_per_sample_slider.setMaximum(30)
        self.words_per_sample_label = QLabel("Words per Sample: (1-30): 1")
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play)
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        self.word_index_label = QLabel("Word Index:")
        self.word_index_edit = QLineEdit()
        self.word_index_edit.editingFinished.connect(self.seek)
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignCenter)

        # Post-instantiation settings
        self.samples_per_minute_slider.setValue(250)
        
        # Create layouts
        file_select_layout = QHBoxLayout()
        file_select_layout.addWidget(self.file_select_button)
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)
        word_index_layout = QHBoxLayout()
        word_index_layout.addWidget(self.word_index_label)
        word_index_layout.addWidget(self.word_index_edit)
        main_layout = QVBoxLayout()
        main_layout.addLayout(file_select_layout)
        main_layout.addWidget(self.samples_per_minute_label)
        main_layout.addWidget(self.samples_per_minute_slider)
        main_layout.addWidget(self.words_per_sample_label)
        main_layout.addWidget(self.words_per_sample_slider)
        main_layout.addLayout(control_layout)
        main_layout.addLayout(word_index_layout)
        main_layout.addWidget(self.text_label, 1)
        self.adjust_font()
        self.setLayout(main_layout)

    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filename, _ = QFileDialog.getOpenFileName(self, "Select File", "", "", options=options)
        if filename:
            print(filename)
            with open(filename, 'r') as f:
                self.words = f.read().split()

    def play(self):
        if not self.words:
            return
        #Set the timer interval based on the samples per minute and words per sample sliders
        interval = 60000 / (self.samples_per_minute_slider.value() * self.words_per_sample_slider.value())
        self.timer.start(interval)
        self.paused = False
        self.word_index_edit.setEnabled(False)

    def pause(self):
        self.timer.stop()
        self.paused = True
        self.word_index_edit.setEnabled(True)

    def stop(self):
        self.timer.stop()
        self.paused = False
        self.word_index = 0
        self.file.seek(0)
        self.word_index_edit.setText("0")

    def display_next_words(self):
        if self.paused:
            return
        words_per_sample = self.words_per_sample_slider.value()
        self.text_label.setText(' '.join(self.words[self.word_index:self.word_index+words_per_sample]))
        self.word_index += words_per_sample
        #print(" ".join(self.words))  # for demonstration purposes, replace with actual display method
        self.word_index_edit.setText(str(self.word_index))
        print(words_per_sample * self.samples_per_minute_slider.value())

    def seek(self):
        word_index = int(self.word_index_edit.text())
        if word_index < 0 or word_index >= len(self.words):
            return
        self.word_index = word_index
        self.display_next_words()

    def adjust_font(self):
            if self.paused:
                self.text_label.setText("")
            font = self.text_label.font()
            font_metrics = QFontMetrics(font)
            words_per_sample_value = self.words_per_sample_slider.value()
            self.words_per_sample_label.setText("Words per Sample: (1-30):          " + str(words_per_sample_value))
            text = " ".join(["a"*18 for i in range(words_per_sample_value)])
            text_rect = font_metrics.boundingRect(text)
            new_font_size = self.text_label.width() / (text_rect.width()/font.pointSizeF())
            font.setPointSizeF(new_font_size)
            self.text_label.setFont(font)
    
    def update_interval(self):
        samples_per_minute = self.samples_per_minute_slider.value()
        self.samples_per_minute_label.setText("Samples per Minute: (1-1000):   " + str(samples_per_minute))
        interval = 60000 / samples_per_minute
        self.timer.setInterval(interval)

    def resizeEvent(self, event):
        self.adjust_font()


    # def show(self):
    #     super().show()
    #     self.adjust_font()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = TextPlayer()
    player.show()
    sys.exit(app.exec_())
    
