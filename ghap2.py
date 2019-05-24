import os
import re
import urllib.request
import time
import sys
from bs4 import BeautifulSoup
from replaceSpecialCh import replaceSpecialCh

path = "D:/Touhou/doujin/ghap2"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
catRegex = re.compile('(동방)')
codeRegex = re.compile('[0-9]*')

def writeLog(msg):
	with open("%s/%s"%(path,logfile),"a",encoding="utf-8") as a:
		a.write(msg)

def ghap(dirList):
	for dirs in dirList:
		print("%s start" %(dirs))
		with open(gitPath+"/"+dirs,"r",encoding="utf-8") as f:
			content = f.read()

		soup = BeautifulSoup(content,"html.parser")
		category = soup.find("h1",class_="header").find_all("a",class_="page-title-link")
		tmp = ""
		for i in range(len(category)):
			tmp = tmp + category[i].text
			if i < len(category)-1:
				tmp = tmp + "/"
		category = tmp
		title = soup.find("h1",class_="article-title").text.strip()
		date = soup.find("time").text

		titleWin = replaceSpecialCh(title)
		code = date+"_"+titleWin
		code = replaceSpecialCh(code).replace("+","＋")
		doc = "%s/%s" %(path,code)
		if not os.path.isdir("%s_%s" %(doc,titleWin)):
			try:
				os.mkdir("%s_%s" %(doc,titleWin))
			except:
				writeLog("Making \'%s_%s\' folder fail\n" %(doc,titleWin))
				continue

		try:
			f = open(doc+".html","w",encoding="utf-8")
		except:
			writeLog("Making \'%s\' file fail\n" %(title))
			f.close()
			continue

		html_header = "<html>\n<head>\n\t<title>%s</title>\n</head>\n<body>\n\t<h2>%s</h2><br/>\n" %(title, title)
		f.write(html_header)
		f.write(str(soup.find("link",rel="canonical"))+"\n")
		f.write("<div class=\"category\">%s</div><br/>\n" %(category))
		f.write("<div class=\"date\">%s</div><br/>\n" %(date))
		
		article = soup.find("div",class_="article-entry")
		p = article.find_all("img")
		f.write("<div class=\"article\">\n")
		num = 1
		for i in p:
			imgSrc = i["src"]
			fileExt = "jpg"
			fileName = "%03d.%s" %(num,fileExt)
			"""
			try:
				imgBuf = urllib.request.urlopen(imgSrc)
			except:
				writeLog("%s_%s/%s open fail\n" %(code,titleWin,fileName))
				continue

			try:
				imgBuf = imgBuf.read()
			except:
				writeLog("%s_%s/%s reading fail\n" %(code,titleWin,fileName))
				continue

			try:
				imgFile = open("%s_%s/%s" %(doc,titleWin,fileName), "wb")
			except:
				writeLog("Making %s_%s/%s fail\n" %(code,titleWin,fileName))
				continue
			else:
				imgFile.write(imgBuf)
			finally:
				imgFile.close()
			"""
			i["src"] = "%s_%s/%s" %(code,titleWin,fileName)
			num+=1
		f.write(str(article))
		f.write("</div><br/>\n")
		
		tag = soup.find("div",class_="article-tag")
		f.write("<div class=\"tagTrail\">\n")
		if tag is not None:
			tag = tag.find_all("a")
			f.write("\t<p>태그: </p>\n\t\t<ul>\n")
			for i in tag:
				f.write("\t\t\t<li>%s</li>\n"%(i.text))
			f.write("\t\t</ul>\n</div><br/>\n")

		f.write(html_footer)
		f.close()
		print("%s end" %(dirs))

for i in range(1,len(sys.argv)):
	ghap([sys.argv[i]])