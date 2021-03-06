import os
import re
import urllib.request
import requests
import time
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://lilybin.tistory.com"
path = "D:/Touhou/doujin/lilybin"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
catRegex = re.compile('(동방/동인지|동방/웹코믹|동방/번역)')
codeRegex = re.compile('[0-9]*')
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}


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
	res = res.replace('#','＃')
	return res

def lilybin(cacheList):
	code = 9706
	for cache in cacheList:
		print("%d start" %(code))
		response = requests.get(cache, headers=headers)

		soup = BeautifulSoup(response.content,"html.parser")
		tdiv = soup.find("div",class_="post-content overflow")
		if tdiv is None:
			writeLog("%d does not exist\n" %(code))
			continue
		
		category = tdiv.find("ul",class_="nav navbar-nav post-nav").find_all("li")[0].text
		if not (catRegex.match(category)):
			writeLog("%d out of category (%s)\n" %(code, category))
			continue

		date = tdiv.find("div",class_="post-top overflow").find_all("li")[1].text
		title = tdiv.find("h2").find("a").text
		title = "Loneliness"
		left = title.find('[')
		right = title.find(']')
		if right != -1 and left == 0:
			title = title[right+1:].strip()

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
		
		article = soup.find("div",class_="area_view")
		fold = article.find_all("p",class_=re.compile("moreless_*"))
		if fold is not None:
			for i in fold:
				i.decompose()
		fold = article.find_all("div",class_=re.compile("moreless_*"))
		if fold is not None:
			for i in fold:
				i.unwrap()
		article.find("div",id=re.compile("dablewidget_*")).decompose()
		article.find("div",class_="container_postbtn").decompose()

		another = soup.find("div",class_="another_category another_category_color_violet").extract()
		p = article.find_all("img")
		f.write("<div class=\"article\">\n")
		num = 1
		if p is not None:
			for i in p:
				if i.has_attr("filename"):
					fileExt = i["filename"].split('.')[-1]
				else:
					fileExt = "jpg"
				imgSrc = i["src"]+"?original"				
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
					
				#i.find("span").unwrap()
				for attr in list(i.attrs):
					if attr != "src":
						del i[attr]
				i.attrs["src"] = "%d_%s/%s" %(code,titleWin,fileName)
				num+=1
		else:
			writeLog("%d has no image\n" %(code))
			continue

		f.write(str(article))
		f.write("</div><br/>\n")
		
		tag = soup.find("div",class_="post-bottom overflow").find("div",class_="pull-left")
		f.write("<div class=\"tagTrail\">\n")
		if tag is not None:
			tag = tag.find_all("a")
			f.write("\t<p>태그: </p>\n\t\t<ul>\n")
			for i in tag:
				f.write("\t\t\t<li>%s</li>\n"%(i.text))
			f.write("\t\t</ul>\n</div><br/>\n")

		f.write("<div class=\"another\">\n")
		f.write("\t<p>'%s' 카테고리의 다른 글</p>\n\t\t<ul>\n" %(category))
		another = another.find_all("tr")
		for i in another:
			anotherTitle = i.th.text
			anotherCode = codeRegex.findall(i.th.a["href"])[1]
			f.write("\t\t\t<li><a href=\"%s.html\">%s</a></li>\n" %(anotherCode, anotherTitle))
		f.write("\t\t</ul>\n</div><br/>\n")
		
		comment = soup.find("div",class_="area_reply response-area padding-top")
		firstCmt = comment.ul
		if firstCmt is not None:
			firstCmt = firstCmt.find_all("li",recursive=False)
			for i in firstCmt:
				img = i.find("a",class_="pull-left comment-img")
				if img is not None:
					img.decompose()

				reaction = i.find("a",class_="link_edit")
				if reaction is not None:
					reaction.decompose()
				reaction = i.find("a",class_="link_edit")
				if reaction is not None:
					reaction.decompose()

				report = i.find("ul",class_="nav navbar-nav post-nav")
				if report is not None:
					report.li.decompose()
				report = i.find("ul",class_="nav navbar-nav post-nav")
				if report is not None:
					report.li.decompose()

				if i.find("div",class_="parrent") is not None:
					secondCmt = i.find("div",class_="parrent").find_all("li",recursive=False)
					for j in secondCmt:
						img = j.find("a",class_="pull-left comment-img")
						if img is not None:
							img.decompose()

						reaction = j.find("a",class_="link_edit")
						if reaction is not None:
							reaction.decompose()
						reaction = j.find("a",class_="link_edit")
						if reaction is not None:
							reaction.decompose()

						report = j.find("ul",class_="nav navbar-nav post-nav")
						if report is not None:
							report.li.decompose()
		contact = comment.find("div",class_="contact-form bottom")
		if contact is not None:
			contact.decompose()
		f.write(str(comment))

		f.write(html_footer)
		f.close()
		print("%d end" %(code))
		time.sleep(3)

pageUrl = "https://webcache.googleusercontent.com/search?q=cache:T6RhmYqtRpsJ:https://lilybin.tistory.com/9706+&cd=1&hl=ko&ct=clnk&gl=kr"
lilybin([pageUrl])