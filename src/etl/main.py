import logging
import sys

from PyQt5.QtWidgets import QApplication
from controller import ETLController

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = ETLController()
    sys.exit(app.exec_())
