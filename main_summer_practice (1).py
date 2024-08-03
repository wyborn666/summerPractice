import sys
import json
import typing

from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QFileDialog, QWidget, QMessageBox, QTextEdit,
                             QFontDialog, QColorDialog, QPushButton, QDialog, QComboBox, QLabel, QVBoxLayout, QInputDialog,
                             QSpinBox, QGridLayout, QLineEdit, QHBoxLayout, QScrollArea)
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtGui import QTextCursor, QPixmap, QKeySequence, QFont, QTextCharFormat, QColor, QTextBlockFormat,\
    QTextDocument, QBrush, QDesktopServices, QTextFrameFormat, QKeyEvent, QPaintEvent, QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import Qt, QUrl, QPoint, QRegExp, QEvent, QSizeF, QByteArray, QBuffer, QIODevice
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from functools import partial

from PyQt6.QtCore import QIODeviceBase
import res_rc
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib



class MarginsDialog(QDialog):
    DEFAULT_LINE_SPACING = 25

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(330, 220)
        self.setWindowTitle("Margins and Line spacing")

        layout = QVBoxLayout()

        self.leftMargin = QSpinBox()
        self.leftMargin.setRange(0, 100)
        layout.addWidget(QLabel("Left margin:"))
        layout.addWidget(self.leftMargin)

        self.rightMargin = QSpinBox()
        self.rightMargin.setRange(0, 100)
        layout.addWidget(QLabel("Right margin"))
        layout.addWidget(self.rightMargin)

        self.lineSpacing = QSpinBox()
        self.lineSpacing.setRange(0, 100)
        self.lineSpacing.setValue(0)  # Установка значения по умолчанию в 0
        layout.addWidget(QLabel("Line spacing(25 = 0)"))
        layout.addWidget(self.lineSpacing)

        self.applyButton = QPushButton("Accept")
        self.applyButton.clicked.connect(self.accept)
        layout.addWidget(self.applyButton)

        self.setLayout(layout)

    def getMargins(self):
        return {
            "left": self.leftMargin.value(),
            "right": self.rightMargin.value(),
            "lineSpacing": self.lineSpacing.value() or self.DEFAULT_LINE_SPACING
        }

    def setMargins(self, margins):
        self.leftMargin.setValue(margins.get("left", 0))
        self.rightMargin.setValue(margins.get("right", 0))
        self.lineSpacing.setValue(margins.get("lineSpacing", self.DEFAULT_LINE_SPACING) if margins.get("lineSpacing", self.DEFAULT_LINE_SPACING) != self.DEFAULT_LINE_SPACING else 0)


class StyleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 150)
        self.setWindowTitle("Choose Style")

        self.layout = QVBoxLayout(self)

        self.comboBox = QComboBox(self)
        self.layout.addWidget(QLabel("Choose Style"))
        self.layout.addWidget(self.comboBox)

        self.newStyleButton = QPushButton("Create new style", self)
        self.newStyleButton.clicked.connect(self.createNewStyle)
        self.layout.addWidget(self.newStyleButton)

        self.deleteStyleButton = QPushButton("Delete style", self)
        self.deleteStyleButton.clicked.connect(self.deleteStyle)
        self.layout.addWidget(self.deleteStyleButton)

        self.applyButton = QPushButton("Accept", self)
        self.applyButton.clicked.connect(self.applyStyle)
        self.layout.addWidget(self.applyButton)

        self.styles = self.parent().loadStyles()  # Load styles from file
        self.updateComboBox()

    def updateComboBox(self):
        self.comboBox.clear()
        for style_name, style in self.styles.items():
            tooltip_text = (
                f"Шрифт: {style['font_family']}\n"
                f"Размер шрифта: {style['font_size']}\n"
                f"Цвет: {style['color']}\n"
                f"Выравнивание: {style['alignment']}\n"
                f"Отступ слева: {style['margins'].get('left', 0)}\n"
                f"Отступ справа: {style['margins'].get('right', 0)}\n"
                f"Межстрочный интервал: {style['lineSpacing']}"
            )
            self.comboBox.addItem(style_name)
            self.comboBox.setItemData(self.comboBox.count() - 1, tooltip_text, Qt.ToolTipRole)

    def createNewStyle(self):
        font, ok = QFontDialog.getFont()
        if ok:
            color = QColorDialog.getColor()
            if color.isValid():
                marginsDialog = MarginsDialog(self)
                marginsDialog.exec_()
                margins = marginsDialog.getMargins()

                styleName, ok = QInputDialog.getText(self, "Style name", "Enetr style name:")
                if ok and styleName:
                    alignment, ok = QInputDialog.getItem(self, "Alignment", "Choose alignment:",
                                                         ["Left", "Center", "Right", "Justify"], 0, False)
                    if ok:
                        lineSpacing = margins.pop("lineSpacing", MarginsDialog.DEFAULT_LINE_SPACING)
                        charFormat = QTextCharFormat()
                        charFormat.setFont(font)
                        charFormat.setForeground(color)

                        self.styles[styleName] = {
                            "font_family": font.family(),
                            "font_size": font.pointSize(),
                            "color": color.name(),
                            "alignment": alignment,
                            "margins": margins,
                            "lineSpacing": lineSpacing
                        }
                        self.updateComboBox()
                        self.parent().saveStyles(self.styles)
                        self.parent().applyTextStyle(charFormat, alignment, margins, lineSpacing)

    def applyStyle(self):
        try:
            styleName = self.comboBox.currentText()
            if styleName in self.styles:
                charFormat = QTextCharFormat()
                style = self.styles[styleName]
                charFormat.setFont(QFont(style["font_family"], style["font_size"]))
                charFormat.setForeground(QColor(style["color"]))

                alignment = style.get("alignment", "Left")
                margins = style.get("margins", {"left": 0, "right": 0})
                lineSpacing = style.get("lineSpacing", MarginsDialog.DEFAULT_LINE_SPACING)
                self.parent().applyTextStyle(charFormat, alignment, margins, lineSpacing)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error occured when applying the style: {str(e)}")

    def deleteStyle(self):
        styleName = self.comboBox.currentText()
        if styleName in self.styles:
            reply = QMessageBox.question(self, "Delete the style", f"Are you sure, you want to delete the style '{styleName}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.styles[styleName]
                self.updateComboBox()
                self.parent().saveStyles(self.styles)


class FindDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setWindowTitle("Find and Replace")

        layout = QGridLayout()
        self.finding_text = QLineEdit()
        layout.addWidget(QLabel("Find:"), 0, 0)
        layout.addWidget(self.finding_text, 0, 1)

        self.findButton = QPushButton("Find")
        layout.addWidget(self.findButton)

        self.comboBox = QComboBox()
        self.comboBox.addItems(["Select full word", "Select piece"])
        layout.addWidget(self.comboBox)

        self.setLayout(layout)

        self.changed = False
        self.isFullWord = True

        self.setWhatsThis("Whats this")
        self.setWindowFlags(Qt.WindowContextHelpButtonHint | Qt.WindowCloseButtonHint)

        self.findButton.clicked.connect(self.find)

    def appendExtraSelection(self, tc):
            
            ex = QTextEdit.ExtraSelection()            
            ex.cursor = tc
            ex.format.setBackground(QBrush(Qt.yellow))
            self.parent.extraSelections.append(ex)

    def find(self):
        self.comboBox.currentTextChanged.connect(self.onComboboxChanged)
        self.parent.extraSelections.clear()
        self.isFullWord = True if self.comboBox.currentText() == "Select full word" else False

        if self.changed: 
            self.parent.extraSelections.clear()

        pattern = self.finding_text.text()

        cursor = self.parent.textEdit.textCursor()
        spec_cursor = self.parent.textEdit.textCursor()
        
        cursor.setPosition(0)
        spec_cursor.setPosition(0)

        doc = self.parent.textEdit.document()
        reg = str(pattern)

        if "?" in pattern:
            reg = pattern.replace("?", "[^ ]?")
        elif "*" in pattern:
            reg = pattern.replace("*", "[^ ]+")

        regex = QRegExp("\\b" + str(reg) + "\\b") if self.isFullWord else QRegExp(str(reg))

        pos = 0
        index = regex.indexIn(self.parent.textEdit.toPlainText(), pos)
        while (index != -1):

            cursor.setPosition(index)

            if self.isFullWord:
                cursor.movePosition(QTextCursor.EndOfWord, 1)
                if not cursor.isNull(): 
                    self.appendExtraSelection(cursor)

            if not self.isFullWord:
                cursor = doc.find(pattern, index)
                if not cursor.isNull(): 
                    self.appendExtraSelection(cursor)

            pos = index + regex.matchedLength()
            index = regex.indexIn(self.parent.textEdit.toPlainText(), pos)

        self.parent.textEdit.setExtraSelections(self.parent.extraSelections)

    def closeEvent(self, event):
        self.parent.d = "Find"
        self.close()

    def onComboboxChanged(self, value):
        self.changed = True

        
class ReplaceDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setWindowTitle("Replace")

        self.gen_layout = QGridLayout()

        self.replacing_text = QLineEdit()
        self.gen_layout.addWidget(QLabel("Replace:"), 0, 0)
        self.gen_layout.addWidget(self.replacing_text, 0, 1)

        self.to_text = QLineEdit()
        self.gen_layout.addWidget(QLabel("To:"), 1, 0)
        self.gen_layout.addWidget(self.to_text, 1, 1)

        self.replaceButton = QPushButton("Replace")
        self.gen_layout.addWidget(self.replaceButton)

        self.setLayout(self.gen_layout)

        self.replaceButton.clicked.connect(self.replace)


    def replace(self):
        self.replaceRec(0)


    def replaceRec(self, pos):

        doc = self.parent.textEdit.document()
        tc = QTextCursor(doc)

        pattern_for_replace = self.replacing_text.text()
        pattern_new = self.to_text.text()

        tc = doc.find(pattern_for_replace, pos)
        if not tc.isNull():
            tc.removeSelectedText()
            tc.insertText(pattern_new)
            self.replaceRec(tc.selectionEnd())


class HrefDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.setWindowTitle("Insert hyperlink")

        layout = QGridLayout()
        self.adress = QLineEdit()
        layout.addWidget(QLabel("Adress:"), 0, 0)
        layout.addWidget(self.adress, 0, 1)

        self.word = QLineEdit()
        layout.addWidget(QLabel("Text:"), 1, 0)
        layout.addWidget(self.word, 1, 1)

        self.insertButton = QPushButton("Insert")
        layout.addWidget(self.insertButton)

        self.setLayout(layout)

        self.insertButton.clicked.connect(self.insertHyperlink)

    def insertHyperlink(self):
        cursor = self.parent.textEdit.textCursor()

        format = cursor.charFormat()
        format_original = cursor.charFormat()
        format.setForeground(QColor("blue"))
        format.setFontUnderline(True)

        if not self.adress.text():
            QMessageBox.critical(self, "Error", "Adress line is empty")

        if not self.word.text():
            self.word.setText(self.adress.text())

        format.setAnchor(True)
        format.setAnchorHref(self.adress.text())
        format.setToolTip(self.adress.text())

        cursor.insertText(self.word.text(), format)
        cursor.insertText(" ", format_original)

        self.close()


class QDocumentEditor(QTextEdit):
    PAGE_WIDTH = 780
    PAGE_HEIGHT = 1000
    PAGE_SIZE = QSizeF(PAGE_WIDTH, PAGE_HEIGHT)
    MARGIN = 50
    SPACING = 30

    def __init__(self, parent: QWidget, scroll_area: QScrollArea):
        super().__init__(parent)

        self.setStyleSheet('background-color: transparent; border: none; font: 14pt "Calibri";')

        self.scroll_area = scroll_area
        self.setFixedSize(QDocumentEditor.PAGE_WIDTH, QDocumentEditor.PAGE_HEIGHT)

        self.document().setPageSize(QDocumentEditor.PAGE_SIZE)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        '''
        frame_format = QTextFrameFormat()
        frame_format.setMargin(QDocumentEditor.MARGIN)
        frame_format.setBottomMargin(QDocumentEditor.MARGIN + QDocumentEditor.SPACING)  
        '''

        #self.document().rootFrame().setFrameFormat(frame_format)

        self.textChanged.connect(self.updateHeight)
        self.cursorPositionChanged.connect(self.updateCurrentScroll)


    def setDocument(self, document):
        super().setDocument(document)

        self.document().setPageSize(QDocumentEditor.PAGE_SIZE)

        
        frame_format = QTextFrameFormat()
        frame_format.setMargin(QDocumentEditor.MARGIN)
        frame_format.setBottomMargin(QDocumentEditor.MARGIN + QDocumentEditor.SPACING)

        '''
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor(QColor("red"))
        frame_format.setBorder(1)
        frame_format.setBorderBrush(brush)
        '''
        self.document().rootFrame().setFrameFormat(frame_format)

        self.document().clearUndoRedoStacks()


    def updateCurrentScroll(self):
        pos = self.mapToParent(self.cursorRect().center())
        self.scroll_area.ensureVisible(pos.x(), pos.y())

    def updateHeight(self):
        self.setFixedHeight(self.document().pageCount() * QDocumentEditor.PAGE_HEIGHT)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            self.document().setPageSize(QDocumentEditor.PAGE_SIZE)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self.viewport())
        pen = QPen()
        pen.setColor(QColor("#e6e3ed"))
        pen.setWidth(1)
        painter.setPen(pen)
        brush = QBrush()
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor(QColor("white"))
        painter.setBrush(brush)
        painter.save()

        for i in range(self.document().pageCount()):
            painter.drawRect(1, i * (QDocumentEditor.PAGE_HEIGHT) + 2,
                             QDocumentEditor.PAGE_WIDTH - 2, QDocumentEditor.PAGE_HEIGHT - QDocumentEditor.SPACING - 3)

        painter.restore()

        super().paintEvent(event)


class QDocument(QTextDocument):

    def __init__(self, title: str = "Untitled") -> None:
        super().__init__()

        self.title = title
        self.images = []

    def getTitle(self) -> str:
        return self.title

    def getImages(self) -> typing.Iterable[str]:
        return self.images

    def addResource(self, type: int, url: QUrl, resource: typing.Any) -> None:
        super().addResource(type, url, resource)
        if type == QTextDocument.ResourceType.ImageResource:
            self.images.append(url.toString())


class QDocumentArchiver:
    CONTENT_FILE_NAME = "content.html"
    COMPRESSION_TYPE = ZIP_DEFLATED
    COMPRESSION_LEVEL = 6

    @staticmethod
    def getFileName(filePath: str) -> str:
        i, j = filePath.rfind("/") + 1, filePath.rfind(".")
        return filePath[i:j]

    @staticmethod
    def getFileFormat(fileName: str) -> str:
        i = fileName.rfind(".") + 1
        return fileName[i:]

    @staticmethod
    def pixmap2ByteArray(pixmap: QPixmap, format: str) -> QByteArray:
        byteArray = QByteArray()
        buffer = QBuffer(byteArray)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, format)
        buffer.close()

        return byteArray

    @staticmethod
    def byteArray2Pixmap(byteArray: QByteArray, format: str) -> QPixmap:
        pixmap = QPixmap()
        pixmap.loadFromData(byteArray, format)

        return pixmap

    @staticmethod
    def saveDocument(filePath: str, document: QDocument) -> None:
        content = document.toHtml()

        try:
            with ZipFile(filePath, mode="w", compression=QDocumentArchiver.COMPRESSION_TYPE,
                         compresslevel=QDocumentArchiver.COMPRESSION_LEVEL) as archive:
                for imageFile in document.getImages():
                    hash = hashlib.sha256(imageFile.encode()).hexdigest()
                    format = QDocumentArchiver.getFileFormat(imageFile)

                    pixmap = document.resource(QDocument.ResourceType.ImageResource, QUrl(imageFile))
                    print(pixmap, imageFile, QUrl(imageFile).toString())
                    byteArray = QDocumentArchiver.pixmap2ByteArray(pixmap, format)
                    archiveFile = hash + "." + format

                    archive.writestr(archiveFile, byteArray)
                    content = content.replace(imageFile, archiveFile)

                archive.writestr(QDocumentArchiver.CONTENT_FILE_NAME, content)
        except Exception as E:
            print(E)

    @staticmethod
    def readDocument(filePath: str) -> QDocument:
        document = QDocument(QDocumentArchiver.getFileName(filePath))
        try:

            with ZipFile(filePath, mode="r") as archive:
                for archiveFile in archive.namelist():
                    if archiveFile == QDocumentArchiver.CONTENT_FILE_NAME:
                        continue

                    format = QDocumentArchiver.getFileFormat(archiveFile)
                    byteArray = QByteArray(archive.read(archiveFile))
                    pixmap = QDocumentArchiver.byteArray2Pixmap(byteArray, format)

                    document.addResource(QDocument.ResourceType.ImageResource,
                                         QUrl(archiveFile), pixmap)

                content = str(archive.read(QDocumentArchiver.CONTENT_FILE_NAME), encoding="utf-8")
                document.setHtml(content)
        except Exception as E:
            print(E)

        return document


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('proj/main_practice_summer.ui', self)

        contentLayout = QHBoxLayout()
        contentLayout.setContentsMargins(0, 60, 0, 10)
        self.scrollAreaWidgetContents.setLayout(contentLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.scrollArea.setWidgetResizable(True)

        self.textEdit = QDocumentEditor(self.scrollAreaWidgetContents, self.scrollArea)
        self.scrollAreaWidgetContents.layout().addWidget(self.textEdit)

        initial_font = QFont("Calibri", 15)
        self.textEdit.setFont(initial_font)
        self.textEdit.setTabStopDistance(20)
        self.actionDefault.setToolTip("This button allows you to reset all text formatting styles to the initial one")

        self.actionCreate_Style.triggered.connect(self.openStyleDialog)
        self.actionCreate_Style_1.triggered.connect(self.openStyleDialog)
        self.actionImage.triggered.connect(self.insertImageAction)
        self.actionInsert_Image.triggered.connect(self.insertImageAction)
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
        self.actionMargins.triggered.connect(self.openMarginsDialog)
        self.actionMargins_2.triggered.connect(self.openMarginsDialog)
        self.actionFind_2.triggered.connect(self.findWindow)
        self.actionReplace_2.triggered.connect(self.replaceWindow)
        self.actionInsert_Hyperlink.triggered.connect(self.insert)
        self.actionInsert_Hyperlink_2.triggered.connect(self.insert)
        self.actionFind_3.triggered.connect(self.findWindow)
        self.actionReplace_3.triggered.connect(self.replaceWindow)

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

        self.textEdit.textChanged.connect(self.changeText)

        self.styles = self.loadStyles()

        self.extraSelections = []

        self.currentMargins = {"left": 0, "right": 0}
        self.actionDefault.triggered.connect(self.applyDefaultStyle)

        self.textEdit.setDocument(QDocument())


    def applyDefaultStyle(self):
        styleName = "Default"
        if styleName in self.styles:
            charFormat = QTextCharFormat()
            style = self.styles[styleName]
            charFormat.setFont(QFont(style["font_family"], style["font_size"]))
            charFormat.setForeground(QColor(style["color"]))

            alignment = style.get("alignment", "Left")
            margins = style.get("margins", {"left": 0, "right": 0})
            lineSpacing = style.get("lineSpacing", MarginsDialog.DEFAULT_LINE_SPACING)

            self.applyTextStyle(charFormat, alignment, margins, lineSpacing)

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
                self.actionRight_2.setChecked(False)
                self.actionLeft_2.setChecked(False)
                self.actionCenter_2.setChecked(False)
        except Exception as E:
            pass

    def setInitialFont(self):
        initial_font = QFont("Calibri", 14)
        self.textEdit.setFont(initial_font)

    def insertImageAction(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select image', '',
                                                   'Images (*.png *.jpg *.bmp *.gif)')

        if file_name:
            url = QUrl(file_name)
            self.textEdit.document().addResource(QDocument.ResourceType.ImageResource, url, QPixmap(url.toString()))
            cursor = self.textEdit.textCursor()
            cursor.insertHtml('<img src="{}">'.format(url.toString()))

    def fileNew(self):
        result = QMessageBox.question(
            self,
            "Opening a new file",
            "Do you want to save the changes to a file?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if result == QMessageBox.Save:
            self.saveFile()

        elif result == QMessageBox.Discard:
            frame_format = self.textEdit.document().rootFrame().frameFormat()

            self.textEdit.clear()

            self.textEdit.document().rootFrame().setFrameFormat(frame_format)

        elif result == QMessageBox.Cancel:
            return

    def openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Open File', '',
                                                  'Tusha Files (*.summer)')
        if filePath:
            self.textEdit.setDocument(QDocumentArchiver.readDocument(filePath))

    def saveFile(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "(*.summer)")

        if file_path:
            QDocumentArchiver.saveDocument(file_path, self.textEdit.document())

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
        document = self.textEdit.document()
        printer.setDocName("Document")
        printer.setPageSize(QPrinter.A4)
        printer.setResolution(QPrinter.HighResolution)
        document.print_(printer)

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

    def openStyleDialog(self):
        dialog = StyleDialog(self)
        dialog.exec_()

    def applyTextStyle(self, charFormat, alignment, margins=None, lineSpacing=None):
        cursor = self.textEdit.textCursor()
        blockFormat = cursor.blockFormat()
        blockFormat.setAlignment(self.getAlignmentFromString(alignment))

        if margins:
            blockFormat.setLeftMargin(margins.get("left", 0))
            blockFormat.setRightMargin(margins.get("right", 0))

        if lineSpacing is not None:
            blockFormat.setLineHeight(lineSpacing, QTextBlockFormat.FixedHeight)

        if cursor.hasSelection():
            cursor.mergeCharFormat(charFormat)
            cursor.mergeBlockFormat(blockFormat)
        else:
            cursor.setBlockFormat(blockFormat)
            cursor.setCharFormat(charFormat)
            self.textEdit.setTextCursor(cursor)

        self.textEdit.setFocus()

    def getAlignmentFromString(self, alignment_string):
        if alignment_string == "Left":
            return Qt.AlignLeft
        elif alignment_string == "Center":
            return Qt.AlignCenter
        elif alignment_string == "Right":
            return Qt.AlignRight
        elif alignment_string == "Justify":
            return Qt.AlignJustify
        return Qt.AlignLeft

    def loadStyles(self):
        try:
            with open('styles.json', 'r') as file:
                data = file.read()
                if not data:
                    return {}
                return json.loads(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def saveStyles(self, styles):
        try:
            with open('styles.json', 'w') as file:
                json.dump(styles, file, indent=4)
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Failed to save styles: {str(e)}")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            cursor = self.textEdit.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.deleteChar()

            default_format = QTextCharFormat()
            default_format.setFont(QFont("Calibri", 11))
            self.textEdit.setCurrentCharFormat(default_format)

            super().keyPressEvent(event)

            cursor.insertBlock()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):

        x, y = event.pos().x(), event.pos().y()

        if self.size().width() == 1920:
            self.anchor = self.textEdit.anchorAt(QPoint(x - 560, y - 120 + self.scrollArea.verticalScrollBar().value()))
        elif self.size().width() == 970:
            self.anchor = self.textEdit.anchorAt(QPoint(x - 81, y - 120 + self.scrollArea.verticalScrollBar().value()))
        elif self.size().width() == 1366:
            self.anchor = self.textEdit.anchorAt(QPoint(x - 280, y - 120 + self.scrollArea.verticalScrollBar().value()))
        elif self.size().width() == 1440:
            self.anchor = self.textEdit.anchorAt(QPoint(x - 320, y - 120 + self.scrollArea.verticalScrollBar().value()))
        elif self.size().width() == 1280:
            self.anchor = self.textEdit.anchorAt(QPoint(x - 240, y - 120 + self.scrollArea.verticalScrollBar().value()))

        if self.anchor:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)

            QDesktopServices.openUrl(QUrl(self.anchor))
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.anchor = None
        

        super(MyWidget, self).mousePressEvent(event)

    def openMarginsDialog(self):
        dialog = MarginsDialog(self)
        dialog.setMargins(self.currentMargins)
        if dialog.exec_():
            margins = dialog.getMargins()
            self.applyMargins(margins)
            self.currentMargins = margins

    def applyMargins(self, margins):
        cursor = self.textEdit.textCursor()
        blockFormat = cursor.blockFormat()

        blockFormat.setLeftMargin(margins["left"])
        blockFormat.setRightMargin(margins["right"])

        lineSpacing = max(margins.get("lineSpacing", 0), 1)
        blockFormat.setLineHeight(lineSpacing, QTextBlockFormat.FixedHeight)

        if cursor.hasSelection():
            cursor.mergeBlockFormat(blockFormat)
        else:
            cursor.setBlockFormat(blockFormat)
            self.textEdit.setTextCursor(cursor)

    def findWindow(self):
        self.dialog = FindDialog(self)
        self.dialog.exec_()

    def replaceWindow(self):
        self.dialog = ReplaceDialog(self)
        self.dialog.exec_()

    def insert(self):
        self.dialog = HrefDialog(self)
        self.dialog.exec_()

    def changeText(self):
        self.extraSelections.clear()
        self.textEdit.setExtraSelections(self.extraSelections)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec_())