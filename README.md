"# syuzai_map_django_site" 


## venv環境構築
python -m venv venv
source venv/bin/activate
### activate
venv\Scripts\activate

### deactivate
deactivate

### パッケージのインストール
pip install -r requirements.txt

### 参考リンク
https://qiita.com/futakuchi0117/items/6030458a96f62cb64d37

## GithubのISSUEの作り方
https://colorfree-map.com/git-issue-myself

### ブランチを切る
#### わかりやすいブランチ名（英語で）と#27のように先ほどの数字を入れ、新しいブランチを作る
$ git checkout -b back-btn#27

#### 今のmasterの状況を新しく作ったブランチにpushして同期させる
$ git push origin back-btn#27

#### ステージする
$ git add .

#### コミットする。このとき#番号を忘れずに！！
$ git commit -m “back-btn#27”

#### プッシュする。先ほどのブランチ名に
$ git push origin back-btn#27

#### ブランチをメインに切り替える
$ git checkout main

#### マスターにマージされた内容を反映させるプル
$ git pull