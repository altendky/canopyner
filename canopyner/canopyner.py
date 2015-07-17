#!/usr/bin/env python3

from PyQt5.QtCore import (Qt, QAbstractItemModel, QVariant, QModelIndex)
from PyQt5.QtWidgets import (QHBoxLayout, QWidget, QTreeView, QMainWindow)
import eds
import od


class TreeNode():
    def __init__(self, a, b, c, parent=None):
        self.a = a
        self.b = b
        self.c = c

        self.parent = parent
        self.children = []

        self.set_parent(parent)

    def set_parent(self, parent):
        self.parent = parent
        if self.parent is not None:
            self.parent.append_child(self)

    def append_child(self, child):
        self.children.append(child)

    def child_at_row(self, row):
        return self.children[row]

    def row_of_child(self, child):
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1

    def remove_child(self, row):
        value = self.children[row]
        self.children.remove(value)

        return True

    def __len__(self):
        return len(self.children)


class TreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)

        self.treeView = parent
        self.headers = ['Col A', 'Col B', 'Col C']

        # TODO   shouldn't this be calculated on the fly in case it changes?
        self.columns = len(self.headers)

        self.root = None

        # TODO   really fill, or at least don't dummy fill here
        self.dummy_fill()

    def dummy_fill(self):
        self.root = TreeNode('A', 'B', 'C')
        self.root_1 = TreeNode('1', '0', '0', self.root)
        self.root_1_1 = TreeNode('1', '1', '0', self.root_1)
        self.root_1_2 = TreeNode('1', '2', '0', self.root_1)
        self.root_1_2_1 = TreeNode('1', '2', '1', self.root_1_2)
        self.root_1_2_2 = TreeNode('1', '2', '2', self.root_1_2)
        self.root_1_3 = TreeNode('1', '3', '0', self.root_1)
        self.root_2 = TreeNode('2', '0', '0', self.root)
        self.root_3 = TreeNode('3', '0', '0', self.root)

    def header_data(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headers[section])
        return QVariant()

    def index(self, row, column, parent):
        node = self.node_from_index(parent)
        return self.createIndex(row, column, node.child_at_row(row))

    def data(self, index, role):
        if role == Qt.DecorationRole:
            return QVariant()

        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop | Qt.AlignLeft))

        if role != Qt.DisplayRole:
            return QVariant()

        node = self.node_from_index(index)

        if index.column() == 0:
            return QVariant(node.a)

        elif index.column() == 1:
            return QVariant(node.b)

        elif index.column() == 2:
            return QVariant(node.c)
        else:
            return QVariant()

    def columnCount(self, parent):
        return self.columns

    def rowCount(self, parent):
        node = self.node_from_index(parent)
        if node is None:
            return 0
        return len(node)

    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        node = self.node_from_index(child)

        if node is None:
            return QModelIndex()

        parent = node.parent

        if parent is None:
            return QModelIndex()

        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.row_of_child(parent)

        assert row != - 1
        return self.createIndex(row, 0, parent)

    def node_from_index(self, index):
        return index.internalPointer() if index.isValid() else self.root


class CANopyner(QMainWindow):
    def __init__(self, file=None, parent=None):
        super(CANopyner, self).__init__(parent)

        self.window = QWidget(self)
        # self.dock = QDockWidget("a docker", self)
        self.hl = QHBoxLayout(self.window)
        # self.dock.setLayout(self.hl)
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
        # self.tree.expandAll()
        # self.tree.resize(300,300)
        # self.dock.resize(400,400)
        self.resize(500, 500)
        self.setCentralWidget(self.window)
        # self.setCentralWidget(self.hl)
        # self.tree.setRootIndex(self.model.index(TreeNode('A', 'B', 'C')))
        # self.tree.setRoot(self.model.root)


if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    #    addressBook = AddressBook()
    #    addressBook.show()
    # mw = QMainWindow()
    # hl = QHBoxLayout()
    canopyner = CANopyner(file=sys.argv[1])
    # canopyner.resize(300,300)
    canopyner.show()
    # hl.addWidget(canopyner)
    # hl.show()
    # mw.setCentralWidget(hl)
    # mw.show()

    #    model = QFileSystemModel()
    #    home_path = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
    #    print(home_path)
    #    root_index = model.setRootPath(home_path)
    #
    #    tree = QTreeView()
    #    tree.setModel(model)
    #    tree.setRootIndex(root_index)
    #    tree.show()

    sys.exit(app.exec_())
