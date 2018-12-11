import pymysql

'''
    recreateLforGTable.py

Lecture for Gakuin
いい名称出てこなかった
OCWTableを誤削除しないためと，
importLforGと同じく講義と学院の対応づけだけ再構築したい時用
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

#LforGのTABLEをつくる　1回しかしなそう
def createLforGtable(column):
    with connection.cursor() as cursor:
        sub_column = []
        KEY_LENGTH = 20
        sub_column.append("{} NVARCHAR({}) NOT NULL".format(column["科目コード"],KEY_LENGTH))
        sub_column.append("{} NVARCHAR({}) NOT NULL".format(column["学院"],KEY_LENGTH))
        sub_column.append("PRIMARY KEY({},{})".format(column["科目コード"],column["学院"]))
        sql = "CREATE TABLE LforG({});".format(",".join(sub_column))
        #print(sql)
        cursor.execute(sql)

#LforGのTABLEを削除する
def dropLforGtable():
    with connection.cursor() as cursor:
        sql = "DROP TABLE LforG;"
        cursor.execute(sql)

if __name__=='__main__':
    print("本当にOCW LforG Tableを削除しますか？(する：y，しない：otherwise)")
    if input()=="y":
        dropLforGtable()
        createLforGtable(column)
        connection.commit()
        print("LforG Tableを再構築しました")
    else:
        print("LforG Tableの再構築を中止しました")
