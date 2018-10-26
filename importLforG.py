import pymysql
import requests
from bs4 import BeautifulSoup

'''
    importLforG.py

Lecture for Gakuin
いい名称出てこなかった
講義と学院の対応づけだけ更新したい時用(講義ページ重いので)
'''

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='test_ocw',
                             charset='utf8',
                             # Selectの結果をdictionary形式で受け取る
                             cursorclass=pymysql.cursors.DictCursor)

#データベースのカラム情報
#科目コードをキーとして持たせたい気持ち
column = {# TOP側 #
          "科目コード":"LectureCode", # キー
          "講義名":"LectureName",
          "担当教員名":"Professor",
          "開講元":"Department",
          "曜日・時限(講義室)":"DateRoom",
          "URL":"URL",
         #"講義室":"Room",
          "単位数":"Credit",
          "開講クォーター":"Quarter",
          "使用言語":"Language",
          # シラバス側 #
          "授業計画・課題":"LecturePlan",
          "成績評価の基準及び方法":"AssessStyle",
          "履修の条件(知識・技能・履修済科目等)":"CourseCond",
          # 検索用 #
          "学院":"Gakuin"}

#limit値　越えて設定した場合，要素数ぶんが最大になる
Glimit = 99 #頭からいくつ学院数見るか
Llimit = 9999 #頭からいくつ講義詳細見るか

def getGakuinList():
	url = "http://www.ocw.titech.ac.jp/"
	response = requests.get(url)
	soup = BeautifulSoup(response.content,"lxml")

	print("Get GakuinList")

	topMainNav = soup.find("ul",id="top-mein-navi")

	gakubus = topMainNav.find_all(class_="gakubuBox")

	gakuinList = []
	for gakubu_div in gakubus:
		gakuin = gakubu_div.find(class_="gakubuHead").span.string
		#if gakuin[-2::] != "学院":
		#	continue
		gakuin_url = url + gakubu_div.parent['href']
		gakuinList.append({'gakuin':gakuin,'gakuin_url':gakuin_url})

	return gakuinList

'''
学院名とurlを渡されたらその学院の授業一覧を持ってくる
'''
def getLectures(name,url):
    urlprefix = "http://www.ocw.titech.ac.jp"
    response = requests.get(url)
    soup = BeautifulSoup(response.content,'lxml')

    print("\tGet Lectures:",name)

    tables = soup.find_all('table',class_='ranking-list')

    LecList = []

    for t in tables:
        table = t.tbody
        for item in table.find_all('tr'):
            code = item.find('td',class_='code').string
            name = item.find('td',class_='course_title').a.string #講義名
            lecture_url = urlprefix + item.find('td',class_='course_title').a['href']
            teachers = [te.string for te in item.find('td',class_='lecturer').find_all('a')]
            quaterColumn = item.find('td',class_='opening_department')	#TODO テーブルに開講元カラムが存在しない場合に対応する
            quater = quaterColumn.a.string if quaterColumn is not None else ''
            if not name or not code:	# 文字列が空の場合はスキップ
                continue
            if code:
                code = code.strip()
            if name:
                name = name.strip()
            if quater:
                quater = quater.strip()
            #print(name)
            #print(teachers)
            #print(lecture_url)
            #print(quater)

            LecList.append({"code":code,"name":name,"lecture_url":lecture_url})

    return LecList

#LectureとGakuinの結びつきデータベースの挿入操作
def insertLforG(column,code,gakuin):
    with connection.cursor() as cursor:
        sql = "INSERT IGNORE INTO LforG ({},{}) ".format(column["科目コード"],column["学院"])
        sql += "VALUES (\'{}\',\'{}\') ".format(code,gakuin)
        cursor.execute(sql)
        print("\t\tUPDATE LforG:",code,"-",gakuin)

#OCWスクレイピング実行
if __name__=='__main__':
    print("OCW LforGデータのスクレイピングを始めます")
    for Gakuin in getGakuinList()[6:7]:
        for Lecture in getLectures(Gakuin["gakuin"],Gakuin["gakuin_url"]):
            insertLforG(column,Lecture["code"],Gakuin["gakuin"])
            connection.commit()
    print("OCW LforGデータのスクレイピングを完了しました")
