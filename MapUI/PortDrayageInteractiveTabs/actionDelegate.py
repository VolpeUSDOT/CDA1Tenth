from PortDrayageInteractiveTabs.actionEditor import ActionEditor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStyledItemDelegate

class ActionDelegate(QStyledItemDelegate):
    '''
    Creates an alternate, interactable and editable view for items in the model and connects the data in the temporary editor with the model
    '''
    def __init__(self, parent=None):
        super().__init__(parent)

    def sizeHint(self, option, index):
        editor = ActionEditor(None)
        return editor.sizeHint()

    def createEditor(self, parent, option, index):
        editor = ActionEditor(parent)
        # Connect the dataChanged signal from each item to update the backend model data
        editor.actionDataChanged.connect(self.commit_from_editor) # TODO Might need to lose this line
        return editor

    def setEditorData(self, editor, index):
        editor.setValue(index.data(role=Qt.ItemDataRole.EditRole))
        editor.actionDataChanged.connect(self.commit_from_editor) # TODO Might need to lose this line

    def setModelData(self, editor, model, index):
        model.setData(index, editor.m_action_data)

    def commit_from_editor(self):
        '''
        Commits the data to the model and closes the editor
        '''
        editor = self.sender()
        # The commitData signal must be emitted when we've finished editing
        # and need to write our changed back to the model.
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)

    def updateEditorGeometry(self, editor, option, index):
        return super().updateEditorGeometry(editor, option, index)
