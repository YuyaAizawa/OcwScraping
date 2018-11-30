import pymysql
import sys
import traceback
import requests
from bs4 import BeautifulSoup

'''
    importOCW.py

講義情報のテーブルにOCWからスクレイピングしてきた講義情報を格納していきます
中断して続きからやるみたいな器用なことはできないので，main部いじってそれっぽくしてください(ごめん)
全データ取得を前提とした記述になっていますが，limitでそれなりに限度をいじれます
記述を変更するとしたらconnection，各Limit値，column，main部のいずれかのハズです
(PRIMARY KEY設定を変更する場合，insertLecture()を少し変える必要があります)

0-7の値を引数に与えると，そのindexの学院でScrapingが行われます

connectionとcolumnの情報はrecreateOCWTable.pyとおなじにしてね！
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
Llimit = 1 #頭からいくつ講義詳細見るか

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

#Q.曜日・時限が複数になった時もリスト構造にするか(今はリスト構造になっていない)
#各教員にaタグが入っている前提で以下の様になっている
#アクセスランキングは必要に感じなかったので空

#時折text内に凄いへんな文字が入る可能性がある(元のOCWの書かれ方のせい)
def fetch_OCW(Gakuin,Lecture):
    response = requests.get(Lecture["lecture_url"])
    soup = BeautifulSoup(response.content, "html.parser")
    print("\t\tSCRAPE Lecture:",Lecture["name"])

    OCW = {}

    for key in soup.find(attrs={"class":"gaiyo-data clearfix"}).find_all("dl"): #上部
        value_list = []
        for value in key.dd.strings:
            value = value.strip().replace(', ', ',').replace(',', ', ')
            if len(value)>0: value_list.append(value)
        OCW[key.dt.text] = ", ".join(value_list)

    for key in soup.find_all(attrs={"class":"cont-sec"}): #下部
        keyString = key.h3.text

        if key.table is not None: #授業計画・学生が身につける力
            tr_list = []
            #print([j.text for j in key.thead.tr.find_all("th")]) #ヘッダ
            for TR in key.tbody.find_all("tr"): #ボディ
                tr_list.append("[{}]".format(
                    ",".join(["\\'{}\\'".format(j.text) for j in TR.find_all("td")])
                     ))
            OCW[keyString] = "[{}]".format(",".join(tr_list))
            ''' リスト構造で保持する場合
            for TR in i.tbody.find_all("tr"): #ボディ
                print([j.text.split() for j in TR.find_all("td")])
            '''

        elif key.ul is not None: #関連する科目
            OCW[keyString] = ",".join([j.text for j in key.ul.find_all("li")])

        elif key.p is not None: #上記以外の、文章で書かれた項目
            OCW[keyString] = "\n".join(key.p.strings)

        else: #そのほか(例：動画)
            #法学（民事法）Ａ（http://www.ocw.titech.ac.jp/index.php?module=General&action=T0300&GakubuCD=7&KamokuCD=110100&LeftTab=graduate&KougiCD=201800860&Nendo=2018&lang=JA&vid=03）に「講義紹介動画」あり
            #暫定処置として、無視している
            pass


    #詳細ページに記載のなかった項目は適宜
    OCW["講義名"] = Lecture["name"]
    OCW["URL"] = Lecture["lecture_url"]
    if Gakuin["gakuin"][-2::] != "学院":
        OCW["学院"] = "その他"
    else:
        OCW["学院"] = Gakuin["gakuin"]

    return OCW

#講義情報をデータベースに格納する
def insertLecture(column,LectureData):
    #前処理(該当箇所が存在しないOCWページがあるので，それの対策)
    for k in column:
        if k not in LectureData:
            if k == "授業計画・課題": LectureData[k] = "[]"
            else: LectureData[k] = ""
    with connection.cursor() as cursor:
        sql = "INSERT INTO lecture ({}) ".format(",".join(map(lambda x:column[x],column)))
        sql += "VALUES ({}) ".format(",".join(map(lambda x:"\'{}\'".format(pymysql.escape_string(LectureData[x])),column)))
        sql += "ON DUPLICATE KEY UPDATE {};".format(",".join(["{} = VALUES({})".format(column[k],column[k]) for k in list(filter(lambda x:x!="科目コード",column))]))

        try:
            cursor.execute(sql)
        except pymysql.err.InternalError as e:
            error_code = e.args[0]
            if error_code != 1366:
                traceback.print_exc()
                sys.exit(1)
            # 変な文字コード（バイト列）があってエラーが出る際の対処（めったに起きないはず）
            non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), '')
            cursor.execute(sql.translate(non_bmp_map))

        print("\t\tUPDATE Lecture:",LectureData["講義名"])

#LectureとGakuinの結びつきデータベースの挿入操作
def insertLforG(column,code,gakuin):
    with connection.cursor() as cursor:
        sql = "INSERT IGNORE INTO LforG ({},{}) ".format(column["科目コード"],column["学院"])
        sql += "VALUES (\'{}\',\'{}\') ".format(code,gakuin)
        cursor.execute(sql)
        print("\t\tUPDATE LforG:",code,"-",gakuin)

#OCWスクレイピング実行
if __name__=='__main__':
    print("OCWデータのスクレイピングを始めます")
    Gakuins = [{'name': '理学院', 'url': 'http://www.ocw.titech.ac.jp//index.php?module=General&action=T0100&GakubuCD=1&lang=JA'},
                {'name': '工学院', 'url': 'http://www.ocw.titech.ac.jp//index.php?module=General&action=T0100&GakubuCD=2&lang=JA'},
                {'name': '物質理工学院', 'url': 'http://www.ocw.titech.ac.jp//index.php?module=General&action=T0100&GakubuCD=3&lang=JA'},
                {'name': '情報理工学院', 'url': 'http://www.ocw.titech.ac.jp//index.php?module=General&action=T0100&GakubuCD=4&lang=JA'},
                {'name': '生命理工学院', 'url': 'http://www.ocw.titech.ac.jp//index.php?module=General&action=T0100&GakubuCD=5&lang=JA'},
                {'name': '環境・社会理工学院', 'url': 'http://www.ocw.titech.ac.jp//index.php?module=General&action=T0100&GakubuCD=6&lang=JA'},
                {'name': '教養科目群', 'url': 'http://www.ocw.titech.ac.jp//index.php?module=General&action=T0200&GakubuCD=7&GakkaCD=370000&tab=2&focus=100&lang=JA'},
                {'name': '類科目', 'url': 'http://www.ocw.titech.ac.jp//index.php?module=General&action=T0100&GakubuCD=0&lang=JA'}]

    g_index = int(sys.argv[1])
    Gakuin = {"gakuin":Gakuins[g_index]["name"],"gakuin_url":Gakuins[g_index]["url"]}
    for Lecture in getLectures(Gakuin["gakuin"],Gakuin["gakuin_url"])[:Llimit]:
        OCWData = fetch_OCW(Gakuin,Lecture)
        insertLecture(column,OCWData)
        insertLforG(column,Lecture["code"],Gakuin["gakuin"])
        connection.commit()

    print("OCWデータのスクレイピングを完了しました")
