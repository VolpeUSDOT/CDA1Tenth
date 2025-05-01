from PortDrayageInteractiveTabs.actionDelegate import ActionDelegate
from PySide6.QtWidgets import QAbstractItemView, QListView

class PendingActionView(QListView):
    '''
    Subclass of list view for showing a list of editable action items
    '''
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setUniformItemSizes(True)
        self.setItemDelegate(ActionDelegate())
        # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)


class CompletedActionView(QListView):
    '''
    Subclass of list view for showing a list of immutable, completed action items
    '''
    def __init__(self):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setUniformItemSizes(True)
        # self.setItemDelegate(ActionDelegate())
        # self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
