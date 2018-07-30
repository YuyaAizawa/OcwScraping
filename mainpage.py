import requests
from bs4 import BeautifulSoup

'''
OCWから学院一覧を取得するスクリプト(6個くらいだから必要ない気もする)
gakuinListの各要素は次のような辞書に鳴っている
{
	'name' : 学院名,
	'url' : その学院の授業の一覧のurl,
}
'''
def getGakuinList():
	url = "http://www.ocw.titech.ac.jp/"
	response = requests.get(url)
	soup = BeautifulSoup(response.content,"lxml")

	topMainNav = soup.find("ul",id="top-mein-navi")

	gakubus = topMainNav.find_all(class_="gakubuBox")

	gakuinList = []
	for gakubu_div in gakubus:
		gakuin = gakubu_div.find(class_="gakubuHead").span.string
		if gakuin[-2::] != "学院":
			continue
		gakuin_url = url + gakubu_div.parent['href']
		gakuinList.append({'name':gakuin,'url':gakuin_url})

	return gakuinList

'''
学院名とurlを渡されたらその学院の授業一覧を持ってくる
'''
def getLectures(name,url):
	urlprefix = "http://www.ocw.titech.ac.jp"
	response = requests.get(url)
	soup = BeautifulSoup(response.content,'lxml')
	table = soup.find('table',class_='ranking-list').tbody

	for item in table.find_all('tr'):
		code = item.find('td',class_='code').string
		name = item.find('td',class_='course_title').a.string #講義名
		lecture_url = urlprefix + item.find('td',class_='course_title').a['href']
		teachers = [te.string for te in item.find('td',class_='lecturer').find_all('a')]
		quater = item.find('td',class_='opening_department').a.string	#TODO ちゃんととれてない
		if not name or not code:	# 文字列が空の場合はスキップ
			continue
		if code:
			code = code.strip()
		if name:
			name = name.strip()
		if quater:
			quater = quater.strip()
		print(name)
		print(teachers)
		print(lecture_url)
		print(quater)


if __name__=='__main__':
	#print(getGakuinList())
	getLectures('情報理工学院','http://www.ocw.titech.ac.jp/index.php?module=General&action=T0100&GakubuCD=4&lang=JA')
