# OcwScraping
OCWをスクレピングするためのスクリプト

---

KEY設定およびそれに対するUPDATE処理により講義情報の更新に対応しています

(2018/10/13現在：PRIMARY KEYは科目コードです)

- python3.6 importOCW.py

  講義情報のテーブルにOCWからスクレイピングしてきた講義情報を格納していきます

  中断して続きからやるみたいな器用なことはできないので，main部いじってそれっぽくしてください(ごめん)

  全データ取得を前提とした記述になっていますが，limitでそれなりに限度をいじれます

  記述を変更するとしたらconnection，各Limit値，column，main部のいずれかのハズです

  (PRIMARY KEY設定を変更する場合，insertLecture()を少し変える必要があります)

- python3.6 recreateOCWTable.py

  (新規にテーブルを構築する場合はdropTable()を#でコメントアウトするよう願います)

  講義情報のテーブルを構築し直します

  打ち込んですぐ行われたらやばいので，質問フェーズを設けてます

  (yを入力すると再構築が行われ，それ以外で再構築を中止します)

  (PRIMARY KEY設定を変更する場合，createTable()を少し変える必要があります)

connectionとcolumnの情報はそれぞれ同一にしてください(recreateOCWTable.pyで設定し，importOCW.pyにコピーするのがオススメだと思います)

- scrapPage.ipynb

  IPython Notebook環境がある場合，こちらの方が見やすく，テストしやすいかと思います

  (IPython Notebook環境：Jupyter Notebook，Google Colabなど)
