import os
import re
import urllib.request
import time
import sys
sys.path.append("C:/users/crazy/pictures/python")
import bs4
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from replaceSpecialCh import replaceSpecialCh

url = "https://nonicname.tistory.com"
path = "D:/Touhou/doujin/nonicname"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
catRegex = re.compile('(동방 동인지|합동인지|동방 웹코믹|세로 식질 유배소)')
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

def nonicname(codeList):
	for code in codeList:
		print("%d start" %(code))
		driver.get("%s/%d" %(url, code))

		soup = BeautifulSoup(driver.page_source,"html.parser")
		notes = soup.find_all(text=lambda text:isinstance(text,bs4.element.Comment))
		for note in notes: note.extract()

		tdiv = soup.find("div",class_="area_title")
		if tdiv is None:
			writeLog("%d does not exist\n" %(code))
			continue
		
		category = tdiv.find("strong",class_="tit_category").find("a").text

		try:
			element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"imageblock")))
		except:
			writeLog("%d has no image\n" %(code))
			continue

		date = tdiv.find("span",class_="txt_detail my_post").text.replace("nonicname","").strip()
		title = tdiv.find("h3").find("a").text
		left = title.find('[')
		right = title.find(']')
		if right != -1 and left == 0:
			author = title[left+1:right]
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
		
		article = soup.find("div",class_="tt_article_useless_p_margin")
		article.find("div",class_="container_postbtn").decompose()

		p = article.find_all("img")
		f.write("<div class=\"article\">\n")
		i=0
		while(i < len(p)):
			if p[i].has_attr("filename"):
				fileExt = i.find("img")["filename"].split('.')[-1]
			elif p[i].has_attr("filemime"):
				if p[i]["filemime"].find("jp") != -1:
					fileExt = "jpg"
				else:
					fileExt = "png"
			else:
				fileExt = "jpg"
				
			imgSrc = p[i]["src"]+"?original"
			fileName = "%03d.%s" %(i+1,fileExt)
				
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
				
			for attr in list(p[i].attrs):
				if attr != "src":
					del p[i][attr]
			p[i].attrs["src"] = "%d_%s/%s" %(code,titleWin,fileName)
			i+=1
		f.write(str(article))
		f.write("\n<p>작가: %s</p><br/>\n"%(author))
		f.write("</div><br/>\n")
		
		tag = soup.find("dl",class_="list_tag")
		f.write("<div class=\"tagTrail\">\n")
		if tag is not None:
			tag = tag.find("dd",class_="desc_tag").find_all("a")
			f.write("\t<p>태그: </p>\n\t\t<ul>\n")
			for i in tag:
				f.write("\t\t\t<li>%s</li>\n"%(i.text))
			f.write("\t\t</ul>\n</div><br/>\n")
		else:
			f.write("</div><br/>\n")
		
		comment = soup.find("ul",class_="list_reply")
		if comment is not None:
			firstCmt = comment.find_all("li",recursive=False)
			for i in firstCmt:
				img = i.find("img")
				if img is not None:
					img.decompose()

				report = i.find("span",class_="txt_date").find("a")
				if report is not None:
					report.decompose()

				reaction = i.find("div",class_="my_edit")
				if reaction is not None:
					reaction.decompose()

				content = i.find("span",class_="txt_reply")
				if content is not None:
					content.name = "div"

				button = i.find("button",class_="btn_replymenu")
				if button is not None:
					button.decompose()
				
				if i.ul is not None:
					secondCmt = i.ul.find_all("li",recursive=False)
					for j in secondCmt:
						img = j.find("img")
						if img is not None:
							img.decompose()

						report = j.find("span",class_="txt_date").find("a")
						if report is not None:
							report.decompose()

						reaction = j.find("div",class_="my_edit")
						if reaction is not None:
							reaction.decompose()

						content = j.find("span",class_="txt_reply")
						if content is not None:
							content.name = "div"

						button = i.find("button",class_="btn_replymenu")
						if button is not None:
							button.decompose()
			f.write(str(comment))
		else:
			f.write("<div class=\"cb_lstcomment\">\n</div><br/>\n")

		f.write(html_footer)
		f.close()
		print("%d end" %(code))
		time.sleep(3)

for i in range(1,len(sys.argv)):
	if sys.argv[i].find('-') == -1:
		nonicname([int(sys.argv[i])])
	else:
		c1 = sys.argv[i].split('-')[0]
		c2 = sys.argv[i].split('-')[1]
		nonicname(range(int(c1),int(c2)+1))
driver.quit()
subprocess.run(["python","htmlToGit.py","nonicname","add"]+sys.argv[1:],encoding="utf-8",cwd="c:/users/crazy/pictures/python")