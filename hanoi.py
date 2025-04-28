
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QRect, QPoint

class TowerOfHanoiWidget(QWidget):
    """
    हनोई टॉवर खेल का क्रियान्वयन PyQt5 के साथ।
    इस खेल में आपको डिस्क को पहले टॉवर से तीसरे टॉवर पर स्थानांतरित करना है,
    बिना किसी बड़ी डिस्क को छोटी डिस्क पर रखे।
    """
    def __init__(self, parent):
        """
        खेल को आरंभ करने का कार्य।
        
        प्राचल:
            parent: मूल विजेट
        """
        super().__init__(parent)
        self.num_discs = 3
        self.towers = [[], [], []]  # तीन टॉवर जिनमें डिस्क आईडी संग्रहित होंगे
        self.disc_sizes = {}  # प्रत्येक डिस्क की चौड़ाई संग्रहित करने के लिए शब्दकोश
        self.selected_disc = None  # वर्तमान में चयनित डिस्क
        self.selected_tower = None  # जिस टॉवर से डिस्क उठाया गया है
        self.drag_pos = None  # खींचने की स्थिति
        self.moves_count = 0  # चालों की गिनती के लिए
        
        # प्रारंभिक डिस्क बनाना
        self.create_discs()
        
        # माउस क्रियाओं को संभालने के लिए
        self.setMouseTracking(True)

    def create_discs(self):
        """प्रारंभ में सभी डिस्क पहले टॉवर पर बनाता है"""
        initial_width = 100
        
        for i in range(self.num_discs):
            disc_width = initial_width - i * 20  # छोटी डिस्क के लिए चौड़ाई कम करना
            disc_id = i + 1  # डिस्क का अद्वितीय आईडी
            self.towers[0].append(disc_id)  # पहले टॉवर पर डिस्क जोड़ना
            self.disc_sizes[disc_id] = disc_width  # डिस्क की चौड़ाई संग्रहित करना

    def paintEvent(self, event):
        """
        विजेट को चित्रित करने का कार्य
        
        प्राचल:
            event: चित्रण घटना
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # पृष्ठभूमि
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # टॉवर चित्रित करना
        self.draw_towers(painter)
        
        # डिस्क चित्रित करना
        self.draw_discs(painter)
        
        # चयनित डिस्क को खींचने की स्थिति पर चित्रित करना
        if self.selected_disc is not None and self.drag_pos is not None:
            self.draw_moving_disc(painter)

    def draw_towers(self, painter):
        """
        तीन टॉवर को चित्रित करना
        
        प्राचल:
            painter: QPainter वस्तु
        """
        painter.setPen(QPen(QColor(0, 0, 0), 10))
        
        for i in range(3):
            x = 150 + i * 200
            painter.drawLine(x, 350, x, 100)
        
        # आधार चित्रित करना
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(150, 75, 0)))
        painter.drawRect(50, 350, 500, 20)

    def draw_discs(self, painter):
        """
        सभी डिस्क को उनके टॉवर पर चित्रित करना
        
        प्राचल:
            painter: QPainter वस्तु
        """
        for tower_idx, tower in enumerate(self.towers):
            for disc_idx, disc_id in enumerate(tower):
                # अगर चयनित डिस्क है तो छोड़ना (वह अलग से खींचने की स्थिति पर चित्रित होगी)
                if self.selected_disc == disc_id and self.selected_tower == tower_idx:
                    continue
                
                x = 150 + tower_idx * 200
                disc_width = self.disc_sizes[disc_id]
                y = 350 - (disc_idx + 1) * 20
                
                self.draw_disc(painter, disc_id, x - disc_width/2, y)

    def draw_disc(self, painter, disc_id, x, y):
        """
        एक डिस्क को चित्रित करना
        
        प्राचल:
            painter: QPainter वस्तु
            disc_id: डिस्क का आईडी
            x: डिस्क के शीर्ष-बाएँ कोने का x निर्देशांक
            y: डिस्क के शीर्ष-बाएँ कोने का y निर्देशांक
        """
        disc_width = self.disc_sizes[disc_id]
        disc_height = 20
        
        # डिस्क का रंग चुनना - आईडी के अनुसार
        color = self.get_disc_color(disc_id - 1)
        
        painter.setPen(QPen(Qt.black, 1))
        painter.setBrush(QBrush(color))
        painter.drawRect(int(x), int(y), int(disc_width), int(disc_height))

    def draw_moving_disc(self, painter):
        """
        चलती हुई डिस्क को वर्तमान खींचने की स्थिति पर चित्रित करना
        
        प्राचल:
            painter: QPainter वस्तु
        """
        if self.selected_disc is not None and self.drag_pos is not None:
            disc_width = self.disc_sizes[self.selected_disc]
            x = self.drag_pos.x() - disc_width/2
            y = self.drag_pos.y() - 10  # 10 डिस्क ऊंचाई का आधा है
            
            self.draw_disc(painter, self.selected_disc, x, y)

    def get_disc_color(self, index):
        """
        डिस्क के लिए QColor वस्तु लौटाता है 
        
        प्राचल:
            index: डिस्क का अनुक्रमांक
            
        प्रतिफल:
            QColor: डिस्क का रंग
        """
        colors = [
            QColor(255, 87, 51),   # #FF5733
            QColor(255, 195, 0),   # #FFC300
            QColor(54, 207, 255),  # #36CFFF
             ] 
        return colors[index % len(colors)]

    def mousePressEvent(self, event):
        """
        माउस दबाने की घटना नियंत्रक
        
        प्राचल:
            event: माउस घटना
        """
        if event.button() == Qt.LeftButton:
            # जांचना कि किसी टॉवर की शीर्ष डिस्क पर क्लिक हुआ है या नहीं
            for tower_idx, tower in enumerate(self.towers):
                if tower:  # अगर टॉवर में डिस्क है
                    top_disc_id = tower[-1]
                    x = 150 + tower_idx * 200
                    disc_width = self.disc_sizes[top_disc_id]
                    y = 350 - len(tower) * 20
                    
                    # जांचना कि क्लिक डिस्क के क्षेत्र में हुआ है या नहीं
                    if (x - disc_width/2 <= event.x() <= x + disc_width/2 and
                        y <= event.y() <= y + 20):
                        self.selected_disc = top_disc_id
                        self.selected_tower = tower_idx
                        self.drag_pos = event.pos()
                        self.update()
                        break

    def mouseMoveEvent(self, event):
        """
        माउस हलचल की घटना नियंत्रक
        
        प्राचल:
            event: माउस घटना
        """
        if self.selected_disc is not None:
            self.drag_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """
        माउस छोड़ने की घटना नियंत्रक
        
        प्राचल:
            event: माउस घटना
        """
        if event.button() == Qt.LeftButton and self.selected_disc is not None:
            # पता लगाना कि डिस्क किस टॉवर पर छोड़ा गया
            target_tower = None
            for i in range(3):
                x = 150 + i * 200
                if x - 50 <= event.x() <= x + 50:
                    target_tower = i
                    break

            if target_tower is not None:
                # जांचना कि चाल वैध है या नहीं
                is_valid = True
                if self.towers[target_tower]:
                    top_disc = self.towers[target_tower][-1]
                    # आकारों की तुलना करना
                    if self.disc_sizes[self.selected_disc] > self.disc_sizes[top_disc]:
                        is_valid = False

                if is_valid:
                    # डिस्क को नए टॉवर पर स्थानांतरित करना
                    self.towers[self.selected_tower].remove(self.selected_disc)
                    self.towers[target_tower].append(self.selected_disc)
                    
                    # चाल की गिनती अद्यतन करना
                    self.moves_count += 1
                    self.parent().update_moves_count(self.moves_count)
                    
                    # जांचना कि खेल पूरा हुआ है या नहीं
                    self.check_win()
            
            # चयन रीसेट करना
            self.selected_disc = None
            self.selected_tower = None
            self.drag_pos = None
            self.update()

    def check_win(self):
        """जांचना कि खेल पूरा हुआ है या नहीं"""
        # जांचना कि सभी डिस्क तीसरे टॉवर पर हैं
        if len(self.towers[2]) == self.num_discs:
            # सफलता संदेश और चालों की गिनती के साथ
            QMessageBox.information(self, "बधाई हो!", 
                                   f"आपने हनोई टॉवर खेल को {self.moves_count} चालों में हल कर लिया है!")
            
            # नए खेल का विकल्प
            play_again = QMessageBox.question(self, "फिर से खेलें?", 
                                             "क्या आप दोबारा खेलना चाहते हैं?",
                                             QMessageBox.Yes | QMessageBox.No)
            if play_again == QMessageBox.Yes:
                # खेल रीसेट करना
                self.reset_game()
            else:
                QApplication.quit()

    def reset_game(self):
        """खेल को रीसेट करने का कार्य"""
        # चर को रीसेट करना
        self.towers = [[], [], []]
        self.disc_sizes = {}
        self.selected_disc = None
        self.selected_tower = None
        self.drag_pos = None
        self.moves_count = 0
        
        # मूल विंडो को अद्यतन करना
        self.parent().update_moves_count(0)
        
        # डिस्क को फिर से बनाना
        self.create_discs()
        
        # पुनः चित्रित करना
        self.update()


class TowerOfHanoiWindow(QMainWindow):
    """हनोई टॉवर खेल के लिए मुख्य विंडो"""
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("हनोई का टॉवर")
        self.setGeometry(100, 100, 600, 450)
        
        # खेल विजेट को स्थापित करना
        self.game_widget = TowerOfHanoiWidget(self)
        self.setCentralWidget(self.game_widget)
        
        # चालों की गिनती बनाना
        self.moves_label = QLabel("चाल: 0", self)
        self.moves_label.setGeometry(250, 380, 100, 30)
        
    def update_moves_count(self, count):
        """
        चालों की गिनती अद्यतन करना
        
        प्राचल:
            count: नई चालों की गिनती
        """
        self.moves_label.setText(f"चाल: {count}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TowerOfHanoiWindow()
    window.show()
    sys.exit(app.exec_())