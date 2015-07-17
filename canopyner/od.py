#!/usr/bin/env python3

from PyQt5.QtCore import (Qt, QAbstractItemModel, QVariant, QModelIndex)


def to_int(value):
    try:
        return int(value, 0)
    except TypeError as e:
        if str(e) == "int() can't convert non-string with explicit base":
            return int(value)
        else:
            raise


class TreeNode:
    def __init__(self, index, name, parent=None):
        self.index = index
        self.name = name

        self.parent = None
        self.set_parent(parent)
        self.children = []

    def set_parent(self, parent):
        self.parent = parent
        if self.parent is not None:
            self.parent.append_child(self)

    def append_child(self, child):
        self.children.append(child)
        child.parent = self

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


class Subindex(TreeNode):
    def __init__(self, subindex, name, parent=None):
        super(Subindex, self).__init__(str(subindex), name, parent)

        if isinstance(subindex, int):
            self.subindex = subindex
        else:
            raise TypeError

    def index_str(self):
        return self.index

    def __str__(self):
        return str(self.subindex)

    def __lt__(self, other):
        return self.subindex < other.subindex


class Index(TreeNode):
    def __init__(self, index, name, parent=None):
        super(Index, self).__init__(hex(index), name, parent)
        # TODO   check valid index range
        self.index = to_int(index)
        # TODO   also store type

        # self.subindexes = []#[Subindex() for i in range(0, subindexes)]

        # TODO   yep, do something more here
        self.value = 0

    def add_subindex(self, subindex):
        if isinstance(subindex, Subindex):
            # self.subindexes.append(subindex)
            self.append_child(subindex)
        else:
            raise TypeError('Must be a Subindex')

    def index_str(self):
        return hex(self.index)

    # def get(self, subindex=0):
    #     return self.subindexes[subindex]

    def __str__(self):
        s = hex(self.index).lstrip('0x').zfill(4).upper()
        s += ' ' + ('y' if self.pdomapping else 'n')
        if len(self.name) > 0:
            s += ' <' + self.name + '>'
        if len(self) > 0:
            s += ' (' + ', '.join([str(si) for si in self.children]) + ')'

        return s

    def __lt__(self, other):
        return self.index < other.index


class ObjectDictionary(TreeNode):
    def __init__(self, name, parent=None):
        super(ObjectDictionary, self).__init__('', name, parent)

    def add_index(self, index):
        if isinstance(index, Index):
            # self.indexes.append(index)
            self.append_child(index)
        else:
            raise TypeError('Must be a Subindex')

    def __str__(self):
        return 'Indexes: \n' + '\n'.join([str(i) for i in self.children])


class ObjectDictionaryModel(QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(ObjectDictionaryModel, self).__init__(parent)

        self.root = root
        self.headers = ['Index', 'Name']
        self.columns = len(self.headers)

    def header_data(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headers[section])
        return QVariant()

    def index(self, row, column, parent):
        node = self.node_from_index(parent)
        return self.createIndex(row, column, node.child_at_row(row))
        # if not parent.isValid():
        #     parent_item = self.root
        # else:
        #     parent_item = parent.internalPointer()
        #
        # child_item = parent_item.children[row]
        # if child_item:
        #     return self.createIndex(row, column, child_item)
        # else:
        #     return QModelIndex()

    def data(self, index, role):
        if role == Qt.DecorationRole:
            return QVariant()

        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignTop | Qt.AlignLeft))

        if role != Qt.DisplayRole:
            return QVariant()

        node = self.node_from_index(index)

        if index.column() == 0:
            return QVariant(node.index_str())

        elif index.column() == 1:
            return QVariant(node.name)

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
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root
        return index.internalPointer() if index.isValid() else self.root


# TODO   implement QAbstractItemModel

class TreeModel(QAbstractItemModel):
    def __init__(self, od, parent=None):
        super(TreeModel, self).__init__(parent)

        #TODO   check od type?
        self.od = od

        self.treeView = parent
        self.headers = ['Col A', 'Col B', 'Col C']

        # TODO   shouldn't this be calculated on the fly in case it changes?
        self.columns = len(self.headers)

        self.root = None

        # TODO   really fill, or at least don't dummy fill here
        self.dummy_fill()

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
        # frameinfo = getframeinfo(currentframe());print(frameinfo.filename, frameinfo.function, frameinfo.lineno)
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


if __name__ == '__main__':
    import sys

    eds = Eds(sys.argv[1])
    print(eds)

    sys.exit(0)