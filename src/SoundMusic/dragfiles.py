# pylint: skip-file
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit

# reference taken from : http://stackoverflow.com/questions/11872141/drag-a-file-into-qtgui-qlineedit-to-set-url-text

class lineEdit_dragFile_injector():
    def __init__(self, lineEdit, auto_inject = True):
        self.lineEdit = lineEdit
        if auto_inject:
            self.inject_dragFile()

    def inject_dragFile( self ):
        self.lineEdit.setDragEnabled(True)
        self.lineEdit.dragEnterEvent = self._dragEnterEvent
        self.lineEdit.dragMoveEvent = self._dragMoveEvent
        self.lineEdit.dropEvent = self._dropEvent

    def _dragEnterEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            event.acceptProposedAction()

    def _dragMoveEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            event.acceptProposedAction()

    def _dropEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            # for some reason, this doubles up the intro slash
            filepath = str(urls[0].path())[1:]
            self.lineEdit.setText(filepath)