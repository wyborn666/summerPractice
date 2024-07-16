import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QComboBox, QMessageBox, QAction, QFileDialog, \
    QTextEdit
from PyQt5.QtGui import QFont
from PyQt5 import uic
from PyQt5 import QtGui
import summer_practice.res_rc
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from PyQt5.QtCore import QFileInfo


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_practice_summer.ui', self)

        self.actionNew.triggered.connect(self.fileNew)
        self.actionNew_3.triggered.connect(self.fileNew)

        self.actionOpen_2.triggered.connect(self.openFile)
        self.actionOpen.triggered.connect(self.openFile)

        self.actionSave_2.triggered.connect(self.saveFile)
        self.actionSave.triggered.connect(self.saveFile)

        self.actionPrint_3.triggered.connect(self.printfile)
        self.actionPrint_2.triggered.connect(self.printfile)

        self.actionPrint_Preview.triggered.connect(self.printPreview)
        self.actionPrint_Preview_2.triggered.connect(self.printPreview)

        self.actionExport_PDF.triggered.connect(self.exportPDF)
        self.actionExport_PDF_2.triggered.connect(self.exportPDF)

        self.actionExit_3.triggered.connect(self.exitEditor)

        self.actionCopy_2.triggered.connect(self.copy)
        self.actionCopy.triggered.connect(self.copy)

        self.actionPaste_2.triggered.connect(self.paste)
        self.actionPaste.triggered.connect(self.paste)
    def fileNew(self):
        result = QMessageBox.question(
            self,
            "Открытие нового файла",
            "Хотите сохранить изменения в файл?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if result == QMessageBox.Save:
            self.saveFile()

        elif result == QMessageBox.Discard:
            self.textEdit.clear()

        elif result == QMessageBox.Cancel:
            return

    def saveFile(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save file", "", "All files (*);;Texts files (*.txt)",
                                                  options=options)
        if filePath:
            text = self.findChild(QTextEdit, "textEdit").toPlainText()

            try:
                with open(filePath, 'w') as file:
                    file.write(text)
                QMessageBox.information(self, "Success", "The file has been saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"The file could not be saved: {str(e)}")

    def openFile(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', '/home')

        if filename[0]:
            f = open(filename[0], 'r')

            with f:
                data = f.read()

                self.textEdit.setText(data)

    def printfile(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec_() == QPrintDialog.Accepted:
            self.textEdit.print_(printer)

    def printPreview(self):
        printer = QPrinter(QPrinter.HighResolution)
        previewDialog = QPrintPreviewDialog(printer, self)
        previewDialog.paintRequested.connect(self.printDocument)
        previewDialog.exec_()

    def printDocument(self, printer):
        self.textEdit.print_(printer)

    def exportPDF(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Export PDF", None, "PDF files (.pdf) ;; All Files")
        if fn != "":
            if QFileInfo(fn).suffix() == "" :fn += '.pdf'
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            self.textEdit.document().print_(printer)


    def exitEditor(self):
        result = QMessageBox.question(
            self,
            "Exit",
            "Do you really want to get out?",
            QMessageBox.No | QMessageBox.Yes
        )

        if result == QMessageBox.Yes:
            self.close()
        else:
            return

    def copy(self):
        cursor = self.textEdit.textCursor()
        textSelected = cursor.selectedText()
        clipboard = QApplication.clipboard()
        clipboard.setText(textSelected)
        self.copiedText = textSelected

    def paste(self):
        clipboard = QApplication.clipboard()
        textToPaste = clipboard.text()
        self.textEdit.append(textToPaste)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec_())