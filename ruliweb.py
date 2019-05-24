import urllib.request
import requests
import os
import re
import time
import sys
sys.path.append("C:/users/crazy/pictures/python")
from bs4 import BeautifulSoup
from replaceSpecialCh import replaceSpecialCh

path = "D:/Touhou/doujin/ruliweb"
url = "https://bbs.ruliweb.com/family/211/board/300545/read/"
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
logfile = "log.log"
html_footer = "\n</body>\n</html>"
codeRegex = re.compile('[0-9]*')


def writeLog(msg):
	with open("%s/%s"%(path,logfile),"a",encoding="utf-8-sig") as a:
		a.write(msg)

def ruliweb(codeList):
	for code in codeList:
		print("%d start" %(code))

		response = requests.get(url+str(code), headers = headers)
		soup = BeautifulSoup(response.content,"html.parser")
		title = soup.find("h4",class_="subject").text
		date = soup.find("span",class_="regdate").text

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

		article = soup.find("div",class_="view_content")
		p = article.find_all("img")
		f.write("<div class=\"article\">\n")
		num = 1
		for i in p:
			imgSrc = "https:"+i["src"].replace("img","ori")
			fileExt = i["src"].split(".")[-1]
			fileName = "%03d.%s"%(num,fileExt)

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
		
		f.write(html_footer)
		f.close()
		print("%d end" %(code))
		time.sleep(3)			

argStr = ""
for i in range(1,len(sys.argv)):
	if sys.argv[i].find('-') == -1:
		ruliweb([int(sys.argv[i])])
		argStr = argStr + sys.argv[i] + " "
	else:
		c1 = sys.argv[i].split('-')[0]
		c2 = sys.argv[i].split('-')[1]
		ruliweb(range(int(c1),int(c2)+1))

os.chdir("c:/users/crazy/pictures/python")
os.system("python htmlToGit.py ruliweb "+argStr.strip())