#!/usr/bin/env python3

from PyQt5.QtWidgets import (QHBoxLayout, QWidget, QTreeView, QMainWindow)

import eds
import od


class CANopyner(QMainWindow):
    def __init__(self, file=None, parent=None):
        super(CANopyner, self).__init__(parent)

        self.window = QWidget(self)
        self.hl = QHBoxLayout(self.window)
        self.tree = QTreeView()
        self.hl.addWidget(self.tree)

        if file is not None:
            self.od = eds.parse(file)
            #TODO   don't sort here...
            self.od.children.sort()
            for child in self.od.children:
                #TODO   don't sort here...
                child.children.sort()
            self.model = od.ObjectDictionaryModel(self.od)
        else:
            self.model = TreeModel()

        self.tree.setModel(self.model)
        self.resize(500, 500)
        self.setCentralWidget(self.window)


if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    canopyner = CANopyner(file=sys.argv[1])
    canopyner.show()

    sys.exit(app.exec_())
