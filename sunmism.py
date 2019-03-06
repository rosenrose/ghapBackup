import os
import re
import urllib.request
import time
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.sunmism.com"
path = "D:/Touhou/doujin/sunmism"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
catRegex = re.compile('(코믹/동인지|코믹/웹코믹)')
codeRegex = re.compile('[0-9]*')

#options = webdriver.ChromeOptions()
#options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36")
#driver = webdriver.Chrome("D:/Install/chromedriver.exe", chrome_options=options)
driver = webdriver.Chrome("D:/Install/chromedriver.exe")
wait = WebDriverWait(driver,5)
#driver.implicitly_wait(3)

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

def sunmism(codeList):
	for code in codeList:
		print("%d start" %(code))
		driver.get("%s/%d" %(url, code))

		soup = BeautifulSoup(driver.page_source,"html.parser")
		tdiv = soup.find("div",class_="jb-content-title jb-content-title-article")
		if tdiv is None:
			writeLog("%d does not exist\n" %(code))
			continue
		
		category = tdiv.find("span",class_="jb-article-information-category").find("a").text.strip()
		if not (catRegex.match(category)):
			writeLog("%d out of category (%s)\n" %(code, category))
			continue
		else:
			writeLog("%d: %s\n"%(code,category))
		"""
		try:
			element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"imageblock")))
		except:
			writeLog("%d has no image\n" %(code))
			continue"""

		title = tdiv.find("h2").find("a").text
		date = tdiv.find("span",class_="jb-article-information-date").text.strip()

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
	
		article = soup.find("div",class_="jb-article")
		fold = article.find_all("p",class_=re.compile("moreless_*"))
		if fold is not None:
			for i in fold:
				i.decompose()
		fold = article.find_all("div",class_="moreless_content")
		if fold is not None:
			for i in fold:
				i.unwrap()
		article.find("div",class_="container_postbtn").decompose()
		
		ads = article.find_all("script")
		if ads is not None:
			for ad in ads:
				ad.decompose()
		ads = article.find_all("ins")
		if ads is not None:
			for ad in ads:
				ad.decompose()

		p = article.find_all("img")
		f.write("<div class=\"article\">\n")
		num = 1
		if p is not None:
			for i in p:
				if i.has_attr("filename"):
					fileExt = i["filename"].split('.')[-1]
				elif i["src"].find("www16") == -1:
					if i.has_attr("filemime"):
						if i["filemime"].find("jp") != -1:
							fileExt = "jpg"
						else:
							fileExt = "png"
					else:
						fileExt = "jpg"
					#writeLog("%d_%d has no filename\n" %(code,num))
				else:
					continue
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
				
				for attr in list(i.attrs):
					if attr != "src":
						del i[attr]
				i.attrs["src"] = "%d_%s/%s" %(code,titleWin,fileName)
				num+=1


		f.write(str(article))
		f.write("</div><br/>\n")
		
		tag = soup.find("span",class_="jb-article-tag-list")
		f.write("<div class=\"tagTrail\">\n")
		if tag is not None:
			tag = tag.find_all("a")
			f.write("\t<p>태그: </p>\n\t\t<ul>\n")
			for i in tag:
				f.write("\t\t\t<li>%s</li>\n"%(i.text))
			f.write("\t\t</ul>\n</div><br/>\n")

		f.write("<div class=\"another\">\n")
		f.write("\t<p>'%s' 관련 글</p>\n\t\t<ul>\n" %(category))
		another = soup.find("div",class_="jb-related").find_all("div",class_="jb-related-table")
		for i in another:
			anotherTitle = i.find("h4").text
			anotherCode = codeRegex.findall(i.find("a")["href"])[1]
			f.write("\t\t\t<li><a href=\"%s.html\">%s</a></li>\n" %(anotherCode, anotherTitle))
		f.write("\t\t</ul>\n</div><br/>\n")
		
		comment = soup.find("div",class_="jb-discuss-list jb-discuss-list-comment")
		if comment is not None:
			firstCmt = comment.ul.find_all("li",class_="rp_general",recursive=False)
			for i in firstCmt:
				report = i.find("span",class_="jb-discuss-information-date").find("a")
				if report is not None:
					report.decompose()

				reaction = i.find("div",class_="jb-discuss-reaction")
				if reaction is not None:
					reaction.decompose()
				
				if i.ul is not None:
					secondCmt = i.ul.find_all("li",recursive=False)
					for j in secondCmt:
						report = j.find("span",class_="jb-discuss-information-date").find("a")
						if report is not None:
							report.decompose()

						reaction = j.find("div",class_="jb-discuss-reaction")
						if reaction is not None:
							reaction.decompose()
			f.write(str(comment))

		f.write(html_footer)
		f.close()
		print("%d end" %(code))
		time.sleep(2)


for i in range(1,len(sys.argv)):
	if sys.argv[i].find('-') == -1:
		sunmism([int(sys.argv[i])])
	else:
		c1 = sys.argv[i].split('-')[0]
		c2 = sys.argv[i].split('-')[1]
		sunmism(range(int(c1),int(c2)+1))
driver.quit()