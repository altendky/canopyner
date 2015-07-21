#!/usr/bin/env python3

from PyQt5.QtCore import (Qt, QObject, QAbstractItemModel, QVariant,
                          QModelIndex, pyqtSignal)

import can


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

        # TODO   yep, do something more here
        self.value = 0

        if isinstance(subindex, int):
            self.subindex = subindex
        else:
            raise TypeError

    def index_str(self):
        return self.index

    def unique(self):
        # TODO  stop CAMPing, see 09824098098092045
        return self.parent.unique() + ':' + str(self.subindex).zfill(3)

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

        # TODO   yep, do something more here
        self.value = 0

        self.pdo_mapping = None

    def add_subindex(self, subindex):
        if isinstance(subindex, Subindex):
            # self.subindexes.append(subindex)
            self.append_child(subindex)
        else:
            raise TypeError('Must be a Subindex')

    def index_str(self):
        return hex(self.index)

    def __str__(self):
        # TODO  stop CAMPing, see 09824098098092045
        s = hex(self.index).lstrip('0x').zfill(4).upper()
        s += ' ' + ('y' if self.pdo_mapping else 'n')
        s += ' ' + '(' + str(self.value) + ')'
        if len(self.name) > 0:
            s += ' <' + self.name + '>'
        if len(self) > 0:
            s += ' (' + ', '.join([str(si) for si in self.children]) + ')'

        return s

    def unique(self):
        # TODO  stop CAMPing, see 09824098098092045
        return hex(self.index).lstrip('0x').zfill(4).upper()

    def __lt__(self, other):
        return self.index < other.index


class ObjectDictionary(TreeNode, can.Listener, QObject):
    changed = pyqtSignal(TreeNode, int)

    def __init__(self, name, node_id=None, parent=None):
        TreeNode.__init__(self, '', name, parent)
        QObject.__init__(self)

        self.node_id = node_id

        self.bus = can.interface.Bus(bustype='socketcan', channel='vcan0')
        self.notifier = can.Notifier(self.bus, [self])

    def add_index(self, index):
        if isinstance(index, Index):
            # self.indexes.append(index)
            self.append_child(index)
        else:
            raise TypeError('Must be a Subindex')

    def set_node_id(self, node_id):
        self.node_id = node_id

    def sdo_read(self, node):
        self.bus.send(
            ReadSdo(node=self.node_id, index=node.index).to_message())

    def on_message_received(self, msg):
        if self.node_id is None:
            return

        # TODO  yuck and the whole do we save sub0 to the
        #       index or subindex thing
        if not msg.id_type:
            if msg.arbitration_id == 0x600 + self.node_id:
                if len(msg.data) == 8:
                    if msg.data[0] == 0x43:
                        index = int.from_bytes(msg.data[1:3],
                                               byteorder='little')
                        subindex = int(msg.data[3])
                        value = int.from_bytes(msg.data[4:8],
                                               byteorder='little')
                        for i in self.children:
                            if i.index == index:
                                if subindex == 0:
                                    i.value = value
                                    self.changed.emit(i, 2)

                                for s in i.children:
                                    if s.subindex == subindex:
                                        s.value = value
                                        self.changed.emit(s, 2)
                                        break

                                break

    def unique(self):
        # TODO  actually identify the object dictionary
        return '-'

    def __str__(self):
        return 'Indexes: \n' + '\n'.join([str(i) for i in self.children])


class ObjectDictionaryModel(QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(ObjectDictionaryModel, self).__init__(parent)

        self.root = root
        self.headers = ['Index', 'Name', 'Value']
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

        # TODO  enumerate columns?
        if index.column() == 0:
            return QVariant(node.index_str())

        elif index.column() == 1:
            return QVariant(node.name)

        elif index.column() == 2:
            return QVariant(node.value)

        elif index.column() == 3:
            return QVariant(node.unique())

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

    def index_from_node(self, node):
        # TODO  make up another role for identification?
        return self.match(self.index(0, 3, QModelIndex()),
                          Qt.DisplayRole,
                          node.unique(),
                          1,
                          Qt.MatchRecursive)

    def changed(self, node, column):
        index = self.index_from_node(node)[0]
        index = self.index(index.row(), column, index.parent())
        self.dataChanged.emit(index, index)


class Sdo:
    def __init__(self, node, header, index, subindex=0, value=0):
        self.node = node
        self.header = header
        self.value = value
        self.index = index
        self.subindex = subindex

    def to_bus(self):
        data = [self.header]
        data.extend(self.index.to_bytes(2, byteorder='little'))
        data.extend(self.subindex.to_bytes(1, byteorder='little'))
        data.extend(self.value.to_bytes(4, byteorder='little'))

        return data

    def to_message(self):
        return can.Message(arbitration_id=0x580 + self.node, data=self.to_bus(),
                           extended_id=False)


class WriteSdo(Sdo):
    def __init__(self, node, value, index, subindex=0):
        super(WriteSdo, self).__init__(node=node, header=0x2B, index=index,
                                       value=value, subindex=subindex)


class ReadSdo(Sdo):
    def __init__(self, node, index, subindex=0):
        super(ReadSdo, self).__init__(node=node, header=0x40, index=index,
                                      value=0,
                                      subindex=subindex)


if __name__ == '__main__':
    import eds
    import sys

    print(eds.parse(sys.argv[1]))

    sys.exit(0)
