import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextBrowser, QAction, QFileDialog, QWidget, QMessageBox, QTextEdit,
                             QFontDialog, QColorDialog)
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QTextCursor, QPixmap, QKeySequence, QFont, QTextCharFormat
from PyQt5.QtCore import QFileInfo, Qt, QUrl
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from functools import partial
import summer_practice.res_rc
import webbrowser


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загрузка UI из файла
        uic.loadUi('main_practice_summer.ui', self)

        initial_font = QFont("Calibri", 11)
        self.textEdit.setFont(initial_font)

        self.actionImage.triggered.connect(self.insertImageAction)


        self.actionNew.triggered.connect(self.fileNew)
        self.actionNew_3.triggered.connect(self.fileNew)
        self.actionOpen_2.triggered.connect(self.openFile)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionSave_2.triggered.connect(self.saveFile)
        self.actionPrint_3.triggered.connect(self.printfile)
        self.actionPrint_2.triggered.connect(self.printfile)
        self.actionPrint_Preview.triggered.connect(self.printPreview)
        self.actionPrint_Preview_2.triggered.connect(self.printPreview)
        self.actionExport_PDF_2.triggered.connect(self.exportPDF)
        self.actionExport_PDF.triggered.connect(self.exportPDF)
        self.actionExit_3.triggered.connect(self.exitEditor)
        self.actionCopy_2.triggered.connect(self.copy)
        self.actionCopy.triggered.connect(self.copy)
        self.actionPaste_2.triggered.connect(self.paste)
        self.actionPaste.triggered.connect(self.paste)
        self.actionCut.triggered.connect(self.cut)
        self.actionCut_2.triggered.connect(self.cut)
        self.actionUndo.triggered.connect(self.textEdit.undo)
        self.actionUndo_2.triggered.connect(self.textEdit.undo)
        self.actionRedo.triggered.connect(self.textEdit.redo)
        self.actionRedo_2.triggered.connect(self.textEdit.redo)
        self.actionFont.triggered.connect(self.fontDialog)
        self.actionFont_2.triggered.connect(self.fontDialog)
        self.actionColor.triggered.connect(self.colorDialog)
        self.actionLeft_2.triggered.connect(self.setAlignment)
        self.actionCenter_2.triggered.connect(self.setAlignment)
        self.actionRight_2.triggered.connect(self.setAlignment)
        self.actionJustify.triggered.connect(self.setAlignment)

        #self.fontsize.currentIndexChanged[str].connect(lambda s: self.editor.setFontPointSize(float(s)))

        self.actionBold.setShortcut(QKeySequence.Bold)
        self.actionBold.setCheckable(True)
        self.actionBold.toggled.connect(lambda x: self.textEdit.setFontWeight(QFont.Bold if x else QFont.Normal))

        self.actionItalic.setShortcut(QKeySequence.Italic)
        self.actionItalic.setCheckable(True)
        self.actionItalic.toggled.connect(self.textEdit.setFontItalic)


        self.actionUnderline.setShortcut(QKeySequence.Underline)
        self.actionUnderline.setCheckable(True)
        self.actionUnderline.toggled.connect(self.textEdit.setFontUnderline)
        self.setInitialFont()

        self.actionLeft_2.setShortcut("CTRL+L")
        self.actionLeft_2.setCheckable(True)
        self.actionLeft_2.triggered.connect(partial(self.setAlignment, Qt.AlignLeft))

        self.actionCenter_2.setShortcut("CTRL+E")
        self.actionCenter_2.setCheckable(True)
        self.actionCenter_2.triggered.connect(partial(self.setAlignment, Qt.AlignCenter))

        self.actionRight_2.setShortcut("CTRL+R")
        self.actionRight_2.setCheckable(True)
        self.actionRight_2.triggered.connect(partial(self.setAlignment, Qt.AlignRight))

        self.actionJustify.setShortcut("CTRL+J")
        self.actionJustify.setCheckable(True)
        self.actionJustify.triggered.connect(partial(self.setAlignment, Qt.AlignJustify))

    def setAlignment(self, alignment):
        try:
            self.textEdit.setAlignment(alignment)

            if alignment == Qt.AlignLeft:
                self.actionCenter_2.setChecked(False)
                self.actionRight_2.setChecked(False)
                self.actionJustify.setChecked(False)

            elif alignment == Qt.AlignRight:
                self.actionLeft_2.setChecked(False)
                self.actionCenter_2.setChecked(False)
                self.actionJustify.setChecked(False)

            elif alignment == Qt.AlignCenter:
                self.actionRight_2.setChecked(False)
                self.actionLeft_2.setChecked(False)
                self.actionJustify.setChecked(False)

            elif alignment == Qt.AlignJustify:
                self.actiontRight_2.setChecked(False)
                self.actionLeft_2.setChecked(False)
                self.actionCenter_2.setChecked(False)
        except Exception as E:
            pass




    def setInitialFont(self):
        initial_font = QFont("Calibri", 14)
        self.textEdit.setFont(initial_font)


    def insertImageAction(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Выбрать изображение', '',
                                                   'Изображения (*.png *.jpg *.bmp *.gif)')
        if file_name:
            cursor = self.textEdit.textCursor()
            cursor.insertHtml('<img src="{}">'.format(file_name))

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
            text = self.textEdit.toPlainText()

            try:
                with open(filePath, 'w') as file:
                    file.write(text)
                QMessageBox.information(self, "Success", "The file has been saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"The file could not be saved: {str(e)}")

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '/home')

        if filename:
            with open(filename, 'r') as file:
                data = file.read()
                self.textEdit.setHtml(data)

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
        if fn:
            if not fn.endswith('.pdf'):
                fn += '.pdf'
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            self.textEdit.document().print_(printer)

    def exitEditor(self):
        result = QMessageBox.question(
            self,
            "Exit",
            "Do you really want to exit?",
            QMessageBox.No | QMessageBox.Yes
        )

        if result == QMessageBox.Yes:
            self.close()

    def copy(self):
        cursor = self.textEdit.textCursor()
        textSelected = cursor.selectedText()
        clipboard = QApplication.clipboard()
        clipboard.setText(textSelected)

    def paste(self):
        clipboard = QApplication.clipboard()
        textToPaste = clipboard.text()
        self.textEdit.insertPlainText(textToPaste)

    def cut(self):
        cursor = self.textEdit.textCursor()
        textSelected = cursor.selectedText()
        self.copiedText = textSelected
        self.textEdit.cut()

    def fontDialog(self):
        cursor = self.textEdit.textCursor()

        if cursor.hasSelection():
            font, ok = QFontDialog.getFont()

            if ok:
                format = QTextCharFormat()
                format.setFont(font)
                cursor.mergeCharFormat(format)

    def colorDialog(self):
        cursor = self.textEdit.textCursor()

        if cursor.hasSelection():
            color = QColorDialog.getColor()

            if color.isValid():
                format = QTextCharFormat()
                format.setForeground(color)
                cursor.mergeCharFormat(format)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ControlModifier:
                self.paste()
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec_())
