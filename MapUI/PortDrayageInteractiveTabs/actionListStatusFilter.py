
from PySide6.QtCore import Qt, Property, QSortFilterProxyModel, Signal
from typing import Literal

class ActionListStatusFilter(QSortFilterProxyModel):
    '''
    # NOTE must use setSourceModel on object when created
    Filter for model that only allows actions with status matching the logic conditions through
    '''
    filterEnabledChanged = Signal()

    def __init__(self, mode: Literal["Equals", "Does Not Equal"], filter_str, parent=None):
        super().__init__(parent)
        self.m_filterEnabled = True
        self.filter_str = filter_str
        if mode == "Equals":
            self.equals_logic = True
        elif mode == "Does Not Equal":
            self.equals_logic = False
        else: raise ValueError("Invalid Mode selected for ActionProxyModel")


    def filterAcceptsRow(self, source_row, source_parent):
        '''
        Filter
        '''
        index = self.sourceModel().index(source_row, 0, source_parent)

        actionStatus = index.data(role=Qt.ItemDataRole.EditRole).status # index.data() calls the model data function at the given index

        if self.equals_logic:
            return (actionStatus == self.filter_str)
        return (actionStatus != self.filter_str)

    def filterEnabled(self):
        return self.m_filterEnabled

    def setFilterEnabled(self, enabled):
        if self.m_filterEnabled == enabled:
            return

        self.m_filterEnabled = enabled
        self.filterEnabledChanged.emit()
        self.invalidateFilter()

    filterEnabled = Property(type=bool, fget=filterEnabled, fset=setFilterEnabled, notify=filterEnabledChanged)
