import urllib.request
import requests
import os
import re
import time
import sys
sys.path.append("C:/users/crazy/pictures/python")
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from replaceSpecialCh import replaceSpecialCh

path = "D:/Touhou/doujin/dcinside"
url = "https://gall.dcinside.com/board/view/?id=touhou&no="
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
logfile = "log.log"
html_footer = "\n</body>\n</html>"
codeRegex = re.compile('[0-9]*')

#options = webdriver.ChromeOptions()
#options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36")
#driver = webdriver.Chrome("D:/Install/chromedriver.exe", chrome_options=options)
driver = webdriver.Chrome("D:/Install/chromedriver.exe")
#wait = WebDriverWait(driver,5)

def writeLog(msg):
	with open("%s/%s"%(path,logfile),"a",encoding="utf-8-sig") as a:
		a.write(msg)

def dc(codeList):
	for code in codeList:
		print("%d start" %(code))
		#response = requests.get(url+str(code),headers = headers)
		#soup = BeautifulSoup(response.content,"html.parser")
		driver.get(url+str(code))		
		soup = BeautifulSoup(driver.page_source,"html.parser")

		tdiv = soup.find("div",class_="gallview_head clear ub-content")
		date = tdiv.find("span",class_="gall_date")
		if date is not None:
			date = date["title"]
		else:
			date = input("date: ")
		title = tdiv.find("h3").text

		if title.find("[") != -1:
			end = title.find("]")
			title = title[end+1:].strip()
		elif title.find("(") <=1:
			end = title.find(")")
			title = title[end+1:].strip()
		ans = input(title)
		if ans == "n":
			title = input()

		titleWin = replaceSpecialCh(title)
		print(titleWin)
		doc = "%s/%d" %(path,code)
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
		f.write("<div class=\"date\">%s</div><br/>\n" %(date))

		article = soup.find("div",style="overflow:hidden;")
		p = article.find_all("img")
		f.write("<div class=\"article\">\n")

		i=0
		while (i < len(p)):
			if p[i].has_attr("onclick"):
				imgSrc = p[i]["onclick"].split('\'')[1].replace("Pop","")
			elif p[i]["src"].find("blogspot") != -1:
				imgSrc = p[i]["src"].replace("s1600","s0")
			elif p[i].has_attr("class") and "written_dccon" in p[i]["class"]:
				p[i].decompose()
				p.remove(p[i])
				continue
			else:
				imgSrc = p[i]["src"]
				print("External Source")

			fileName = "%03d.jpg"%(i+1)
			imgSrc = imgSrc.replace("https","http")
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
			
			p[i].attrs["src"] = "%d_%s/%s" %(code,titleWin,fileName)
			for attr in list(p[i].attrs):
				if attr != "src":
					del p[i][attr]
			i+=1
		f.write(str(article))
		f.write("</div><br/>\n")

		tagList = []
		tags = input(str(code)+" tag: ")
		if tags != "":
			for tag in tags.split(" "):
				tagList.append(tag)
		f.write("<div class=\"tagTrail\">\n")
		f.write("\t<p>태그: </p>\n\t\t<ul>\n")
		for i in tagList:
			f.write("\t\t\t<li>%s</li>\n"%(i))
		f.write("\t\t</ul>\n")
		f.write("</div><br/>\n")

		banWord = ["강간"]
		comment = soup.find("div",class_="comment_box")
		if comment is not None:
			firstCmt = comment.ul.find_all("li",recursivce=False)
			for i in firstCmt:
				remove = i.find("div",class_="cmt_mdf_del")
				if remove is not None:
					remove.decompose()

				if i.has_attr("id") and (i["id"] == "comment_li_0"):
					i.decompose()

				nick = i.find("span",class_="gall_writer ub-writer")
				if nick is not None and nick.find("em") is not None:
					nick.find("em").unwrap()
					for ban in banWord:
						if nick.text.find(ban) != -1:
							nick["data-nick"] = nick["data-nick"].replace(ban,"")
							nick2 = nick.find("span",class_="nickname in")
							nick2["title"] = nick2["title"].replace(ban,"")
							nick2.string = nick2.string.replace(ban,"")

				if i.find("ul",class_="reply_list") is not None:
					secondCmt = i.find("ul",class_="reply_list").find_all("li",recursivce=False)
					for j in secondCmt:
						remove = j.find("div",class_="cmt_mdf_del")
						if remove is not None:
							remove.decompose()

						if j.has_attr("id") and (j["id"] == "comment_li_0"):
							j.decompose()

						nick = j.find("span",class_="gall_writer ub-writer")
						if nick is not None and nick.find("em") is not None:
							nick.find("em").unwrap()
							for ban in banWord:
								if nick.text.find(ban) != -1:
									nick["data-nick"] = nick["data-nick"].replace(ban,"")
									nick2 = nick.find("span",class_="nickname in")
									nick2["title"] = nick2["title"].replace(ban,"")
									nick2.string = nick2.string.replace(ban,"")

			comment.find("div",class_="bottom_paging_box").decompose()
			comment["class"] = "comment"
			f.write(str(comment))

		f.write(html_footer)
		f.close()
		print("%d end" %(code))
		time.sleep(3)

for i in range(1,len(sys.argv)):
	if sys.argv[i].find('-') == -1:
		dc([int(sys.argv[i])])
	else:
		c1 = sys.argv[i].split('-')[0]
		c2 = sys.argv[i].split('-')[1]
		dc(range(int(c1),int(c2)+1))
driver.quit()
subprocess.run(["python","htmlToGit.py","dcinside","add"]+sys.argv[1:],encoding="utf-8",cwd="c:/users/crazy/pictures/python")