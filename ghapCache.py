import os
import re
import urllib.request
import requests
import time
import sys
from bs4 import BeautifulSoup
from selenium import webdriver

path = "D:/Touhou/doujin/ghap"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
catRegex = re.compile('(동방 동인지|합동인지|동방 웹코믹|세로 식질 유배소)')
codeRegex = re.compile('[0-9]*')
#headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"}

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

def ghap(cacheList):
	if selenium:
		driver = webdriver.Chrome("D:/Install/chromedriver.exe")

	for cache in cacheList:
		end = cache.find("+")
		start = cache.rfind("/",0,end)
		if end-start > 5:
			end = cache.find("category")
			end = end-3
		code = int(cache[start+1:end])
		
		print("%d start" %(code))
		if selenium:
			driver.get(cache)
			soup = BeautifulSoup(driver.page_source,'html.parser')
		else:
			response = requests.get(cache, headers=headers)
			if local:
				with open("C:/users/crazy/pictures/python/temp.html",'r',encoding="utf-8") as f:
					tmp = f.read()
				soup = BeautifulSoup(tmp,'html.parser')
			else:
				soup = BeautifulSoup(response.content,'html.parser')

		#print(soup)
		if mode == "d":
			tdiv = soup.find('div',class_='tdiv')
			category = tdiv.find('div',class_='ect').find('a').text
			title = tdiv.find('h2').find('a').text
			date = tdiv.find_all('span')[1].text
		else:
			tdiv = soup.find('div',class_='blogview_tit')
			category = tdiv.find('a',class_='txt_category').text
			title = tdiv.find('h2').text
			date = soup.find('time',class_='txt_date').text

		titleWin = replaceSpecialCh(title)
		doc = "%s/%d" %(path, code)
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
		f.write("<div class=\"category\">%s</div><br/>\n" %(category))
		f.write("<div class=\"date\">%s</div><br/>\n" %(date))
		
		if mode == "d":
			article = soup.find('div',class_='article')
		else:
			article = soup.find('div',class_='blogview_content')
		p = article.find_all('p')
		f.write("<div class=\"article\">\n")
		num = 1
		for i in p:
			if i.find('img') is not None:
				if mode == "d":
					imgSrc = i.find('img')['src']+"?original"
					fileExt = i.find('img')['filename'].split('.')[-1]
					fileName = "%03d.%s" %(num,fileExt)
				else:
					imgSrc = i.find('img')['src']
					start = imgSrc.find("fname")
					imgSrc = imgSrc[start+6:]
					imgSrc = imgSrc.replace("%3A",':').replace("%2F",'/').replace("image","original")
					fileName = "%03d.jpg" %(num)
					
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
					
				pos1 = str(i).find("<span class=\"imageblock\"")
				pos2 = str(i).find("</p>", pos1)
				f.write("\t"+str(i)[:pos1]+"<img src=\"%d_%s/%s\">" %(code,titleWin,fileName)+str(i)[pos2:]+"\n")
				num+=1
			else:
				f.write("\t"+str(i)+"\n")
		f.write("</div><br/>\n")
		
		f.write("<div class=\"tagTrail\">\n")
		if mode == "d":
			tag = soup.find('div',class_='tagTrail')
		else:
			tag = soup.find('div',class_='list_tag')

		if tag is not None:
			tag = tag.find_all('a')[1:]
			f.write("\t<p>태그: </p>\n\t\t<ul>\n")
			for i in tag:
				if mode == "d":
					f.write("\t\t\t<li>%s</li>\n"%(i.text))
				else:
					f.write("\t\t\t<li>%s</li>\n"%(i.text[1:]))
			f.write("\t\t</ul>\n</div><br/>\n")

		f.write("<div class=\"another\">\n")
		f.write("\t<p>'%s' 카테고리의 다른 글</p>\n\t\t<ul>\n" %(category))
		another = soup.find('div',class_='another_category another_category_color_gray')
		if another is not None:
			another = another.find('table').find_all('a')
			for i in another:
				anotherTitle = i.text
				anotherCode = codeRegex.findall(i['href'])[1]
				f.write("\t\t\t<li><a href=\"%s.html\">%s</a></li>\n" %(anotherCode, anotherTitle))
		f.write("\t\t</ul>\n</div><br/>\n")
		
		comment = soup.find('div',class_='cb_lstcomment')
		if comment is not None:
			firstCmt = comment.ul.find_all('li',recursive=False)
			for i in firstCmt:
				report = i.find_all('div',class_='cb_section')[1].find_all('span',recursive=False)[0].a
				if report is not None:
					report.decompose()

				modify = i.find_all('div',class_='cb_section')[1].find_all('span',recursive=False)[1]
				if modify is not None:
					modify.decompose()

				reply = i.find_all('div',class_='cb_section')[1].find_all('span',recursive=False)[1]
				if reply is not None:
					reply.decompose()
					
				if i.ul is not None:
					secondCmt = i.ul.find_all('li')
					for j in secondCmt:
						report = j.find_all('div',class_='cb_section')[1].find_all('span',recursive=False)[0].a
						if report is not None:
							report.decompose()

						modify = j.find_all('div',class_='cb_section')[1].find_all('span',recursive=False)[1]
						if modify is not None:
							modify.decompose()
			f.write(str(comment))

		f.write(html_footer)
		f.close()
		print("%d end" %(code))

	if selenium:
		driver.quit()

cachelist = []
while(True):
	temp = input()
	if temp == "q":
		break
	else:
		cachelist.append(temp)

mode = "m"
selenium = False
local = False
ghap(cachelist)