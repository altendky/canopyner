#!/usr/bin/env python3

from PyQt5.QtWidgets import QMainWindow

import eds
import od
from generated.canopyner_ui import Ui_MainWindow


class CANopyner(QMainWindow):
    def __init__(self, file=None, parent=None):
        super(CANopyner, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        if file is not None:
            self.od = eds.parse(file)
            # TODO   don't sort here...
            self.od.children.sort()
            for child in self.od.children:
                # TODO   don't sort here...
                child.children.sort()
            self.model = od.ObjectDictionaryModel(self.od)
        else:
            self.model = TreeModel()

        self.ui.tree.setModel(self.model)

        self.ui.tree.clicked.connect(self.item_clicked)

    def item_clicked(self, index):
        self.ui.label.setText(str(index.model().node_from_index(index)))


if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    canopyner = CANopyner(file=sys.argv[1])
    canopyner.show()

    sys.exit(app.exec_())
