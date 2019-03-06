import os
import re
import urllib.request
import requests
import time
import sys
from bs4 import BeautifulSoup
from selenium import webdriver

path = "D:/Touhou/doujin/enlsparker"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}

def writeLog(msg):
	with open("%s/%s"%(path,logfile),'a',encoding="utf-8-sig") as a:
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

def ghap(postList):
	if selenium:
		driver = webdriver.Chrome("D:/Install/chromedriver.exe")

	for postUrl in postList:
		start = postUrl.find("com")
		code = postUrl[start+4:-5].replace('/','-')
		
		print("%s start" %(code))
		if selenium:
			driver.get(postUrl)
			soup = BeautifulSoup(driver.page_source,'html.parser')
		else:
			response = requests.get(postUrl,headers=headers)
			soup = BeautifulSoup(response.content,'html.parser')

		title = soup.find("div",class_="post hentry").find("h3").text.strip()
		titleWin = replaceSpecialCh(title)
		doc = "%s/%s" %(path, code)
		if not os.path.isdir("%s_%s" %(doc,titleWin)):
			try:
				os.mkdir("%s_%s" %(doc,titleWin))
			except:
				writeLog("Making \'%s_%s\' folder fail\n" %(doc,titleWin))
				return

		try:
			f = open(doc+".html", "w", encoding="utf-8-sig")
		except:
			writeLog("Making \'%s\' file fail\n" %(title))
			f.close()
			return
		
		html_header = "<html>\n<head>\n\t<title>%s</title>\n</head>\n<body>\n\t<h2>%s</h2><br/>\n" %(title, title)
		f.write(html_header)
		
		article = soup.find("div",class_="post-body entry-content")
		p = article.find_all("div")
		f.write("<div class=\"article\">\n")
		num = 1
		for i in p:
			if i.find("img") is not None and i.find("img").has_attr("src"):
				imgSrc = i.find("img")["src"].replace("s1600","s0")
				if imgSrc.find("http") == -1:
					imgSrc = "https:" + imgSrc
				fileExt = imgSrc.split('.')[-1]
				fileName = "%03d.%s" %(num,fileExt)
				
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
					
				pos1 = str(i).find("<a href=")
				pos2 = str(i).find("</div>", pos1)
				f.write("\t"+str(i)[:pos1]+"<img src=\"%s_%s/%s\">" %(code,titleWin,fileName)+str(i)[pos2:]+"\n")
				num+=1
			else:
				f.write("\t"+str(i)+"\n")
		f.write("</div><br/>\n")
		
		f.write("<div class=\"tagTrail\">\n")
		tag = soup.find("span",class_="post-labels")
		if tag is not None:
			tag = tag.find_all('a')
			f.write("\t<p>태그: </p>\n\t\t<ul>\n")
			for i in tag:
				f.write("\t\t\t<li>%s</li>\n"%(i.text))
			f.write("\t\t</ul>\n</div><br/>\n")

		f.write(html_footer)
		f.close()
		print("%s end" %(code))

	if selenium:
		driver.quit()
	time.sleep(3)

selenium = False
pageUrl = "https://enlsparker.blogspot.com/search?updated-max=2014-01-24T05:12:00-08:00&max-results=30&start=3210&by-date=false"

while(True):
	response = requests.get(pageUrl,headers=headers)
	soup = BeautifulSoup(response.content,'html.parser')
	postUrls = []

	posts = soup.find_all("div",class_="post-outer")
	writeLog("="*30+"\n%s: %d posts\n" %(pageUrl,len(posts)))
	for p in posts:
		postUrls.append(p.find("h3").find("a")['href'])
		writeLog("%s\n" %(postUrls[-1]))

	ghap(postUrls)

	next = soup.find("a",class_="blog-pager-older-link")
	if next is None:
		break

	pageUrl = next['href']

#ghap(["http://enlsparker.blogspot.com/2014/01/blog-post_12.html"])