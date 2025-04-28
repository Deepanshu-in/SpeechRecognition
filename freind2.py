import sys, json, os, threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QListWidget, QLineEdit, QPushButton, QMessageBox, QLabel, QHBoxLayout
from PyQt5.QtCore import QStringListModel
from PyQt5.QtWidgets import QCompleter

DATA_FILE = 'friends.json'

# Load friends list from JSON file
def load_friends():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print("File load mein truti:", e)
    return []

# Save friends list to JSON file asynchronously
def save_friends(friends):
    def save():
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(friends, f, indent=4)
        except Exception as e:
            print("File save mein truti:", e)
    threading.Thread(target=save).start()

class MitraPrabandhakPyQt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mitra Prabandhak - PyQt5")
        self.sampurn_mitra = load_friends()  # Load all friends
        self.chhanti_mitra = self.sampurn_mitra.copy()  # Filtered friends list
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Search field with auto-complete feature
        khoj_layout = QHBoxLayout()
        khoj_label = QLabel("Mitra Khoj:")
        khoj_layout.addWidget(khoj_label)
        self.khoj_field = QLineEdit()
        khoj_layout.addWidget(self.khoj_field)
        layout.addLayout(khoj_layout)
        self.khoj_field.textChanged.connect(self.update_filter)

        self.completer = QCompleter(self.sampurn_mitra)
        self.completer.setCaseSensitivity(False)
        self.khoj_field.setCompleter(self.completer)

        # List widget to display friends
        self.suchilist = QListWidget()
        layout.addWidget(self.suchilist)

        # Input field to add a new friend
        jod_layout = QHBoxLayout()
        jod_label = QLabel("Naya Mitra Jodne:")
        jod_layout.addWidget(jod_label)
        self.jod_field = QLineEdit()
        jod_layout.addWidget(self.jod_field)
        layout.addLayout(jod_layout)

        # Buttons to add and remove friends
        button_layout = QHBoxLayout()
        self.jod_button = QPushButton("Mitra Jodo")
        self.jod_button.clicked.connect(self.add_mitra)
        button_layout.addWidget(self.jod_button)
        self.hatao_button = QPushButton("Mitra Hatao")
        self.hatao_button.clicked.connect(self.remove_mitra)
        button_layout.addWidget(self.hatao_button)
        layout.addLayout(button_layout)

        central_widget.setLayout(layout)
        self.refresh_list()

    # Filter friends based on search input
    def update_filter(self):
        query = self.khoj_field.text().strip().lower()
        if query == "":
            self.chhanti_mitra = self.sampurn_mitra.copy()
        else:
            self.chhanti_mitra = [m for m in self.sampurn_mitra if query in m.lower()]
        self.refresh_list()
        self.completer.model().setStringList(self.sampurn_mitra)

    # Refresh the friends list display
    def refresh_list(self):
        self.suchilist.clear()
        self.suchilist.addItems(self.chhanti_mitra)

    # Add a new friend to the list
    def add_mitra(self):
        mitra_naam = self.jod_field.text().strip()
        if mitra_naam == "":
            QMessageBox.critical(self, "Pravesh Truti", "Mitra naam khaali nahin ho sakta!")
            return
        if mitra_naam in self.sampurn_mitra:
            QMessageBox.critical(self, "Dohrav Truti", "Mitra pahle se maujood hai!")
            return
        self.sampurn_mitra.append(mitra_naam)
        save_friends(self.sampurn_mitra)
        self.jod_field.clear()
        self.update_filter()

    # Remove a selected friend from the list
    def remove_mitra(self):
        selected_items = self.suchilist.selectedItems()
        if not selected_items:
            QMessageBox.critical(self, "Chayan Truti", "Koi mitra chayan nahin hua hai!")
            return
        mitra_naam = selected_items[0].text()
        self.sampurn_mitra.remove(mitra_naam)
        save_friends(self.sampurn_mitra)
        self.update_filter()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MitraPrabandhakPyQt()
    window.show()
    sys.exit(app.exec_())
