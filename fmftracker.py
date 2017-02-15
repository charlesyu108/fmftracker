#!/usr/bin/env python
import urllib2
import smtplib
from fmfConfig import * #Getting constants
from glob import glob
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

page = urllib2.urlopen(URL)
soup = BeautifulSoup(page.read())
listings = soup.body.find("div", {"id": "siteTable"})

def getPosts():
	frontpage = []
	for div in listings:

		post = div.find("p", {"class":"title"})

		if post is not None:
			title = post.find('a')
			link = title['href']
			if link[0:3] ==  '/r/':
				link = 'https://reddit.com' + link
			frontpage += [(title.text, link)]


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

	for title, url in posts:
		for s in searches:
			if s in title.lower():
				matches[title] = url
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
	for title, url in matches.iteritems():
		m += "<b>" + title + "<b> (<a href = \" " + url + " \" >Link</a>) <br><br>"
		mtxt += title + ", URL: " + url + "/n"

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
