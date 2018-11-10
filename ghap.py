import os
import re
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver

url = "https://ghaptouhou.tistory.com"
path = "D:/Touhou/ghap"
driver = webdriver.Chrome("D:\\Install\\chromedriver")
driver.implicitly_wait(5)

for code in range(9, 11):
	driver.get("%s/%d" %(url, code))
	soup = BeautifulSoup(driver.page_source, 'html.parser')

	tdiv = soup.find('div', { 'class': 'tdiv' })
	category = tdiv.find('div', { 'class': 'ect' }).find('a').text

	catRegex = re.compile('(동방 동인지|합동인지|동방 웹코믹|세로 식질 유배소)')
	if(catRegex.match(category)):
		title = tdiv.find('h2').find('a').text
		date = tdiv.find_all('span')[1].text
		html_header = "<html><head><title>%s</title></head><body><br><h1>%s</h1><br>" %(title, title)
		html_footer = "</body></html>"
		
		if not os.path.isdir("%s/%s_%d" %(path, title, code)):
			os.mkdir("%s/%s_%d" %(path, title, code))

		f = open("%s/%s_%d.html" %(path, title, code), "w", encoding="utf-8-sig")
		f.write(html_header)
		article = soup.find('div', { 'class': 'article' })

		p = article.find_all('p')
		for i in p:
			if i.find('span',{'class':'imageblock'}) is not None:
				urllib.request.urlretrieve(i.find('img')['src'], '%s/%s_%d/%s' %(path, title, code, i.find('img')['filename']))
				pos1 = str(i).find("<span class=\"imageblock\"")
				pos2 = str(i).find("</p>", pos1)
				f.write(str(i)[:pos1]+"<img src=\"%s_%d/%s\"></p><br>" %(title, code, i.find('img')['filename'])+str(i)[pos2:])
			else:
				f.write(str(i))
    			
		tag = soup.find('div', { 'class': 'tagTrail' }).find_all('a')[1:]
		f.write("<br><p>태그: </p><ul>")
		for i in tag:
			f.write("<li>%s</li>"%(i.text))
		f.write("</ul><br>")

		another = soup.find('div', { 'class': 'another_category another_category_color_gray' }).find('table').find_all('a')
		f.write("<p>'%s' 카테고리의 다른 글</p><ul>" %(category))
		codeRegex = re.compile('[0-9]*')
		for i in another:
			f.write("<li><a href=\"%s_%s.html\">%s</a></li>" %(i.text, codeRegex.findall(i['href'])[1], i.text))
		f.write("</ul><br>")

		comment = soup.find('div', { 'class': 'comment' })
		f.write(str(comment))

		f.write(html_footer)
		f.close()
