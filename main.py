from PyQt5.QtWidgets import QApplication
from src.statswing_utils import load_data
from src.statswing_gui import StatSwingApp
import sys

if __name__ == "__main__":
    data = load_data("data/player_data.csv")
    app = QApplication(sys.argv)
    window = StatSwingApp(data)
    window.show()
    sys.exit(app.exec_())