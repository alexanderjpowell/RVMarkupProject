import MySQLdb
import os
from HTMLParser import HTMLParser

class HTMLScorer(object):

	def __init__(self, directory_name):
		self.directory_name = directory_name
		self.all_files = [self.directory_name + file for file in os.listdir(source_directory) if file.endswith('.html')]
		
		self.tag_scores = {'div' : 3, 
						   'p' : 1, 
						   'h1' : 3, 
						   'h2' : 2, 
						   'html' : 5, 
						   'body' : 5, 
						   'header' : 10, 
						   'footer' : 10, 
						   'font' : -1, 
						   'center' : -2, 
						   'big' : -2, 
						   'strike' : -1, 
						   'tt' : -2, 
						   'frameset' : -5, 
						   'frame' : -5}

		self.db = MySQLdb.connect(host='localhost', user='root', passwd='password', db='RedVentures')
		self.cursor = self.db.cursor()

		self._processHtml()

	def _processHtml(self):
		''' Iterates through all html files in the data/ directory and stores score in database table. '''

		for file in self.all_files:
			html = open(file, 'r').read().replace('\n', '')
			parser = BuiltinHTMLParser()
			parser.feed(html)
			score = self._calculateScore(parser.tag_counter)

			components = self._parseFileName(file.replace(self.directory_name, ""))
			keyname = components[0]
			year = components[1]
			month = components[2]
			day = components[3]
			date = year + '-' + month + '-' + day

			queryString = "INSERT INTO HtmlScores (ID, Score, Keyname, Filename, Last_modified) VALUES (NULL, @Score, '@Keyname', '@Filename', '@Date');"
			queryString = queryString.replace("@Score", str(score))
			queryString = queryString.replace("@Keyname", keyname)
			queryString = queryString.replace("@Filename", file.replace(self.directory_name, ""))
			queryString = queryString.replace("@Date", date)

			try:
				self.cursor.execute(queryString)
				self.db.commit()
			except:
				self.db.rollback()
				print("Error executing insert query")


	def _calculateScore(self, tags):
		''' Takes in the dictionary of tags and counts for a particular html file and returns score. '''
		score = 0
		for tag in tags:
			if self.tag_scores.has_key(tag):
				score += self.tag_scores[tag] * tags[tag]
		return score

	def _parseFileName(self, fileName):
		''' Helper method to parse fileName into different components '''
		fileName = fileName.replace(".html", "") # Trim off file extension
		components = fileName.split("_") # Split filename into list based on underscore
		return components

	def getScoresByUser(self, name):
		''' returns all scores for the specified username.  If the given name doesn't exist in the table
		then an empty list is returned.  '''
		queryString = "SELECT Score FROM HtmlScores WHERE Keyname = '@Keyname';"
		queryString = queryString.replace("@Keyname", name)
		try:
			self.cursor.execute(queryString)
			result = self.cursor.fetchall()
			return [int(i[0]) for i in result]
		except:
			print("Error executing select query")

	def getScoresByDate(self, start, end):
		''' returns all scores observed between the specified start and end dates.  If no records are returned
		from the query, an empty list is returned. '''
		queryString = "SELECT Score from HtmlScores where Last_modified > '@start' and Last_modified < '@end';"
		queryString = queryString.replace("@start", start)
		queryString = queryString.replace("@end", end)
		try:
			self.cursor.execute(queryString)
			result = self.cursor.fetchall()
			return [int(i[0]) for i in result]
		except:
			print("Error executing select query")

	def getHighestScore(self):
		''' returns the highest score in the db table. '''
		queryString = "SELECT Score, Keyname FROM HtmlScores WHERE Score = (SELECT MAX(score) FROM HtmlScores);"
		try:
			self.cursor.execute(queryString)
			result = self.cursor.fetchone()
			return result
		except Exception as e:
			print("Error executing select query")

	def getLowestScore(self):
		''' returns the lowest score in the db table '''
		queryString = "SELECT Score, Keyname FROM HtmlScores WHERE Score = (SELECT MIN(score) FROM HtmlScores);"
		try:
			self.cursor.execute(queryString)
			result = self.cursor.fetchone()
			return result
		except Exception as e:
			print("Error executing select query")

	def getAverageScore(self):
		''' returns the average score from the db table '''
		queryString = "SELECT AVG(Score) FROM HtmlScores;"
		try:
			self.cursor.execute(queryString)
			result = self.cursor.fetchone()
			return result[0]
		except:
			print("Error executing select query")

# Inherits from the HTMLParser python class.  Overrides the handle_starttag method 
# to count the number of occurences of each tag.  
class BuiltinHTMLParser(HTMLParser):

	def __init__(self):
		HTMLParser.__init__(self)
		self.tag_counter = {}

	def handle_starttag(self, tag, attrs):
		''' For every tag encountered in the html doc, either add it to the dictionary or increment value if it already exists.'''
		if self.tag_counter.has_key(tag):
			self.tag_counter[tag] = self.tag_counter[tag] + 1
		else:
			self.tag_counter[tag] = 1

if __name__ == "__main__":

	source_directory = "../data/"
	parser = HTMLScorer(source_directory)

	# Method: Retrieve highest scored unique id
	(score, name) = parser.getHighestScore()
	print("The highest recorded score was " + str(score) + " by " + str(name) + ". ")
	print("-------------------------------------------------")

	# Method: Retrieve lowest scored unique id
	(score, name) = parser.getLowestScore()
	print("The lowest recorded score was " + str(score) + " by " + str(name) + ". ")
	print("-------------------------------------------------")

	# Method: Retrieve scores for a unique id
	keyname = "bob"
	scores = parser.getScoresByUser(keyname)
	print(keyname + " had the following HTML scores: ")
	for i in scores:
		print(i)
	print("-------------------------------------------------")

	# Method: Retrieve all scores run in the system for a custom date range
	begin = "2013-01-15"
	end = "2013-03-01"
	scores = parser.getScoresByDate(begin, end)
	print("The following scores were observed between the dates " + begin + " and " + end + ": ")
	for i in scores:
		print(i)
	print("-------------------------------------------------")

	# Additionally you should write one query that will find the average score for all runs
	score = parser.getAverageScore()
	print("The average score for all runs is: " + str(score) + ". ")




