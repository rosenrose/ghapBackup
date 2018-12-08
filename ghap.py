import os
import re
import urllib.request
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://ghaptouhou.tistory.com"
path = "D:/Touhou/ghap"
logfile = "log.log"
html_footer = "</body></html>"
driver = webdriver.Chrome("D:/Install/chromedriver.exe")
wait = WebDriverWait(driver,5)
catRegex = re.compile('(동방 동인지|합동인지|동방 웹코믹|세로 식질 유배소)')

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
	return res

def ghap(codeList):
	for code in codeList:
		print("%d start" %(code))
		driver.get("%s/%d" %(url, code))
		current_code = driver.current_url.split('/')[-1]

		soup = BeautifulSoup(driver.page_source, 'html.parser')
		tdiv = soup.find('div', { 'class': 'tdiv' })
		if (tdiv is None) or (int(current_code) != code):
			writeLog("%d does not exist\n" %(code))
			continue

		category = tdiv.find('div', { 'class': 'ect' }).find('a').text
		if not (catRegex.match(category)):
			writeLog("%d out of category (%s)\n" %(code, category))
			continue

		try:
			element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"imageblock")))
		except:
			writeLog("%d has no image\n" %(code))
			continue

		title = tdiv.find('h2').find('a').text
		date = tdiv.find_all('span')[1].text

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

		html_header = "<html><head><title>%s</title></head><body><br><h2>%s</h2><br>" %(title, title)
		f.write(html_header)
		f.write("<div class=\"category\">%s</div><br>" %(category))
		f.write("<div class=\"date\">%s</div><br>" %(date))

		article = soup.find('div', { 'class': 'article' })
		p = article.find_all('p')
		f.write("<div class=\"article\">")
		num = 1
		for i in p:
			if i.find('img') is not None and str(i.find('img')).find('filename')!=-1:
				imgSrc = i.find('img')['src']+"?original"
				fileExt = i.find('img')['filename'].split('.')[-1]
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
				pos1 = str(i).find("<span class=\"imageblock\"")
				pos2 = str(i).find("</p>", pos1)
				f.write(str(i)[:pos1]+"<img src=\"%d_%s/%s\"></p><br>" %(code,titleWin,fileName)+str(i)[pos2:])
				num+=1
			else:
				f.write(str(i))
		f.write("</div><br>")

		tag = soup.find('div', { 'class': 'tagTrail' })
		f.write("<div class=\"tagTrail\">")
		if tag is not None:
			tag = tag.find_all('a')[1:]
			f.write("<p>태그: </p><ul>")
			for i in tag:
				f.write("<li>%s</li>"%(i.text))
			f.write("</ul></div><br>")

		another = soup.find('div', { 'class': 'another_category another_category_color_gray' }).find('table').find_all('a')
		f.write("<div class=\"another\">")
		f.write("<p>'%s' 카테고리의 다른 글</p><ul>" %(category))
		codeRegex = re.compile('[0-9]*')
		for i in another:
			anotherTitle = i.text
			anotherCode = codeRegex.findall(i['href'])[1]
			f.write("<li><a href=\"%s.html\">%s</a></li>" %(anotherCode, anotherTitle))
		f.write("</ul></div><br>")

		comment = str(soup.find('div', { 'class': 'cb_module cb_fluid' }))
		while(comment.find("<a href=\"/toolbar") != -1):
			pos1 = comment.find("<a href=\"/toolbar")
			pos2 = comment.find("</span>", pos1)
			comment = comment[:pos1]+comment[pos2:]
			pos1 = comment.find("<span>")
			pos2 = comment.find("</div>", pos1)
			comment = comment[:pos1]+comment[pos2:]
		f.write(comment)

		f.write(html_footer)
		f.close()
		print("%d end" %(code))
		time.sleep(5)
	driver.quit()

ghap(range(1,5306))
