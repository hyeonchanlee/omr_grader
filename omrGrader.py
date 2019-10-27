from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QImage, QPalette, QPixmap
from PyQt5.QtWidgets import (QApplication, QFileDialog, QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy, 
		QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea, QWidget, QDesktopWidget)
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
import numpy as np
import csv

from gradeTest import gradeTest


class omrGrader(QMainWindow):
	# Initialize the pyqt window parameters
	def __init__(self):
		super().__init__()
		screen = QDesktopWidget().screenGeometry()
		self.title = "OMR Grader"
		self.left = 0.1 * screen.width()
		self.top = 0.1 * screen.height()
		self.width = 0.8 * screen.width()
		self.height = 0.8 * screen.height()
		self.initUI()

	# Initialize the pyqt window
	def initUI(self):
		# Set window title and window size
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		# Initialize image label for displaying test
		self.testImage = QLabel()
		self.testImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.testImage.setAlignment(Qt.AlignRight | Qt.AlignTop)

		# Initialize scroll area for displaying answers
		self.scrollArea = QScrollArea()
		self.scrollArea.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		# Initialize button layout and connect functions for buttons
		self.buttons = QVBoxLayout()
		
		self.openButton = QPushButton("Open")
		self.openButton.clicked.connect(self.open)

		self.gradeButton = QPushButton("Grade")
		self.gradeButton.clicked.connect(self.grade)

		self.exportButton = QPushButton("Export Answers")
		self.exportButton.clicked.connect(self.export)

		self.clearButton = QPushButton("Clear")
		self.clearButton.clicked.connect(self.clear)

		self.buttons.addWidget(self.openButton)
		self.buttons.addWidget(self.gradeButton)
		self.buttons.addWidget(self.exportButton)
		self.buttons.addWidget(self.clearButton)
		self.buttons.addStretch(1)

		# Create grid layout and add the initialized widgets and layouts
		self.grid = QGridLayout()
		self.grid.setSpacing(10)

		self.grid.addWidget(self.testImage, 0, 0, -1, 3)
		self.grid.addWidget(self.scrollArea, 0, 3, -1, 1)
		self.grid.addLayout(self.buttons, 0, 4, 2, 1)

		self.window = QWidget()
		self.window.setLayout(self.grid)
		self.setCentralWidget(self.window)

	# Open and display scanned image of bubble sheet
	def open(self):
		self.fileName, _ = QFileDialog.getOpenFileName(self, "Open File", QDir.currentPath())

		if self.fileName:
			imageFile = QImage(self.fileName)

			if imageFile.isNull():
				QMessageBox.information(self, "OMR Grader", "Cannot load %s." % self.fileName)
				return

			self.testImage.setPixmap(QPixmap.fromImage(imageFile).scaled(self.width, self.height, aspectRatioMode=Qt.KeepAspectRatio))

	# Grade the scanned bubble sheet and display answers
	def grade(self):

		if self.testImage.pixmap() == None:
			QMessageBox.information(self, "OMR Grader", "There is no scanned test to grade.")
			return

		self.scrollArea.takeWidget()

		img, ans = gradeTest(self.fileName)

		height, width, channel = img.shape
		bytesPerLine = 3 * width
		qimg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)

		self.testImage.setPixmap(QPixmap.fromImage(qimg).scaled(self.width, self.height, aspectRatioMode=Qt.KeepAspectRatio))

		answers = QVBoxLayout()

		for i in range(0, len(ans)):
			answer = QHBoxLayout()
			answer.addStretch(1)
			answer.addWidget(QLabel(str(i + 1)))
			answer.addWidget(QLineEdit(str(ans[i])))
			answers.addLayout(answer)

		widget = QWidget()
		widget.setLayout(answers)
		self.scrollArea.setWidget(widget)

	# Export the student answers as csv file
	def export(self):
		img, ans = gradeTest(self.fileName)

		savePath, _ = QFileDialog.getSaveFileName(self, "Save As", "", "CSV Files(*.csv)")

		if savePath != '':
			# Write the student answers to the new csv file
			with open(savePath, mode='w', newline='') as student_answers:
				answers_writer = csv.writer(student_answers, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

				answers_writer.writerow(np.arange(1, 101, 1))
				answers_writer.writerow(ans)

	# Clear student OMR sheet
	def clear(self):
		self.testImage.clear()
		self.scrollArea.takeWidget()


if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)
	omrGrader = omrGrader()
	omrGrader.show()
	sys.exit(app.exec_())