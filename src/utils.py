#WINDOWS用
from selenium import webdriver
import time
import os
import pandas as pd
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
import urllib
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import re
import csv
import codecs
import requests
import urllib.request as req
import glob
import mysql
import mysql.connector
import sys
import traceback

import json
import time
import datetime
from datetime import datetime, date, timedelta
import numpy as np
import gspread

from PIL import Image, ImageDraw, ImageFont
import datetime
import shutil
import pymysql

from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc import Client, WordPressPost, methods

import requests
import json
import base64
from wordpress_xmlrpc.methods import media
#from oauth2client.service_account import ServiceAccountCredentials
import gspread
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc import Client, WordPressPost
from dateutil.relativedelta import relativedelta
import os
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import Select
import urllib
from bs4 import BeautifulSoup
import re
import csv
import codecs
import requests
import urllib.request as req
import glob
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import datetime
import os
from selenium.webdriver.common.by import By
from wordpress_xmlrpc import Client, WordPressPost, methods
from urllib.parse import urljoin
import mysql
import mysql.connector
import urllib.request


from dotenv import load_dotenv
load_dotenv(".env")
print('読み込み完了')

class UtilsTwitterClass():

    def __init__(self):
        #日付関連処理
        today = datetime.date.today()
        tomorrow :datetime = datetime.date.today() + datetime.timedelta(days=1)
        yesterday :datetime = datetime.date.today() - datetime.timedelta(days=1)
        week_list = [ '(日)','(月)', '(火)', '(水)', '(木)', '(金)', '(土)','(日)']
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_date_string_jp:str = tomorrow.strftime('%m').lstrip('0') + '/' + tomorrow.strftime('%d').lstrip('0') + week_list[tomorrow.isoweekday()]
        tomorrow_date_string_sql:str = tomorrow.strftime('%Y-%m-%d')
        yesterday_date_string:str =  yesterday.strftime('%m').lstrip('0') + '/' +  yesterday.strftime('%d').lstrip('0') + week_list[ yesterday.isoweekday()]

        self.tomorrow_8numbers_string:str = tomorrow.strftime('%Y%m%d')
        self.tomorrow_date_stinrg_jp:str = tomorrow_date_string_jp
        self.tomorrow_date_string_sql = tomorrow_date_string_sql
        self.yesterday = yesterday
        self.tomorrow = tomorrow
        self.yesterday_date_string = yesterday_date_string
        self.id = os.getenv('TWITTER_ID')
        self.pw = os.getenv('TWITTER_PW')
        self.tweet_text = ''
        self.image_path_list = []
        self.main_tweet_text = ''
        #ディレクトリ関係
        self.project_dir_path = os.path.join(os.path.expanduser(r'~'),"Desktop","syuzai_map_django_site")
        self.image_dir_path = os.path.join(self.project_dir_path,"image")
        self.tweet_footer_text = '\n\n#XXXX '+ yesterday.strftime('%Y%m%d') + '\n\n'
        #os.path.join(self.image_dir_path," ") これ/imageの基本パス
        self.created_image_dir_path = os.path.join(self.image_dir_path,"image")
        self.servise_account_json_path = os.path.join(self.project_dir_path,"config", "twitteranalytics-jsonsercretkey.json")

    def add_target_date (self, taget_day_number:int):
        week_list = [ '(日)','(月)', '(火)', '(水)', '(木)', '(金)', '(土)','(日)']
        target_date:datetime = datetime.date.today() + datetime.timedelta(days=taget_day_number)
        #datetime(2023,3,3)
        self.target_date:datetime = datetime.date.today() + datetime.timedelta(days=taget_day_number)
        #3月3日(火)
        self.target_date_string_jp:str = target_date.strftime('%m').lstrip('0') + '月' + target_date.strftime('%d').lstrip('0') + '日'  +week_list[target_date.isoweekday()]
        #2023-03-03
        self.target_date_string_sql:str = target_date.strftime('%Y-%m-%d')

    def twitter_login(self):
        options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-gpu")
        # options.add_argument("--disable-features=NetworkService")
        # options.add_argument("--window-size=1920x1080")
        # options.add_argument("--disable-features=VizDisplayCompositor")
        browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        browser.get("https://twitter.com/home")
        browser.implicitly_wait(10)

        browser.maximize_window()
        browser.implicitly_wait(10)

        #ログイン処理~定位置画面までの処理
        element = browser.switch_to.window(browser.window_handles[-1])
        browser.implicitly_wait(10)
        #新規ウインドウをアクティブにする

        element = browser.find_element(By.XPATH, '//*[@autocomplete="username"]')
        time.sleep(1)
        element.send_keys(self.id)
        time.sleep(1)
        #IDを入力

        element.find_element(By.XPATH, "//*[text()=\"次へ\"]").click()
        time.sleep(1)

        #pwを入力
        element = browser.find_element(By.XPATH, '//*[@name="password"]')
        time.sleep(1)
        element.send_keys(self.pw)
        time.sleep(1)

        element = browser.find_element(By.XPATH, "//*[text()=\"ログイン\"]")
        element.click()
        time.sleep(1)
        self.browser = browser
        return self.browser

    def post_tweet(self,kotei_tweet_option=False):
                # ツイートボタンを押す
        browser = self.browser
        browser.get("https://twitter.com/home")
        time.sleep(2)
        element = browser.find_element(By.XPATH, '/html/body/div/div/div/div[2]/header/div/div/div/div[1]/div[3]/a/div')
        element.click()
        time.sleep(2)

        element_text = browser.find_element(By.CLASS_NAME, "notranslate")
        element_text.click()
        element_text.send_keys(self.tweet_text)

        time.sleep(2)
        browser.implicitly_wait(10)

        element = browser.find_element(By.XPATH, '//*[@data-testid="fileInput"]')
        time.sleep(1)
        pwd = os.getcwd()
        print('pwd',os.getcwd())
        for image_path in self.image_path_list:
            abusolute_image_path = os.path.join(pwd,image_path)
            element.send_keys(abusolute_image_path)
            time.sleep(1) 

        #browser.execute_script("arguments[0].click();", element)
        browser.execute_script("window.scrollTo(0, 600);")
        time.sleep(5) 

        #element = browser.switch_to.window(browser.window_handles[-1])
        tweet_button = browser.find_element(By.XPATH, '//*[@data-testid="tweetButton"]')
        tweet_button.click()
        time.sleep(3) 

        browser.implicitly_wait(10)
        print('終わり')

        browser.get("https://twitter.com/home")
        browser.implicitly_wait(10)
        print('終わり')

        if kotei_tweet_option is True:
            browser.get(f"https://twitter.com/{self.id}")
            time.sleep(3)

            #element = browser.switch_to.window(browser.window_handles[-1])
            browser.execute_script("window.scrollTo(0, 600);")
            time.sleep(3)

            element = browser.find_elements_by_xpath('//*[@aria-label="もっと見る"]')[1]

            element.find_elements_by_xpath('div/div')[0].find_elements_by_css_selector("*")[1].click()
            time.sleep(3)

            element.find_element(By.XPATH, "//*[text()=\"プロフィールに固定する\"]").click()
            time.sleep(3)

            element.find_element(By.XPATH, "//*[text()=\"固定する\"]").click()
            time.sleep(3)

        else:
            pass

    def reply_tweet_1(self,text):
        if len(self.tweet_text) != 0:
            browser = self.browser
            browser.get(f"https://twitter.com/{self.id}")
            browser.execute_script("window.scrollTo(0, 600);")
            time.sleep(2)

            element = browser.find_elements(By.XPATH,'//*[@data-testid="tweet"]')[1]
            element.click()
            time.sleep(2)

            element = browser.find_elements(By.XPATH,'//*[@aria-label="返信"]')[0]
            element.click()
            time.sleep(2)


            element = browser.find_elements(By.XPATH,'//*[@aria-label="テキストをツイート"]')[0]
            element.click()
            time.sleep(2)
            element.send_keys(text)
            time.sleep(2)


            time.sleep(2)
            browser.implicitly_wait(10)

            element = browser.find_element(By.XPATH, '//*[@data-testid="fileInput"]')
            time.sleep(1)

            #element.send_keys(self.image_path_list[0])

            browser.execute_script("arguments[0].click();", element)
            browser.execute_script("window.scrollTo(0, 2000);")
            time.sleep(5) 

            #element = browser.switch_to.window(browser.window_handles[-1])

            tweet_button = browser.find_element(By.XPATH, '//*[@data-testid="tweetButton"]')
            tweet_button.click()
            time.sleep(3) 

    def change_plus_convert(x):
        x = int(x)
        if x >= 0 :
            x = '-' + str(x).replace('+','')
        else:
            x = '+' + str(x).replace('-','')
        #print(x)
        return x


    def generate_database_query_df(self,tenpo_name,baitai_name,date):
        import pymysql
        global zendai_ichiran_df
        conn = pymysql.connect(host='XXXX',
                                    user='XXXX',
                                    password='XXXXX',
                                    db='XXXXX',
                                    port=0000)
        print(conn)
        
        # yesterday = datetime.today() + timedelta(days=-1)
        

        try:
            self.baitai_name_jpn = tenpo_name.split('\n')[2]
            tenpo_name = tenpo_name.split('\n')[1].replace('・','')
        except:
            pass

        
        self.tenpo_name_plus_syuzai_name = tenpo_name

        tenpo_name = tenpo_name.split('(')[0]
        self.tenpo_name = tenpo_name
        # SQLを実行する
        #SELECT 引っ張ってきたい列名　FROM　テーブル名 WHERE 条件列 = 'ジャグ（文字列の完全一致）' " 
        column_name = ['都道府県', '店舗名','日付', 'レート', '機種名', '台番号', '総回転数', 'BB', 'RB', 'ART', '差枚', 'BB確率',
            'RB確率', 'ART確率', '合成確率', '末尾','id']
        print(column_name)
        with conn.cursor() as cursor:
            sql = f"SELECT * FROM anaslo_table WHERE 店舗名 = '{tenpo_name}' AND 日付 = '{date}' " #AND 機種名 = '主役は銭形3'
            cursor.execute(sql)
            # # Select結果を取り出す
            #results = cursor.fetchall()
        print(sql)
        zendai_ichiran_df = pd.DataFrame(data=cursor.fetchall(), index = None, columns = column_name)
        self.zendai_ichiran_df = zendai_ichiran_df

        return zendai_ichiran_df


    def post_line(message:str) -> None:
        url = "https://notify-api.line.me/api/notify"
        token = os.environ['LINE_TOKEN']
        headers = {"Authorization" : "Bearer "+ token}
        payload = {"message" :  message}
        #imagesフォルダの中のgazo.jpg
        #print('image_path',image_path)
        #files = {"imageFile":open(image_path,'rb')}
        post = requests.post(url ,headers = headers ,params=payload) 


    def convert_string(x):
        x = x.replace('来店+取材B', '+スロパチ取材').replace('応援地区(ディレクター有)', '').replace('応援地区(ディレクター無)', '').replace('取材C', 'スロパチ潜入取材').replace('+結-MUSUBI-取材', '+スロパチ取材"結"').replace('+取材B', '+スロパチ取材').replace('潜入取材メガテン', 'メガテン').replace('襲来', '').replace('(30％以上)', '').replace('WEB広告', 'スロパチ広告').replace('+トレジャー取材', '+トレジャー').replace('あつまる+スロパチ取材', 'あつまる').replace('潜入光', '光').replace('潜入取材光', '光').replace('取材光', '光').replace('かたまる+スロパチ取材"結"', 'かたまる').replace('光(25％以上30％未満)', '光').replace('スロパチ潜入取材', '潜入取材').replace('あつまるのみ', 'あつまる').replace('応援地区', '').replace('ホールサーチマン金枠', '金枠').replace('ホールサーチマン赤枠', '赤枠').replace('かたまる×スロパチ取材結', 'かたまる').replace('本店館', '本館').replace('ホールサーチマンレインボー枠', 'レインボー枠').replace(' ', '').replace('　', '')
        return x


    def tenpo_convert_string(x):
        x = x.replace('相模原ピーくんステージ', 'ピーくんステージ').replace('アミューズメントコミュニティ ', '').replace('店', '').replace('新!', '').replace('本', '本店').replace('新！', '')
        return x
    
    

class Blog():
    def __init__(self):
        WORDPRESS_ID = os.environ['WORDPRESS_ID']
        WORDPRESS_PW = os.environ['WORDPRESS_PW']
        WORDPRESS_URL = os.environ['WORDPRESS_URL']
        self.error_pledge_name_list = []
        self.wp = Client(WORDPRESS_URL, WORDPRESS_ID, WORDPRESS_PW)
        
    def check_url(self,url,pledge_name):
        flag = True
        try:
            f = urllib.request.urlopen(url)
            #print('OK:', url)
            f.close()
        except urllib.request.HTTPError:
            print('Not found:', pledge_name,url)
            flag = False

        return flag

    def add_target_date (self, target_day_number:int):
        week_list = [ '(日)','(月)', '(火)', '(水)', '(木)', '(金)', '(土)','(日)']
        target_date:datetime = datetime.date.today() + datetime.timedelta(days=target_day_number)
        #datetime(2023,3,3)
        self.target_date:datetime = datetime.date.today() + datetime.timedelta(days=target_day_number)
        #3月3日(火)
        self.target_date_string_jp:str = target_date.strftime('%m').lstrip('0') + '月' + target_date.strftime('%d').lstrip('0') + '日'  +week_list[target_date.isoweekday()]
        #2023-03-03
        self.target_date_string_sql:str = target_date.strftime('%Y-%m-%d')
        print(f'インスタンに日付:{self.target_date_string_jp}など三つの変数が追加されました')
    
    def upload_image(self,in_image_file_name, out_image_file_name):
        if os.path.exists(in_image_file_name):
            with open(in_image_file_name, 'rb') as f:
                binary = f.read()

            data = {
                "name": out_image_file_name,
                "type": 'image/png',
                "overwrite": True,
                "bits": binary
            }

            media_id = self.wp.call(media.UploadFile(data))['id']
            print(in_image_file_name.split('/')
                [-1], 'Upload Success : id=%s' % media_id)
            return media_id
        else:
            print(in_image_file_name.split('/')[-1], 'NO IMAGE!!')

    def post_line(self,message):
        url = "https://notify-api.line.me/api/notify"
        token = os.environ['LINE_TOKEN']
        headers = {"Authorization" : "Bearer "+ token}
        payload = {"message" :  message}
        #imagesフォルダの中のgazo.jpg
        #print('image_path',image_path)
        #files = {"imageFile":open(image_path,'rb')}
        post = requests.post(url ,headers = headers ,params=payload) 


    def get_post_list(self) -> list[WordPressPost]:
        '''投稿一覧を取得する関数
        一回で500記事まで取得できる'''
        post_list:list[WordPressPost] = self.wp.call(methods.posts.GetPosts({"number": 800, "offset":0}))
        self.post_list = post_list
        return self.post_list

    def generate_thumbnail(self) :
        image_path = r'image\image_source\千葉.jpg'  # mac
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        write_image_context = f'''{self.target_date_string_jp }\n{self.prefecture_name}\n取材予定まとめ'''
        font_path = r"font/LightNovelPOPv2.otf"
        font = ImageFont.truetype(font_path, size=240)
        draw.multiline_text((130, 20), write_image_context, fill=(255, 255, 255),align='center',font=font, spacing=50, stroke_width=5, stroke_fill=(55, 55, 55))
        thumbnail_image_path = fr'image\temp_image\thumbnail_{self.target_date}_{self.prefecture_name}.jpg'
        image.save(thumbnail_image_path)
        self.thumbnail_image_path = thumbnail_image_path


    def post_blog(self,main_text):
        title = f"【{self.prefecture_name}】{self.target_date_string_jp} パチンコスロットイベント取材まとめ"
        # Blog Content (html)
        body = main_text
        # publish or draft
        status = 'publish' # "publish"　or# 'draft'

        # Category keyword
        cat1 = '取材予定まとめ'
        cat2 = ''
        cat3 = ''

        # Tag keyword
        tag1 = f'{self.prefecture_name}'
        #tag2 = f'{self.target_date}'

        slug = f"pledge_report_{self.target_date}_{self.prefecture_name}"

        # Post
        post = WordPressPost()
        post.title = title
        post.content = body
        post.post_status = status
        post.terms_names = {
            "category": [cat1],
            "post_tag": [tag1],
        }
        post.slug = slug

        #サムネイル関連
        output_thumbnail_path = f'thumbnail_{self.target_date}_{self.prefecture_name}.jpg'
        media_id = self.upload_image(self.thumbnail_image_path, output_thumbnail_path)
        post.thumbnail = media_id

        #Post Time
        #post.date = datetime.datetime.now()

        self.wp.call(NewPost(post))
        print('記事書き込み完了')
        # except Exception as e:
    #     post_line(f'{tomorrow}分ブログ投稿失敗\n{e}')
    
    def wp_update_post(self,content_id:int,content_text:str) -> dict:
        
        # URL, User, Password設定
        WP_URL: str = os.getenv('WP_URL')
        WP_USER: str = os.getenv('WP_USER')
        WP_API_PASSWORD: str = os.getenv('REST_API_PW')
        API_URL = f"{WP_URL}/wp-json/wp/v2/"
        url = f'{WP_URL}/wp-json/wp/v2/posts/{content_id}'
        credentials = WP_USER + ':' + WP_API_PASSWORD
        token = base64.b64encode(credentials.encode())
        headers = {'Authorization': 'Basic ' + token.decode('utf-8')}

        post = {f'content': content_text,
                'status': 'publish'}
        res = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{content_id}", headers=headers, json=post)
        if res.ok:
            print("投稿の更新 成功 code:{res.status_code}")
            return json.loads(res.text)
        else:
            print(f"投稿の更新 失敗 code:{res.status_code} reason:{res.reason} msg:{res.text}")
            return {}

    def wp_tag_add(self,tagname:str) -> int:
        
        WP_URL: str = os.getenv('WP_URL')
        WP_USER: str = os.getenv('WP_USER')
        WP_API_PASSWORD: str = os.getenv('REST_API_PW')
        API_URL = f"{WP_URL}/wp-json/wp/v2/"
        TAG_URL = urljoin(WP_URL, '/wp-json/wp/v2/tags/')
        r = ""
        post = {
            'name': tagname,
        }
        res = requests.post(
            TAG_URL ,
            json=post,
            auth=(WP_USER, WP_API_PASSWORD),
            )
        data = json.loads(res.text)
        if 'code' in data:
            if data['code'] == "term_exists":
                r = data['data']['term_id']
                print(r)
        else:
            r = data['id']
            print(r)
        return r
    
    def create_main_text(self,save_main_image_path_list,merged_syuzai_pledge_df):
        main_text = f'''
[st-kaiwa1]【{self.prefecture_name}】{self.target_date_string_jp }　パチンコホールイベント取材まとめ記事です。

イベントの公約に基づき、高設定が投入される可能性が高いと予想されるホールを中心に公約内容も一緒にわかりやすく明日のイベントのある店舗を紹介しています。

毎日更新されますので是非、ブックマークお願いします。[/st-kaiwa1]
<h3>更新時間:{datetime.datetime.now().strftime("%m月%d日%H時%m分")}</h3>
<h2>{self.prefecture_name}  パチンコ・スロット イベント 取材まとめ・オススメ店舗順一覧画像</h2>
'''
        print(main_text)
        image_url_head_text:str = f'http://slotana777.com/wp-content/uploads/{datetime.datetime.now().strftime("%Y")}/{datetime.datetime.now().strftime("%m")}/'
        for input_image_path in save_main_image_path_list:
            output_path = input_image_path.replace('image\\temp_image\\','')
            output_path = output_path.split('.')[0] + f'_updatetime_' + datetime.datetime.now().strftime('%m-%d') +'.' +output_path.split('.')[1]
            print(output_path)
            self.upload_image(input_image_path, output_path)
            main_text  += f'''\n<a href="{image_url_head_text}{output_path}">\n<img src="{image_url_head_text}{output_path}" alt="{self.prefecture_name}_{self.target_date_string_sql}_パチンコ・パチスロ_イベント" class="alignnone size-full " /></a>'''

        html_table_df = merged_syuzai_pledge_df[['店舗名','取材名','媒体名','公約内容']]
        html_table_df['イベント日'] = self.target_date_string_jp
        html_table_df = html_table_df[['店舗名','取材名','媒体名','公約内容']]
        print(html_table_df.to_html(index=False))

        main_text += f'<h2>{self.prefecture_name} {self.target_date_string_jp} パチンコ・スロット イベント 取材まとめ・オススメ店舗順一覧</h2>'
        main_text += '\n[su_spoiler title="店舗別一覧を表示する※タップで全取材一覧が見れます" style="fancy" icon="chevron-circle" anchor="Hello"]\n' + html_table_df.to_html(index=False) + '[/su_spoiler]'
        self.main_text = main_text
        return self.main_text

    def generate_by_pledge_text(self,merged_syuzai_pledge_df,scraping):
        input_by_pledge_text = f'\n<h2>{self.prefecture_name} {self.target_date_string_jp} 媒体別取材まとめ</h2>\n'
        pledge_name_list:list[str] = list(merged_syuzai_pledge_df['媒体名'].unique())
        for pledge_name in ['フリー','その他','未調査']:
            try:
                pledge_name_list.remove(pledge_name)
                pledge_name_list.append(pledge_name)
            except:
                pass
        error_pledge_name_list = []
        for pledge_name in pledge_name_list:
            extract_pledge_name_df = merged_syuzai_pledge_df[merged_syuzai_pledge_df['媒体名'] == pledge_name]
            encoced_plefge_name = urllib.parse.quote(pledge_name)
            header_url:str = f'http://slotana777.com/wp-content/uploads/2023/04/{encoced_plefge_name}.jpg'
            if self.check_url(header_url,pledge_name):
                input_by_pledge_text += f'<img src="http://slotana777.com/wp-content/uploads/2023/04/{pledge_name}.jpg" alt="{pledge_name}" width="1000" height="400" class="size-full " />\n'
            else:
                h2_banner_text:str =f'''<div class="box-alert box-alert-info">
        <i class="fas fa-exclamation-circle fa-4x"></i>
        <div class="alert-message">
            <div class="alert-title">{pledge_name}</div>
            <p>{scraping.target_date_string_jp}  {scraping.prefecture_name}</p>
        </div></div>'''
                #print(h2_banner_text)
                input_by_pledge_text += '\n' + h2_banner_text
                self.error_pledge_name_list.append(pledge_name)
            #display(extract_pledge_name_df )
            #break
            rank_replace_dict:dict[str] = {'S':'<h4 class="rankh4 rankno-1">','A':'<h4 class="rankh4 rankno-2">','B':'<h4 class="rankh4 rankno-3">','C':'<h4 class="rankh4 rankno-4">','・':'<h4 class="rankh4 rankno-4">'}
            for rank in ['S','A','B','C','・']:
                extract_syuzai_name_df  = extract_pledge_name_df[extract_pledge_name_df['取材ランク'] == rank]
                #display(extract_syuzai_name_df)
                for syuzai_name in extract_syuzai_name_df['取材名'].unique():
                    input_by_pledge_text += '<div class="redbox"><h5><span class="oomozi"><strong>' + syuzai_name + '</strong></span></h5>\n'
                    extract_parlar_name_df  = extract_pledge_name_df[extract_pledge_name_df['取材名'] == syuzai_name]
                    pre_pledge_name = ''
                    for i,row in extract_parlar_name_df.iterrows():
                        if pre_pledge_name != row['取材名']:
                            input_by_pledge_text += f'\n<span class="hatenamark2 on-color">公約:{row["公約内容"]}</span>'
                            input_by_pledge_text += f'\n{rank_replace_dict[rank]} {row["店舗名"]}</strong></span></h4>'
                        else:
                            input_by_pledge_text += f'\n{rank_replace_dict[rank]} {row["店舗名"]}</strong></span></h4>'
                        pre_pledge_name = row['取材名']
                    input_by_pledge_text +='</div>'  
            # if len(extract_pledge_name_df ) != 0:
            #     # print('\n■',baitai,sep='')
            #     winput_by_pledge_text += '<h3>' + string_date_only + ' ' + todoufuken_kanji + ' スロット ' + baitai + '</h3>' + f'\n<img src="http://slotana777.com/wp-content/uploads/2021/04/{error_baitai}.jpg" alt="{error_baitai} タイトル画像" width="1000" height="400" class="alignnone size-full " />\n'
            # else:
            #     pass
            #break
        print(input_by_pledge_text)
        self.input_by_pledge_text = input_by_pledge_text
        return self.input_by_pledge_text

class PledgeScraping():
    def add_target_date(self, target_day_number:int):
        week_list = [ '(日)','(月)', '(火)', '(水)', '(木)', '(金)', '(土)','(日)']
        target_date:datetime = datetime.date.today() + datetime.timedelta(days=target_day_number)
        #datetime(2023,3,3)
        self.target_date:datetime = datetime.date.today() + datetime.timedelta(days=target_day_number)
        #3月3日(火)
        self.target_date_string_jp:str = target_date.strftime('%m').lstrip('0') + '月' + target_date.strftime('%d').lstrip('0') + '日'  +week_list[target_date.isoweekday()]
        #2023-03-03
        self.target_date_string_sql:str = target_date.strftime('%Y-%m-%d')
        print(f'インスタンに日付:{self.target_date_string_jp}など三つの変数が追加されました')

    def login_scraping_site(self,area_name):
        global browser
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)#ChromeDriverManager().install()
        browser.implicitly_wait(10)
        url_login = f"https://{os.getenv('SCRAPING_SYUZAI_DOMAIN')}/login_form_mail"
        #admageを開く
        browser.get(url_login)
        browser.implicitly_wait(10)
        # id
        element = browser.find_element(By.NAME,"id")
        element.click()
        element.clear()
        browser.implicitly_wait(10)
        element.send_keys(os.getenv('REPORT_SITE_ID'))
        # pw
        element = browser.find_element(By.NAME,"pass")
        element.click()
        element.clear()
        browser.implicitly_wait(10)
        element.send_keys(os.getenv('REPORT_SITE_PW'))
        browser.implicitly_wait(10)
        element = browser.find_element(By.CLASS_NAME,"box_hole_view_report_input")
        element.click()
        browser.implicitly_wait(10)
        url = f"https://{os.getenv('SCRAPING_SYUZAI_DOMAIN')}/select_area"
        browser.get(url)
        browser.implicitly_wait(10)
        url = f"https://{os.getenv('SCRAPING_SYUZAI_DOMAIN')}/?area={area_name}"
        browser.get(url)
        browser.implicitly_wait(10)
        self.browser =browser
        return self.browser

#エリアの都道府県の名前と対応番号を取得

    def get_prefecture_name_and_number_dict(self):
        prefectures_box_elements = browser.find_element(By.CLASS_NAME,"one_sp_block")
        prefectures_elements:list = prefectures_box_elements.find_elements(By.CLASS_NAME,"mgn_serch_list_bottom")
        prefecture_name_and_number_dict:dict[str:str] = {}

        for element in prefectures_elements:
            prefecture_name:str = element.find_element(By.CLASS_NAME,"side_bar_L_O").text
            #print(prefecture_name)
            link_url:str = element.find_element(By.TAG_NAME,'a').get_attribute('href')
            prefecture_number:int = link_url.split('ken=')[-1]
            #print(prefecture_number)
            prefecture_name_and_number_dict[prefecture_name] = prefecture_number

        self.prefecture_name_and_number_dict = prefecture_name_and_number_dict
        return self.prefecture_name_and_number_dict
    
    def read_target_date_pledge_df(self,prefecture_name:str):
        browser = self.browser
        self.prefecture_name = prefecture_name
        furture_syuzai_list_df = pd.DataFrame(index=[], columns=['都道府県','イベント日','店舗名','取材名','取材ランク'])
        prefecture_number:int = int(self.prefecture_name_and_number_dict[prefecture_name])
        url = f"https://{os.getenv('SCRAPING_SYUZAI_DOMAIN')}/osusume_list?ken={prefecture_number}&ymd={self.target_date_string_sql}"
        browser.get(url)
        page_number = 0
        while True:
            page_number += 1
            browser.implicitly_wait(10)
            kiji_element_box = browser.find_element(By.CLASS_NAME,"osusume_list_container")
            kiji_elements_list:list = kiji_element_box.find_elements(By.CLASS_NAME,"osbox")

            for i,syuzai_record_element in enumerate(kiji_elements_list):
                if 'プレミアム会員登録' == browser.find_element(By.CLASS_NAME,"menu_child").text:
                    browser = self.login_scraping_site('chubu')
                    url = f"https://{os.getenv('SCRAPING_SYUZAI_DOMAIN')}/osusume_list?ken={prefecture_number}&ymd={self.target_date_string_sql}"
                    browser.get(url)
                    browser.implicitly_wait(10)
                else:
                    pass
                #print(syuzai_record_element.text)
                syuzai_record_element_list = syuzai_record_element.find_elements(By.CLASS_NAME,"list_event_name")
                browser.implicitly_wait(1)
                #print(syuzai_record_element_list)
                if len(syuzai_record_element_list) == 0:
                    continue
                tenpo_name = syuzai_record_element.find_element(By.CLASS_NAME,"oslh2").text
                for syuzai_name_element in syuzai_record_element_list:
                    #print(syuzai_name_element.text)
                    syuzai_rank = syuzai_name_element.find_element(By.CLASS_NAME,"list_event_name_rank").text
                    schedule_name = syuzai_name_element.find_element(By.CLASS_NAME,"list_event_name_li").text
                    #print(tenpo_name,syuzai_rank,schedule_name)
                    record = pd.Series([prefecture_name,self.target_date_string_sql, tenpo_name,schedule_name,syuzai_rank], index=furture_syuzai_list_df.columns)
                    record_df =  pd.DataFrame(record)
                    furture_syuzai_list_df = pd.concat([furture_syuzai_list_df,record_df.T])
            if browser.find_element(By.CLASS_NAME,"navi_1_next").text == '次へ':
                browser.find_element(By.CLASS_NAME,"navi_1_next").click()
            else:
                break
            if page_number >= 3:
                break
            
        self.furture_syuzai_list_df = furture_syuzai_list_df
        return self.furture_syuzai_list_df

    def read_convert_parlar_name_df(self):
        cnx = mysql.connector.connect(
                        user = os.getenv('DB_USER_NAME'),
                        password=os.getenv('DB_PASSWORD'), 
                        host=os.getenv('DB_HOST'), 
                        port='3306',
                        database=os.getenv('DB_NAME'))
        cursor = cnx.cursor()
        sql = f"""SELECT * FROM pledge"""
        print(sql)
        cursor.execute(sql)
        #cols = [col[0] for col in cursorsor.description]
        convert_parlar_name_df = pd.DataFrame(cursor.fetchall(),columns = ['id','取材名','媒体名','公約内容','取得時間'])
        self.convert_parlar_name_df = convert_parlar_name_df
        return self.convert_parlar_name_df
    
    def generate_merged_syuzai_pledge_df(self):
        merged_syuzai_pledge_df = pd.merge(self.furture_syuzai_list_df,self.convert_parlar_name_df,how='left',on='取材名')
        merged_syuzai_pledge_df = merged_syuzai_pledge_df.fillna('未調査')
        merged_syuzai_pledge_df = merged_syuzai_pledge_df.replace({'': '未調査'})
        merged_syuzai_pledge_df = merged_syuzai_pledge_df[~merged_syuzai_pledge_df['取材名'].str.contains('ナビ子')]
        merged_syuzai_pledge_df = merged_syuzai_pledge_df[~merged_syuzai_pledge_df['媒体名'].str.contains('ホールナビ')]
        self.merged_syuzai_pledge_df = merged_syuzai_pledge_df
        return self.merged_syuzai_pledge_df
    
    def recommend_image(self,write_image_context, length,read_image_path,save_image_jpg):
        image = Image.open(read_image_path)
        draw = ImageDraw.Draw(image)
        # フォントを指定
        font_path = r"font\LightNovelPOPv2.otf"
        font = ImageFont.truetype(font_path, size=40)

        # 文字を描く
        # 最初の(0,0)は文字の描画を開f始する座標位置です　もちろん、(10,10)などでもOK
        # fillはRGBで文字の色を決めています
        draw.multiline_text((55, 40), write_image_context, fill=(255, 255, 255), font=font, spacing=10, stroke_width=5, stroke_fill=(55, 55, 55))

        # 画像を保存する
        image.save(save_image_jpg)
        print('length', length)
        length_croped = 110 + length * 66  # 500
        im = Image.open(save_image_jpg)
        im_crop = im.crop((0, 0, 1000, length_croped))
        im_crop.save(save_image_jpg, quality=100)

    def create_pledge_main_images(self):
        read_image_path:str = r"image\image_source\eva_board.jpg"
        create_image_number:int = 0
        parlar_name_count:int = 0
        schedule_text:str = ''
        last_time_parlar_name:str = ''
        save_main_image_path_list:list[str] = []
        for i,row in self.merged_syuzai_pledge_df.iterrows():
            #print(row)
            print(row['店舗名'],last_time_parlar_name )
            if last_time_parlar_name != row['店舗名']:
                schedule_text += '\n◆' +  row['店舗名'] + '\n'
                parlar_name_count += 1
                #print(parlar_name_count)
            else:
                pass


            if row['取材名'].startswith(tuple(['旧イベ'])):
                schedule_text += '　☆' + row['取材名']  + '\n'
                last_time_parlar_name = row['店舗名']
                continue
            else:
                schedule_text += '　☆' + row['取材名'] + ' 【' + row['媒体名'] + '】' + '\n'


            if (str(row['公約内容']) == 'nan') or (row['公約内容'] == None) or (row['公約内容'] == ''):
                schedule_text += '       ┗' + '未調査' + '\n'
            else:
                schedule_text += '       ┗' + row['公約内容'] + '\n'

            last_time_parlar_name = row['店舗名']
            #print(parlar_name_count)
            if (parlar_name_count > 9 ) or self.merged_syuzai_pledge_df.index[-1] == i :
                #print('処理開始')
                create_image_number  += 1
                title = f'{self.prefecture_name} {self.target_date_string_jp} スロットイベントまとめ{create_image_number}\n'
                input_image_text : str = title + schedule_text
                text__row_length = input_image_text.count('\n')
                #print('length', text__row_length )
                print(input_image_text)
                save_image_jpg = fr"image\temp_image\eva_board_{self.prefecture_name}_{self.target_date_string_sql}_{create_image_number}.jpg"
                self.recommend_image(input_image_text, text__row_length ,read_image_path,save_image_jpg)
                save_main_image_path_list.append(save_image_jpg)
                schedule_text = ''
                last_time_parlar_name = ''
                parlar_name_count = 0
        self.save_main_image_path_list = save_main_image_path_list
        return self.save_main_image_path_list
