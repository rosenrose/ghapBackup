import os
import re
import urllib.request
import requests
import time
from bs4 import BeautifulSoup

url = "http://blog.daum.net/_blog/BlogTypeView.do?blogid=0qN5Q&articleno"
articleUrl = "http://blog.daum.net/_blog/hdn/ArticleContentsView.do?blogid=0qN5Q&articleno"
path = "D:/Touhou/sniperriflesr"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
catIDList = [3,5,6,7,8,32,38,46,50,51,52,104,105,114,115,117,118,119,122,134,141,156,161,185,204,210,211,212,216,384,385,386,387,388,389,390,391,432,433]
codeRegex = re.compile('[0-9]*')

def writeLog(msg):
	with open("%s/%s"%(path, logfile), 'a', encoding="utf-8-sig") as a:
		a.write(msg)

def replaceSpecialCh(title):
	res = title.replace('\\', '＼')
	res = res.replace('/', '／')
	res = res.replace(':','：')
	res = res.replace('*','＊')
	res = res.replace('?','？')
	res = res.replace('\"','＂')
	res = res.replace('<','〈')
	res = res.replace('>','〉')
	res = res.replace('|','｜')
	res = res.replace('.','．')
	return res

def sniperriflesr(codeList):
	for code in codeList:
		print("%d start" %(code))
		response = requests.get("%s=%d" %(url, code))
		soup = BeautifulSoup(response.content, 'html.parser')
		main = soup.find('div', { 'class': 'articlePrint' })
		if main is None:
			writeLog("%d does not exist\n" %(code))
			continue

		catID = main.find('span', { 'class': 'cB_Folder' }).find('a')['href']
		catID = codeRegex.findall(catID.split('&')[1])[-2]
		if not int(catID) in catIDList:
			writeLog("%d out of category\n" %(code))
			continue
		category = main.find('span', { 'class': 'cB_Folder' }).find('a').text

		articleResponse = requests.get("%s=%d" %(articleUrl, code))
		articleSoup = BeautifulSoup(articleResponse.content, 'html.parser')
		if not articleSoup.find('img', {'class':'txc-image'}):
			writeLog("%d has no image\n" %(code))
			continue
		
		title = soup.find('title').text
		for i in title.split('-'):
			if i.find("東方 Project") == -1:
				title = i.strip()
		date = main.find('span',{'class':'cB_Tdate'}).text

		titleWin = replaceSpecialCh(title)
		doc = "%s/%d" %(path, code)
		if not os.path.isdir("%s_%s" %(doc,titleWin)):
			try:
				os.mkdir("%s_%s" %(doc,titleWin))
			except:
				writeLog("Making \'%s_%s\' folder fail\n" %(doc,titleWin))
				continue

		try:
			f = open(doc+".html", "w", encoding="utf-8-sig")
		except:
			writeLog("Making \'%s\' file fail\n" %(title))
			f.close()
			continue

		html_header = "<html>\n<head>\n\t<title>%s</title>\n</head>\n<body>\n\t<h2>%s</h2><br/>\n" %(title, title)
		f.write(html_header)
		f.write("<div class=\"category\">%s</div><br/>\n" %(category))
		f.write("<div class=\"date\">%s</div><br/>\n" %(date))

		article = articleSoup.find('div', { 'id': 'contentDiv' })
		p = article.find_all('p')
		f.write("<div class=\"article\">\n")
		num = 1
		for i in p:
			if i.find('img') is not None and i.find('img').has_attr('data-filename'):
				imgSrc = i.find('img')['src'].replace("image","original")
				fileExt = i.find('img')['data-filename'].split('.')[-1]
				fileName = "%03d.%s" %(num,fileExt)
				try:
					imgBuf = urllib.request.urlopen(imgSrc)
				except:
					writeLog("%d_%s/%s open fail\n" %(code,titleWin,fileName))
					continue

				try:
					imgBuf = imgBuf.read()
				except:
					writeLog("%d_%s/%s reading fail\n" %(code,titleWin,fileName))
					continue

				try:
					imgFile = open("%s_%s/%s" %(doc,titleWin,fileName), "wb")
				except:
					writeLog("Making %d_%s/%s fail\n" %(code,titleWin,fileName))
					continue
				else:
					imgFile.write(imgBuf)
				finally:
					imgFile.close()
				pos1 = str(i).find("<img")
				pos2 = str(i).find("</p>", pos1)
				f.write("\t"+str(i)[:pos1].replace("<p>","<p style=\"TEXT-ALIGN: center\">")+"<img src=\"%d_%s/%s\">" %(code,titleWin,fileName)+str(i)[pos2:]+"\n")
				num+=1
			else:
				f.write("\t"+str(i).replace("<p>","<p style=\"TEXT-ALIGN: center\">")+"\n")
		f.write("</div><br/>\n")
		
		f.write("<div class=\"another\">\n")
		f.write("\t<p>'%s' 카테고리의 다른 글</p>\n\t\t<ul>\n" %(category))
		another = soup.find('div', { 'class': 'cContentCateMore' }).find_all('li')
		for i in another:
			anotherTitle = i.find('a')['title']
			for j in anotherTitle.split('-'):
				if j.find("東方 Project") == -1:
					anotherTitle = j.strip()

			if str(i.find('a')).find("href") != -1:
				anotherCode = i.find('a')['href']
				anotherCode = codeRegex.findall(anotherCode.split('&')[1])[-2]
				f.write("\t\t\t<li><a href=\"%s.html\">%s</a></li>\n" %(anotherCode, anotherTitle))
			else:
				f.write("\t\t\t<li>%s</li>\n" %(anotherTitle))
		f.write("\t\t</ul>\n</div><br/>\n")
		
		comment = str(soup.find('div', { 'class': 'opinionListBox' }))
		pos1 = comment.find("<ul class=\"opinionListMenu")
		pos2 = comment.find("<input name=\"cmtCount")
		pos2 = comment.find("</div>", pos2)
		comment = comment[:pos1]+"<ul>\n"+comment[pos1:pos2]+"\n</ul>\n"+comment[pos2:]
		
		while(comment.find("<li class=\"opinionBtn") != -1):
			pos1 = comment.find("<li class=\"opinionBtn")
			pos1 = comment[:pos1].rfind("<ul class=\"opinionListMenu")
			pos2 = comment.find("id=\"inWrite", pos1)
			pos2 = comment.find("</div>", pos2)
			comment = comment[:pos1]+"<li class=\"cb_comment_area\">\n"+comment[pos1:pos2+6]+"\n</li>"+comment[pos2+6:]

			pos1 = comment.find("<li class=\"opinionBtn")
			pos2 = comment.find("</ul>", pos1)
			comment = comment[:pos1]+comment[pos2:]
		f.write(comment)

		f.write(html_footer)
		f.close()
		print("%d end" %(code))
		time.sleep(5)

sniperriflesr(range(1,5714))
