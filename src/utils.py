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


        for image_path in self.image_path_list:
            element.send_keys(image_path)
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


    def post_line(message):
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