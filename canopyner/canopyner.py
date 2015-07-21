#!/usr/bin/env python3

from collections import OrderedDict

from PyQt5.QtWidgets import QMainWindow, QFileDialog

import eds
import od
from generated.canopyner_ui import Ui_MainWindow


class CANopyner(QMainWindow):
    def __init__(self, file=None, parent=None):
        super(CANopyner, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(self.__class__.__name__)

        self.od = None
        self.model = None
        if file is not None:
            self.import_od(file)

        self.ui.tree.clicked.connect(self.item_clicked)
        self.ui.actionImport_Object_Dictionary.triggered.connect(self.import_od)

    def item_clicked(self, index):
        node = index.model().node_from_index(index)
        self.ui.label.setText(str(node))
        self.od.sdo_read(node)

    def import_od(self, checked=False, file=None):
        print(file)
        if file is None:
            types = OrderedDict()
            types['Electronic Data Sheet'] = ['eds']
            # TODO  add XDD support
            # types['XDD'] = ['xdd']

            filters = []
            for name, extensions in types.items():
                ext = ', '.join(['*.' + e for e in extensions])
                filters.append('{n} ({e}) ({e})'.format(n=name, e=ext))
            print(';;'.join(filters))

            file = QFileDialog.getOpenFileName(self, 'Open Object Dictionary',
                                               filter=';;'.join(filters))[0]
            file = file if len(file) > 0 else None

        if file is not None:
            self.od = eds.parse(file)
            # TODO   don't sort here...
            self.od.children.sort()
            for child in self.od.children:
                # TODO   don't sort here...
                child.children.sort()
            self.model = od.ObjectDictionaryModel(self.od)

            self.ui.tree.setModel(self.model)

            self.ui.nodeid.valueChanged.connect(self.od.set_node_id)
            self.od.set_node_id(self.ui.nodeid.value())
            self.od.changed.connect(self.model.changed)


if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    canopyner = CANopyner()
    canopyner.show()

    sys.exit(app.exec_())
