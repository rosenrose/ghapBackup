import os
import re
import urllib.request
import requests
import time
import sys
sys.path.append("C:/users/crazy/pictures/python")
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from replaceSpecialCh import replaceSpecialCh

url = "https://enlsparker.blogspot.com"
path = "D:/Touhou/doujin/enlsparker"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}

def writeLog(msg):
	with open("%s/%s"%(path,logfile),'a',encoding="utf-8-sig") as a:
		a.write(msg)

def enlsparker(postList):
	if selenium:
		driver = webdriver.Chrome("D:/Install/chromedriver.exe")

	for postUrl in postList:
		#end = code.find("-")
		#end = code.find("-",end+1)
		#date = code[:end+1]+"%02d"%(random.randint(1,28))
		date = input("date: ")

		code = postUrl.replace('/','-')[:-5]
		print("%s start" %(code))
		if selenium:
			driver.get("%s/%s"%(url,postUrl))
			soup = BeautifulSoup(driver.page_source,'html.parser')
		else:
			response = requests.get("%s/%s"%(url,postUrl),headers=headers)
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
		f.write("<div class=\"date\">%s</div><br/>\n" %(date))
		
		article = soup.find("div",class_="post-body entry-content")
		f.write("<div class=\"article\">\n")

		tmp = article.find_all("div")
		p = []
		for t in tmp:
			a = t.find("a",recursive=False)
			if a is not None:
				img = a.find("img",recursive=False)
				if img is not None:
					p.append(t)
				else:
					continue
			else:
				continue

		num = 1
		for i in p:
			if i.find("img").has_attr("src"):
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
				
				i.find("a").unwrap()
				for attr in list(i.find("img").attrs):
					if attr != "src":
						del i.find("img")[attr]
				i.find("img")["src"] = "%s_%s/%s"%(code,titleWin,fileName)
				num+=1
		f.write(str(article))
		f.write("</div><br/>\n")
		
		f.write("<div class=\"tagTrail\">\n")
		tag = soup.find("span",class_="post-labels")
		if tag is not None:
			tag = tag.find_all('a')
			f.write("\t<p>태그: </p>\n\t\t<ul>\n")
			for i in tag:
				f.write("\t\t\t<li>%s</li>\n"%(i.text))
			f.write("\t\t</ul>\n")
		f.write("</div><br/>\n")

		f.write(html_footer)
		f.close()
		print("%s end" %(code))

	if selenium:
		driver.quit()
	time.sleep(1)

selenium = False
pageUrl = "https://enlsparker.blogspot.com/search?updated-max=2019-02-01T01:32:00-08:00&max-results=30"
"""
while(True):
	response = requests.get(pageUrl,headers=headers)
	soup = BeautifulSoup(response.content,'html.parser')
	postUrls = []

	posts = soup.find_all("div",class_="post-outer")
	writeLog("="*30+"\n%s: %d posts\n" %(pageUrl,len(posts)))
	for p in posts:
		start = p.find("h3").find("a")['href'].find("com")
		postUrl = p.find("h3").find("a")['href'][start+4]
		postUrls.append(postUrl)
		writeLog("%s\n" %(postUrls[-1]))

	enlsparker(postUrls)

	next = soup.find("a",class_="blog-pager-older-link")
	if next is None:
		break

	pageUrl = next['href']
"""
enlsparker(sys.argv[1:])
