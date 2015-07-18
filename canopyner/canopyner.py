#!/usr/bin/env python3

from PyQt5.QtWidgets import (QHBoxLayout, QWidget, QTreeView, QMainWindow,
                             QDockWidget)

from PyQt5.QtCore import Qt
import eds
import od


class CANopyner(QMainWindow):
    def __init__(self, file=None, parent=None):
        super(CANopyner, self).__init__(parent)

        self.setDockOptions(
            QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)

        self.od_dock = QDockWidget("OD", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.od_dock)

        self.tree = QTreeView()
        self.od_dock.setWidget(self.tree)

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

        self.tree.setModel(self.model)
        self.resize(500, 500)

        self.tree.clicked.connect(self.model.item_clicked)


if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    canopyner = CANopyner(file=sys.argv[1])
    canopyner.show()

    sys.exit(app.exec_())
