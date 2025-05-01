from PySide6.QtCore import Qt, Property, QSortFilterProxyModel, Signal


class ActionListTypeFilter(QSortFilterProxyModel):
    '''
    # NOTE must use setSourceModel on object when created
    Filter for model that only allows actions with status matching the logic conditions through
    '''
    filterEnabledChanged = Signal()

    def __init__(self, filter_items = [], parent=None):
        '''
        Filter_items is a list of strings to compare to the name of the action point associated with the action item
        '''
        super().__init__(parent)
        self.m_filterEnabled = True
        self.filter_items = filter_items

    def filterAcceptsRow(self, source_row, source_parent):
        '''
        Filter
        '''
        index = self.sourceModel().index(source_row, 0, source_parent)

        actionType = index.data(role=Qt.ItemDataRole.EditRole).actionPoint.name # index.data() calls the model data function at the given index

        if actionType in self.filter_items:
            return True
        return False


    def filterEnabled(self):
        return self.m_filterEnabled

    def setFilterEnabled(self, enabled):
        if self.m_filterEnabled == enabled:
            return

        self.m_filterEnabled = enabled
        self.filterEnabledChanged.emit()
        self.invalidateFilter()

    def updateFilterItems(self, filter_items):
        self.filter_items = filter_items
        self.invalidateFilter()

    filterEnabled = Property(type=bool, fget=filterEnabled, fset=setFilterEnabled, notify=filterEnabledChanged)
