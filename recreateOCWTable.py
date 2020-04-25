import pymysql
from settings_secret import *

'''
    recreateOCWTable.py

講義情報のテーブルを構築し直します
打ち込んですぐ行われたらやばいので，質問フェーズを設けてます
(yを入力すると再構築が行われ，それ以外で再構築を中止します)
(PRIMARY KEY設定を変更する場合，createTable()を少し変える必要があります)

connectionとcolumnの情報はimportOCW.pyとおなじにしてね！
'''

connection = pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWORD,
                             db=DB_NAME,
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
          "単位数":"Credit",
          "開講クォーター":"Quarter", # キー
          "使用言語":"Language",
          # シラバス側 #
          "授業計画・課題":"LecturePlan",
          "成績評価の基準及び方法":"AssessStyle",
          "履修の条件(知識・技能・履修済科目等)":"CourseCond",
          # 検索用 #
          "学院":"Gakuin",
          # その他 #
          "取得日":"LastUpdate"}

#TABLEをつくる　データベースの構造が完全になったら不要
def createTable(column):
    with connection.cursor() as cursor:
        KEY_COLUMN1 = "科目コード"
        KEY_LENGTH1 = 10
        KEY_COLUMN2 = "開講クォーター"

        sub_column = []
        for k in column:
            if column[k] == KEY_COLUMN1 or column[k] == KEY_COLUMN2:
                #key処理そのいち
                sub_column.append(column[k]+" TEXT NOT NULL")
            else:
                sub_column.append(column[k]+" TEXT")

        sub_column.append("PRIMARY KEY({}({}), {})".format(column[KEY_COLUMN1],KEY_LENGTH1,column[KEY_COLUMN2])) #key処理そのに
        sql = "CREATE TABLE lecture({});".format(",".join(sub_column))
        #print(sql)
        cursor.execute(sql)

#TABLEを削除する
def dropTable():
    with connection.cursor() as cursor:
        sql = "DROP TABLE IF EXISTS lecture;"
        cursor.execute(sql)

#LforGのTABLEをつくる　1回しかしなそう
def createLforGtable(column):
    with connection.cursor() as cursor:
        sub_column = []
        KEY_LENGTH = 10
        sub_column.append("{} NVARCHAR({}) NOT NULL".format(column["科目コード"],KEY_LENGTH))
        sub_column.append("{} NVARCHAR({}) NOT NULL".format(column["開講クォーター"],KEY_LENGTH))
        sub_column.append("{} NVARCHAR({}) NOT NULL".format(column["学院"],KEY_LENGTH))
        sub_column.append("PRIMARY KEY({},{},{})".format(column["科目コード"],column["開講クォーター"],column["学院"]))
        sql = "CREATE TABLE LforG({});".format(",".join(sub_column))
        #print(sql)
        cursor.execute(sql)

#LforGのTABLEを削除する
def dropLforGtable():
    with connection.cursor() as cursor:
        sql = "DROP TABLE IF EXISTS LforG;"
        cursor.execute(sql)

if __name__=='__main__':
    print("本当にOCW Tableを再構築しますか？(する：y，しない：otherwise)")
    if input()=="y":
        #新規作成する場合はdrop2つともコメントアウト
        dropTable()
        dropLforGtable()
        createTable(column)
        createLforGtable(column)
        connection.commit()
        print("OCW Tableを再構築しました")
    else:
        print("OCW Tableの再構築を中止しました")
