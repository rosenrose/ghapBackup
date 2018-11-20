import os
import re
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver

url = "https://ghaptouhou.tistory.com"
path = "D:/Touhou/ghap"
logfile = "log.log"
driver = webdriver.Chrome("D:/Install/chromedriver")
driver.implicitly_wait(5)
html_footer = "</body></html>"

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
	return res

for code in range(1, 101):
	print("%d start" %(code))
	driver.get("%s/%d" %(url, code))
	soup = BeautifulSoup(driver.page_source, 'html.parser')

	tdiv = soup.find('div', { 'class': 'tdiv' })
	if tdiv is None:
		writeLog("%d does not exist\n" %(code))
		continue

	category = tdiv.find('div', { 'class': 'ect' }).find('a').text
	catRegex = re.compile('(동방 동인지|합동인지|동방 웹코믹|세로 식질 유배소)')
	if not (catRegex.match(category)):
		writeLog("%d out of category\n" %(code))
		continue

	title = tdiv.find('h2').find('a').text
	date = tdiv.find_all('span')[1].text
	html_header = "<html><head><title>%s</title></head><body><br><h2>%s</h2><br>" %(title, title)

	titleWin = replaceSpecialCh(title)
	doc = "%s/%d_%s" %(path, code, titleWin)
	if not os.path.isdir(doc):
		os.mkdir(doc)

	f = open(doc+".html", "w", encoding="utf-8-sig")
	f.write(html_header)
	f.write("%s<br>%s<br>" %(category, date))

	article = soup.find('div', { 'class': 'article' })
	p = article.find_all('p')
	for i in p:
		if i.find('span',{'class':'imageblock'}) is not None:
			fileName = i.find('img')['filename']
			urllib.request.urlretrieve(i.find('img')['src'], "%s/%s" %(doc, fileName))
			pos1 = str(i).find("<span class=\"imageblock\"")
			pos2 = str(i).find("</p>", pos1)
			f.write(str(i)[:pos1]+"<img src=\"%d_%s/%s\"></p><br>" %(code, titleWin, fileName)+str(i)[pos2:])
		else:
			f.write(str(i))
	writeLog("%d contents done\n" %(code))
    			
	tag = soup.find('div', { 'class': 'tagTrail' }).find_all('a')[1:]
	f.write("<br><p>태그: </p><ul>")
	for i in tag:
		f.write("<li>%s</li>"%(i.text))
	f.write("</ul><br>")

	another = soup.find('div', { 'class': 'another_category another_category_color_gray' }).find('table').find_all('a')
	f.write("<p>'%s' 카테고리의 다른 글</p><ul>" %(category))
	codeRegex = re.compile('[0-9]*')
	for i in another:
		anotherTitle = i.text
		anotherTitleWin = replaceSpecialCh(anotherTitle)
		anotherCode = codeRegex.findall(i['href'])[1]
		f.write("<li><a href=\"%s_%s.html\">%s</a></li>" %(anotherCode, anotherTitleWin, anotherTitle))
	f.write("</ul><br>")

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
	writeLog("%d all done\n" %(code))
	f.close()
	print("%d end" %(code))
