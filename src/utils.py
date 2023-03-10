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
import openpyxl
import glob

import json
import time
import datetime
from datetime import datetime, date, timedelta
import numpy as np
import gspread

from PIL import Image, ImageDraw, ImageFont
import cv2
import datetime
import shutil
import pymysql
print('読み込み完了')

class UtilsTwitterClass():
    #ブラウザ処理
    #日付関連処理

    today = datetime.date.today()
    week_list = [ '(日)','(月)', '(火)', '(水)', '(木)', '(金)', '(土)','(日)']
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    date_string = tomorrow.strftime('%m').lstrip('0') + '/' + tomorrow.strftime('%d').lstrip('0') + week_list[tomorrow.isoweekday()]


    def __init__(self):
        
        week_list = [ '(日)','(月)', '(火)', '(水)', '(木)', '(金)', '(土)','(日)']
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        tomorrow_date_string = tomorrow.strftime('%m').lstrip('0') + '/' + tomorrow.strftime('%d').lstrip('0') + week_list[tomorrow.isoweekday()]
        yesterday_date_string =  yesterday.strftime('%m').lstrip('0') + '/' +  yesterday.strftime('%d').lstrip('0') + week_list[ yesterday.isoweekday()]
        self.tomorrow_8numbers_string = tomorrow.strftime('%Y%m%d')
        self.tomorrow_date_stinrg = tomorrow_date_string
        self.yesterday = yesterday
        self.tomorrow = tomorrow
        self.yesterday_date_string = yesterday_date_string
        self.id = 'pachinkas_ai' #'slotana777' #'akasaka_develop'
        self.pw = '6tjc5306' #'6tjc5306' #'slopachi777'
        self.tweet_text = ''
        self.image_path_list = []
        self.main_tweet_text = ''
        #ディレクトリ
        self.project_dir_path = os.path.join(os.path.expanduser(r'~'),"Desktop","influence_twitter_akasaka")
        self.image_dir_path = os.path.join(self.project_dir_path,"image")
        self.tweet_footer_text = '\n\n#赤坂DB' + yesterday.strftime('%Y%m%d') + '\n\n'
        #os.path.join(self.image_dir_path," ") これ/imageの基本パス
        self.created_image_dir_path = os.path.join(self.image_dir_path,"created_image")
        self.servise_account_json_path = os.path.join(self.project_dir_path,"config", "twitteranalytics-jsonsercretkey.json")

    def syuzai_df(self):
        
        SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.servise_account_json_path, SCOPE)
        gs = gspread.authorize(credentials)
        SPREADSHEET_KEY = '1p_D461z7t3bbL0hbknenZNn2wPIVHz03-wNPg7IBCL0'
        worksheet = gs.open_by_key(SPREADSHEET_KEY).worksheet('master')
        df = pd.DataFrame(worksheet.get_all_values())
        df.columns = list(df.loc[0, :])
        df.drop(0, inplace=True)
        df.reset_index(inplace=True)
        df.drop('index', axis=1, inplace=True)
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        df['日付'] = pd.to_datetime(df['日付'])
        df = df[df['日付'] <= pd.to_datetime(tomorrow)]
        df['日付'] = df['日付'].dt.strftime('%Y/%m/%d')

        self.df = df
        self.tomorrow_df = df
        
        
        

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

    def create_image(self,baitai_name,write_syuzai_text):
        if baitai_name == 'slopachi':
            color = (0,0,124)#えんじ色
            kouyaku_string = '''公約　スロパチ広告
┗6台並び(設定⑤⑥)×複数箇所
'''
            
        elif baitai_name == 'ryuko':
            color = (15,14,14)#ほぼ黒
            kouyaku_string = '''公約 りゅーこ
┗3台以上設置の2機種が
     全台設定⑤⑥'''

        elif baitai_name == 'hissyouhon':
            color = (232,159,0)#水色
            kouyaku_string = ''

        elif baitai_name == 'atsuhime':
            color = (100,100,255)#赤色
            kouyaku_string = '''公約 アツ姫広告
┗3台並び(設定⑤⑥)×複数箇所'''
            
        elif baitai_name == 'sloslo':
            color = (75,75,75)#灰色
            kouyaku_string = '''公約 スロスロ広告
┗全体出率100%以上'''

        elif baitai_name == 'akasaka':
            color = (128,64,0)#灰色
            kouyaku_string = '''集計方法
┗webサイトから集計
※推定の部分もあるので要確認'''
            
        else:
            pass


        #画像の生成
        # 4000(高さ) x 1000(幅)　3レイヤー(BGR)を定義
        size = (4000, 1000, 3)
        # 空の配列
        img = np.zeros(size, dtype=np.uint8)
        # ポリゴンの座標を指定
        pts = np.array( [ [0,0], [0,4000], [1000, 4000], [1000,0] ] )
        dst = cv2.fillPoly(img, pts =[pts], color=color)
        temp_image_path = os.path.join(self.image_dir_path,"temp_image.png")

        cv2.imwrite(temp_image_path, dst)
        image_path = (temp_image_path)
        write_image_text = kouyaku_string + '\n\n' + instance.date_string +  '\n\n'  + syuzai_text
        print(instance.date_string)
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        #フォントを指定する（フォントファイルはWindows10ならC:\\Windows\\Fontsにあります）
        #フォントの読み込
        if os.name == 'nt':
            font_path =  r"C:\Users\slotd\Desktop\influence_twitter_akasaka\config\LightNovelPOPv2.otf"
        elif os.name == 'posix':
            font_path = "/Users/devlopment/Library/Fonts/LightNovelPOPv2.otf"

        #sizeは文字サイズです（とりあえず適当に50）
        font = ImageFont.truetype(font_path, size=50)
        #最初の(0,0)は文字の描画を開f始する座標位置です　もちろん、(10,10)などでもOK
        #fillはRGBで文字の色を決めています
        draw.text((45,45), write_image_text , fill=(255,255,255), font=font, align ="left")
        output_path = os.path.join(self.image_dir_path,"atsuhime_2.png")
        
        image.save(output_path)
        output_path = os.path.join(self.image_dir_path,"atsuhime_2.png")
        output_path_croped = os.path.join(self.image_dir_path,"atsuhime_2.png")
        #画像切り抜き
        im = Image.open(output_path)
        length_croped =  100 + write_image_text.count('\n') * 70

        im_crop = im.crop((0, 0, 1000, length_croped))
        im_crop.save(output_path_croped, quality=100)
        instance.write_image_text = write_image_text
        
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        date_8figures_string = tomorrow.strftime('%Y%m%d')
        print('baitai_name',f'{baitai_name}')
        im1_image_path = os.path.join(self.image_dir_path,"png",f"{baitai_name}.png")
        #print('im1_image_path',im1_image_path)
        im1 = cv2.imread(im1_image_path)
        #print('im1',im1)

        im2_image_path = os.path.join(self.image_dir_path,"atsuhime_2.png")
        #print('im2_image_path',im2_image_path)
        im2 = cv2.imread(im2_image_path)
        #print('im2',im2)
        im_v = cv2.vconcat([im1, im2])
        created_image_path = os.path.join(self.image_dir_path,"created_image",f"{baitai_name}_{date_8figures_string}.png")
        cv2.imwrite(created_image_path, im_v)


    def get_concat_h_blank(self,baitai_name_1,baitai_name_2):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        date_8figures_string = tomorrow.strftime('%Y%m%d')

        #self.created_image_dir_path = os.path.join(self.image_dir_path,"created_image")
        im_cv_1_path = os.path.join(self.created_image_dir_path,f"{baitai_name_1}_{date_8figures_string}.png")
        im_cv_1 = cv2.imread(im_cv_1_path)

        im_cv_2_path = os.path.join(self.created_image_dir_path,f"{baitai_name_2}_{date_8figures_string}.png")
        im_cv_2 = cv2.imread(im_cv_2_path)
        
        im1_path = os.path.join(self.created_image_dir_path,f"{baitai_name_1}_{date_8figures_string}.png")
        im2_path = os.path.join(self.created_image_dir_path,f"{baitai_name_2}_{date_8figures_string}.png")
        im1 = Image.open(im1_path)
        im2 = Image.open(im2_path)
        
        #print(im1)
        if im_cv_1.shape[0] < im_cv_2.shape[0]:
            #print(baitai_name_1)
            color = tuple(im_cv_1[-30, -30, :])
            color =  color[::-1]
            #print(color)
        else:
            #print(baitai_name_2)
            color = tuple(im_cv_2[-30, -30, :])
            color =  color[::-1]
            #print(color)
        
        dst = Image.new('RGB', (im1.width + im2.width, max(im1.height, im2.height)), color)
        dst.paste(im1, (0, 0))
        dst.paste(im2, (im1.width, 0))
        image_path =  os.path.join(self.created_image_dir_path,f"{baitai_name_1}_{baitai_name_2}_{date_8figures_string}.png")
        print(image_path)
        dst.save(image_path)
        self.image_path_list.append(image_path)


    def create_tweet_text(self,query_tomorrow_df):
        input_twitter_text = ''
        query_tomorrow_df['媒体'] = query_tomorrow_df['媒体'].map({'slopachi':'スロパチ','ryuko':'りゅーこ','hissyouhon':'必勝本','atsuhime':'アツ姫','sloslo':'スロスロ','akasaka':'演者'})
        print(query_tomorrow_df)
        for row in query_tomorrow_df.itertuples():
            #print('文字数',len(input_twitter_text))
            #print(row[3])
            if row[3] == '':
                continue

            else:
                for x in range(2,11):
                    #print(row[2])

                    if x == 2:
                        input_twitter_text += '\n\n◆' + row[x]
                        
                    elif row[x] == '':
                        break

                    else:
                        input_twitter_text += '\n' + row[x]

        text_1 = f'{instance.date_stinrg}※毎日21時頃ツイート\n明日の都内取材予定'
        text_2 = ''
        text_3 = ''

        input_twitter_text_list = input_twitter_text.split('\n')[1:]

        for text in input_twitter_text_list:
            
            if 100 < len(text_1) <= 110:
                text_1 += '\n' + text +'\nリプに続く'
                continue

            if len(text_1) < 110:
                text_1 += '\n' + text

            elif 110 < len(text_1) < 220:
                text_2 += '\n' + text

            else :
                text_2 += '\n' + text

        tweet_footer_text = '\n\n#赤坂DB' + date_8figures_string + '\n\n'

        self.tweet_footer_text = tweet_footer_text
        text_1 += '\n\n#赤坂DB' + date_8figures_string + '\n\n'

        print('===============tweet_text ツイート用文章=============\n',text_1,'\n===============ツイート用文章=============\n')
        print('===============reply_text_1 リプ用文章1=============\n',text_2,'\n===============リプ用文章1=============')
        print('===============reply_text_2 リプ用文章2=============\n',text_3,'\n===============リプ用文章2=============')
        self.tweet_text = text_1
        self.reply_text_1 =  text_2 
        self.reply_text_2 =  text_3

    def post_error_line(self,message,image_path):
        url = "https://notify-api.line.me/api/notify"
        token = "72wjnow36IUmMDI82RIJFtEQ06eJcGNzAwPz1cNzoAE"
        headers = {"Authorization" : "Bearer "+ token}
        payload = {"message" :  message}
        #imagesフォルダの中のgazo.jpg
        print('image_path',image_path)
        files = {"imageFile":open(image_path,'rb')}
        post = requests.post(url ,headers = headers ,params=payload,files=files) 
    
    def post_slack(self,text):
        requests.post('https://hooks.slack.com/services/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', data = json.dumps({
        'text': f'https://twitter.com/{self.id}\n\n{text}', # 投稿するテキスト
        'username': u'赤坂_通知bot', # 投稿のユーザー名
        'icon_emoji': u':ureshi_yoshi:', # 投稿のプロフィール画像に入れる絵文字
        'link_names': 1, # メンションを有効にする
        })) 

    def add_random_samai(self,data):
        data = int(data) - random.choice([-1, 0, 1])
        return data


    def change_plus_convert(x):
        x = int(x)
        if x >= 0 :
            x = '-' + str(x).replace('+','')
        else:
            x = '+' + str(x).replace('-','')
        #print(x)
        return x
            
    def create_zizenichiran_image(self,tenpo_name,baitai_name,date_string):
        global df
        conn = pymysql.connect(host='127.0.0.1',
                                    user='akasaka',
                                    password='slopachi777',
                                    db='akasaka_db',
                                    port=3307)
        print(conn)
        
        # yesterday = datetime.today() + timedelta(days=-1)
        date = date_string#yesterday.strftime('%Y/%m/%d')

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
        df = pd.DataFrame(data=cursor.fetchall(), index = None, columns = column_name)
        print(df)
        def add_random_samai(data):
            data = int(data) - random.choice([-1, 0, 1])
            return data

        df['差枚'] = df['差枚'].map(add_random_samai) 
        #df['差枚'].sum()


        tenpo_sousamai : str =  str(df['差枚'].sum()) + '枚'


        print('総差枚',tenpo_sousamai)
        tenpo_heikin_samai : str = str(int(df['差枚'].sum() / len(df))) + '枚'
        print('平均差枚',tenpo_heikin_samai)

        # tenpo_heikin_samai
        # tenpo_sousamai

        heikin_gamesuu = str(int(df['総回転数'].sum() / len(df))) + 'G'
        print('平均G数から',heikin_gamesuu)
        #print(self.baitai_name_jpn)

        if baitai_name == 'slopachi':
            self.baitai_name_jpn = 'スロパチ広告'
            
        elif baitai_name == 'ryuko':
            self.baitai_name_jpn = 'りゅーこ'

        elif baitai_name == 'hissyouhon':
            self.baitai_name_jpn = '必勝本広告'

        elif baitai_name == 'atsuhime':
            self.baitai_name_jpn = 'アツ姫広告'
            
        elif baitai_name == 'sloslo':
            self.baitai_name_jpn = 'スロスロ広告'

        elif baitai_name == 'akasaka':
            pass

        tweet_text = ''
        main_tweet_text = f'''
    {instance.yesterday_date_string}
    【{self.tenpo_name_plus_syuzai_name}】
    『{self.baitai_name_jpn}』結果

    ◆総差枚 {tenpo_sousamai}
    ◆平均差枚 {tenpo_heikin_samai}
    ◆平均G数 {heikin_gamesuu}

    '''

    def generate_database_query_df(self,tenpo_name,baitai_name,date):
        import pymysql
        global zendai_ichiran_df
        
        conn = pymysql.connect(host='127.0.0.1',
                                    user='akasaka',
                                    password='slopachi777',
                                    db='akasaka_db',
                                    port=3307)
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


        if baitai_name == 'slopachi':
            self.baitai_name_jpn = 'スロパチ広告'
            
        elif baitai_name == 'ryuko':
            self.baitai_name_jpn = 'りゅーこ'

        elif baitai_name == 'hissyouhon':
            self.baitai_name_jpn = '必勝本広告'

        elif baitai_name == 'atsuhime':
            self.baitai_name_jpn = 'アツ姫広告'
            
        elif baitai_name == 'sloslo':
            self.baitai_name_jpn = 'スロスロ広告'

        elif baitai_name == 'akasaka':
            pass

        
        return zendai_ichiran_df


    

