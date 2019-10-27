from collections import defaultdict
from imutils import contours
import numpy as np
import imutils
import cv2
import csv


def gradeTest(testImage):

	# Define the structure of the OMR sheet
	num_rows = 25
	num_columns = 4
	num_questions = 100
	num_choices = 5

	# Define the answer key
	ANSWER_KEY = {}
	ANSWER_KEY = defaultdict(lambda: 0, ANSWER_KEY)

	# Load the image and convert it into grayscale
	image = cv2.imread(testImage)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Binarize the image using Otsu's thresholding method
	thresh = cv2.threshold(gray.copy(), 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

	# Find the contours and initialize the list of contours
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	questionCnts = []

	# Loop over the contours
	for cnt in cnts:
		# Compute the bounding box of the contour, then use the bounding box to derive aspect ratio
		(x, y, w, h) = cv2.boundingRect(cnt)
		ar = w / float(h)

		# Bounding box must be sufficiently wide, sufficiently tall, and have aspect ratio approximately equal to 1
		if w >= 10 and h >= 10 and ar >= 0.9 and ar <= 1.1:
			questionCnts.append(cnt)

	# Sort the question contours top-to-bottom and initialize the list for contour-sorting
	questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]
	sortedCnts = np.empty(len(questionCnts), dtype=object)

	# Each row of questions has 20 bubbles, so loop over the question contours in groups of 20
	for (r, q) in enumerate(np.arange(0, len(questionCnts), num_columns * num_choices)):
		# Sort the contours for current row of questions from left to right
		rowCnts = contours.sort_contours(questionCnts[q:q + num_columns * num_choices])[0]

		# Sort the contours into appropriate columns
		for (i, c) in enumerate(rowCnts):
			sortedCnts[num_choices*r + int(i/num_choices)*num_choices*num_rows + i - int(i/num_choices)*num_choices] = c

	correct = 0
	student_ans = []

	# Each question has 5 possible answers, loop over the sorted contours in groups of 5
	for (q, b) in enumerate(np.arange(0, len(sortedCnts), 5)):
		# Get bubbles for current question, and initialize the index of bubbled answer
		cnts = sortedCnts[b:b + 5]
		bubbled = None

		# Loop over the sorted contours
		for (j, c) in enumerate(cnts):
			# Construct a mask that reveals only the current bubble for the question
			mask = np.zeros(thresh.shape, dtype="uint8")
			cv2.drawContours(mask, [c], -1, 255, -1)

			# Apply the mask to the thresholded image, then count the non-zero pixels
			mask = cv2.bitwise_and(thresh, thresh, mask=mask)
			total = cv2.countNonZero(mask)

			# If the current total has a larger number of total non-zero pixels,
			# current bubble is the bubbled in answer
			if bubbled is None or total > bubbled[0]:
				bubbled = (total, j)

		# Initialize the contour color and the index of the correct answer
		color = (0, 0, 255)
		k = ANSWER_KEY[q]
		student_ans.append(bubbled[1])

		# Check to see if the bubbled answer is correct
		if k == bubbled[1]:
			color = (0, 255, 0)
			correct += 1	

		# Draw the outline of the correct answer on the test
		cv2.drawContours(image, [cnts[k]], -1, color, 3)

	# # write the student answers to a new csv file
	# with open('student_answers.csv', mode='w', newline='') as student_answers:
	# 	answers_writer = csv.writer(student_answers, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	# 	answers_writer.writerow(np.arange(1, 101, 1))
	# 	answers_writer.writerow(student_ans)

	# cv2.imshow("image", image)
	# cv2.waitKey(0)

	return image, student_ans