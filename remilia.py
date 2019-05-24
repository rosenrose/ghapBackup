import urllib.request
import requests
import os
from bs4 import BeautifulSoup 

path = "D:/Touhou/remilia"
prefix = "http://gall.dcinside.com/board/view/?id=touhou&no="
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
imgHeight = 700

def crawl():
	with open ("%s/remilia.txt" %(path), "r", encoding="utf-8-sig") as f:
		lines = f.readlines()

	for i in range(len(lines)):
		if i%2 == 0:
			line = lines[i].split(" ")
			code = line[len(line)-1].strip()
			food=""
			for j in range(len(line)-1):
				food += (line[j]+" ")
			food = food.strip()

			response = requests.get(prefix+code, headers = headers)
			soup = BeautifulSoup(response.content, 'html.parser')
			div = soup.find('div', { 'class':'s_write' })
			images = div.find_all('img', { 'class':'txc-image' })
			table = str(div.find('table'))

			title = "%s %s" %(code, food)
			if not os.path.isdir("%s/%s" %(path, title)):
				os.mkdir("%s/%s" %(path, title))

			html_header = """
			<html>
			<head>
			<title>%s</title>
			</head>
			<body>
			<br>
			<h1>%s</h1>
			<br>
			""" %(title, food)
			html_footer = """</body>
			</html>"""

			if i > 0:
				for j in range(len(images)):
					imgUrl = images[j].get('onclick').split('\'')[1]
					imgUrl = imgUrl.replace("Pop","")
					urllib.request.urlretrieve(imgUrl, '%s/%s/%02d.png' %(path, title, j+1))

					pos1 = table.find("onclick")
					pos2 = table.find("src", pos1)
					table = table[:pos1]+table[pos2:]
					pos2 = table.find("src", pos1)
					pos3 = table.find("style", pos2)
					filePath = "%s/%s/%02d.png" %(path,title,j+1)
					table = table[:pos2+5]+filePath+"\" height=\"%d" %(imgHeight)+table[pos3-2:]

				with open ("%s/%s.html" %(path,title), "w", encoding="utf-8-sig") as f:
					f.write(html_header)
					f.write(table + "<br>"*3)
					prev_line = lines[i-2].split(" ")
					prev_code = prev_line[len(prev_line)-1].strip()
					prev_food = ""
					for j in range(len(prev_line)-1):
						prev_food += (prev_line[j]+" ")
					prev_food = prev_food.strip()
					prev_title = prev_code+" "+prev_food
					prev = "<a href=\"%s/%s.html\">이전</a>"%(path,prev_title)
					f.write(prev)
					if i < len(lines)-2:
						next_line = lines[i+2].split(" ")
						next_code = next_line[len(next_line)-1].strip()
						next_food = ""
						for j in range(len(next_line)-1):
							next_food += (next_line[j]+" ")
						next_food = next_food.strip()
						next_title = next_code+" "+next_food
						next = "&nbsp"*5 + "<a href=\"%s/%s.html\">다음</a>"%(path,next_title)
						f.write(next)
					f.write(html_footer)

				files = os.listdir("%s/%s" %(path,title))
				for file in files:
					ffmpegInput = "%s/%s/%s" %(path,title,file)
					os.system("C:/Users/crazy/Pictures/ffmpeg -i \"%s\" -vf \"crop=944:1544:0:122\" -y \"%s\"" %(ffmpegInput,ffmpegInput))
			else:
				with open ("%s/%s.html" %(path,title), "r", encoding="utf-8-sig") as f:
					html = f.read()

				pos = html.find("</body>")
				next_line = lines[i+2].split(" ")
				next_code = next_line[len(next_line)-1].strip()
				next_food = ""
				for j in range(len(next_line)-1):
					next_food += (next_line[j]+" ")
				next_food = next_food.strip()
				next_title = next_code+" "+next_food
				next = "&nbsp"*5 + "<a href=\"%s/%s.html\">다음</a>"%(path,next_title)

				html = html[:pos]+next+html[pos:]
				with open ("%s/%s.html" %(path,title), "w", encoding="utf-8-sig") as f:
					f.write(html)

crawl()