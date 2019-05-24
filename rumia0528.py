import os
import re
import urllib.request
import time
import sys
sys.path.append("C:/users/crazy/pictures/python")
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from replaceSpecialCh import replaceSpecialCh

url = "https://rumia0528.tistory.com"
path = "D:/Touhou/doujin/rumia0528"
logfile = "log.log"
html_footer = "\n</body>\n</html>"
catRegex = re.compile('(동방 동인지)')
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

def rumia0528(codeList):
	for code in codeList:
		print("%d start" %(code))
		driver.get("%s/%d" %(url, code))

		soup = BeautifulSoup(driver.page_source,"html.parser")
		notes = soup.find_all(text=lambda text:isinstance(text,bs4.element.Comment))
		for note in notes: note.extract()

		tdiv = soup.find("div",class_="tdiv")
		if tdiv is None:
			writeLog("%d does not exist\n" %(code))
			continue
		
		category = tdiv.find("div",class_="ect").find("a").text
		if not (catRegex.match(category)):
			writeLog("%d out of category (%s)\n" %(code, category))
			continue

		try:
			element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"imageblock")))
		except:
			writeLog("%d has no image\n" %(code))
			continue

		title = tdiv.find("h2").find("a").text
		left = title.find('[')
		right = title.find(']')
		if right != -1 and left == 0:
			title = title[right+1:].strip()

		date = tdiv.find_all("span")[1].text

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
		
		article = soup.find("div",class_="article")
		fold = article.find_all("p",class_=re.compile("moreless_*"))
		if fold is not None:
			for i in fold:
				i.decompose()
		fold = article.find_all("div",class_=re.compile("moreless_*"))
		if fold is not None:
			for i in fold:
				i.unwrap()
		article.find("div",class_="container_postbtn").decompose()
		article.find("div",class_="tt-plugin tt-share-entry-with-sns tt-sns-icon-alignment-center tt-sns-icon-size-big").decompose()
		another = article.find("div",class_="another_category another_category_color_gray").extract()

		p = article.find_all("img")
		f.write("<div class=\"article\">\n")
		i=0
		while(i < len(p)):
			if p[i].has_attr("filename"):
				fileExt = p[i]["filename"].split('.')[-1]
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
		f.write("</div><br/>\n")
		
		tag = soup.find('div',class_='tagTrail')
		f.write("<div class=\"tagTrail\">\n")
		if tag is not None:
			tag = tag.find_all('a')[1:]
			f.write("\t<p>태그: </p>\n\t\t<ul>\n")
			for i in tag:
				f.write("\t\t\t<li>%s</li>\n"%(i.text))
			f.write("\t\t</ul>\n</div><br/>\n")
		else:
			f.write("</div><br/>\n")

		f.write("<div class=\"another\">\n")
		f.write("\t<p>'%s' 카테고리의 다른 글</p>\n\t\t<ul>\n" %(category))
		another = another.find_all("tr")
		for i in another:
			anotherTitle = i.find("a").text
			anotherCode = codeRegex.findall(i.find("a")["href"])[1]
			f.write("\t\t\t<li><a href=\"%s.html\">%s</a></li>\n" %(anotherCode,anotherTitle))
		f.write("\t\t</ul>\n</div><br/>\n")
		
		comment = soup.find("div",class_="cb_lstcomment")
		if comment is not None:
			firstCmt = comment.ul.find_all("li",recursive=False)
			for i in firstCmt:
				report = i.find("span",class_="cb_date").find("a")
				if report is not None:
					report.decompose()

				reaction = i.find("div",class_="cb_section2")
				if reaction is not None:
					reaction.decompose()
				
				if i.ul is not None:
					secondCmt = i.ul.find_all("li",recursive=False)
					for j in secondCmt:
						report = j.find("span",class_="cb_date").find("a")
						if report is not None:
							report.decompose()

						reaction = j.find("div",class_="cb_section2")
						if reaction is not None:
							reaction.decompose()
			comment["class"] = "comment"
			f.write(str(comment))

		f.write(html_footer)
		f.close()
		print("%d end" %(code))
		time.sleep(3)

argStr = ""
for i in range(1,len(sys.argv)):
	if sys.argv[i].find('-') == -1:
		rumia0528([int(sys.argv[i])])
	else:
		c1 = sys.argv[i].split('-')[0]
		c2 = sys.argv[i].split('-')[1]
		rumia0528(range(int(c1),int(c2)+1))
	argStr = argStr + sys.argv[i] + " "
driver.quit()
os.chdir("c:/users/crazy/pictures/python")
os.system("python htmlToGit.py rumia0528 "+argStr.strip())