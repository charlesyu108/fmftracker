#!/usr/bin/env python
import requests
import smtplib
from fmfConfig import * #Getting constants
from glob import glob
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

headers = {'User-agent': 'Mozilla/5.0'}
page = requests.get(URL, headers = headers).content
soup = BeautifulSoup(page)
listings = soup.body.find("div", {"id": "siteTable"})

def getPosts():
	frontpage = []
	for div in listings:

		post = div.find("p", {"class":"title"})

		item = []

		if post is not None:
			title = post.find('a')
			link = title['href']
			if link[0:3] ==  '/r/':
				link = 'https://reddit.com' + link
			item += [title.text, link]

		post = div.find("ul", {"class": "flat-list buttons"})

		if post is not None:
			comments = post.find("li", {"class": "first"}).find('a')
			comments = comments['href']
			if comments[0:3] ==  '/r/':
				comments = 'https://reddit.com' + comments
			item += [comments]

		if len(item) > 0 :
			frontpage += [tuple(item)]

	return frontpage

#Retrieves user settings
def getQueries(file):
	searches = []
	with open(file) as f:
		for line in f:
			if 'EMAIL' in line:
				email = line.split(':')[1].strip()

			elif 'QUERIES' not in line and 'EMAIL' not in line:
				q = line.strip().lower()
				if q != "":
					searches += [q]

	return email, searches

#checks for user queries in posts
def getMatches(posts, searches):
	matches = {}

	for title, url, comments in posts:
		for s in searches:
			if s in title.lower():
				matches[title] = (url, comments)
	return matches

#sends email alert
def sendEmail(email, queries, matches):
	sender = HOST_EMAIL
	receiver = email

	msg = MIMEMultipart('alternative')
	msg['Subject'] = 'FMF Tracker Update'
	msg['From'] = sender
	msg['To'] = receiver
	q = ""
	m = ""
	mtxt = ""
	for item in queries:
		q += item + ", "

	for title, data in matches.iteritems():
		m += """<b> {} <b> (<a href = \"{}\">Link</a>) (<a href = \"{}\" >Discussion</a>)
		<br> <br>""".format(title, data[0], data[1])
		mtxt += title + ", URL: " + data[0] + ", Disccusion: " + data[1] + "/n"

	html = """\
	<html>
		<head></head>
		<body>
			<p> Your queries for <b> {queries} </b> have returned the following
			results: <br> <br>{results}
		</body>
	</html>
	""".format(queries = q.encode('utf-8'), results = m.encode('utf-8'))

	text = "Your queries have returned the following results: /n" + mtxt.encode('utf-8')

	msg.attach(MIMEText(text, 'plain'))
	msg.attach(MIMEText(html, 'html'))

	if m != "":
		#Make sure you've enabled SMTP with your gmail acc
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.ehlo()
		s.starttls()
		s.ehlo()
		s.login(HOST_EMAIL, HOST_EMAIL_PWD)
		s.sendmail(sender, [receiver], msg.as_string())
		s.quit()


if __name__ == '__main__':
	posts = getPosts()

	for file in glob(USERS_SEARCH_DIR + "*.txt"): 
		email, queries = getQueries(file)
		matches = getMatches(posts, queries)
		sendEmail(email, queries, matches)
		print('SUCCESS!')
