# -*- coding: utf-8 -*-
import requests
import json
from wordpress_xmlrpc.methods import media
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc import Client, WordPressPost
from PIL import Image, ImageDraw, ImageFont
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
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
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as ticker
from matplotlib import rcParams
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import timedelta
import datetime
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from wordpress_xmlrpc import Client, WordPressPost, methods
from utils import *
from urllib.parse import urljoin
import mysql
import mysql.connector
print('ライブラリの読み込み完了')

# .envファイルの内容を読み込見込む
load_dotenv()


class Blog():

    def __init__(self):
        WORDPRESS_ID = os.environ['WORDPRESS_ID']
        WORDPRESS_PW = os.environ['WORDPRESS_PW']
        WORDPRESS_URL = os.environ['WORDPRESS_URL']
        self.wp = Client(WORDPRESS_URL, WORDPRESS_ID, WORDPRESS_PW)

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


    def get_post_list(self) -> list[any]:
        '''投稿一覧を取得する関数
        一回で100記事まで取得できる'''
        post_list:list[WordPressPost] = self.wp.call(methods.posts.GetPosts({"number": 50, "offset":0}))
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

    def create_post_content(self):
        pass

    def post_blog(self,main_text):
        title = f"【{self.prefecture_name}】{self.target_date_string_jp} パチンコスロットイベント取材まとめ"
        # Blog Content (html)
        body = main_text
        # publish or draft
        status =  "publish" #or# 'draft'

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
    
    def wp_update_post(self,content_id:int, changed_content:str):

        # URL, User, Password設定
        WP_URL: str = os.getenv('WP_URL')
        WP_USER: str = os.getenv('WP_USER')
        WP_API_PASSWORD: str = os.getenv('REST_API_PW')
        API_URL = f"{WP_URL}/wp-json/wp/v2/"
        url = f'{WP_URL}/wp-json/wp/v2/posts/{content_id}'


        params = {'content':changed_content}

        res = requests.post(
            url,
            params=params,
            auth=( WP_USER, WP_API_PASSWORD),
            )

        return res

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
        main_text += '\n' + html_table_df.to_html(index=False)
        self.main_text = main_text
        return self.main_text



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
        #options.add_argument('--headless')
        #options.add_argument("--no-sandbox")
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
        browser.implicitly_wait(10)
        kiji_element_box = browser.find_element(By.CLASS_NAME,"osusume_list_container")
        kiji_elements_list:list = kiji_element_box.find_elements(By.CLASS_NAME,"osbox")

        for i,syuzai_record_element in enumerate(kiji_elements_list):
            if 'プレミアム会員登録' == browser.find_element(By.CLASS_NAME,"menu_child").text:
                browser = self.login_scraping_site('chubu')
                url = f"https://{os.getenv('SCRAPING_SYUZAI_DOMAIN')}/osusume_list?ken={self.target_date_string_sql}&ymd={self.target_date_string_sql}"
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
                furture_syuzai_list_df = furture_syuzai_list_df.append(record, ignore_index=True)

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
        merged_syuzai_pledge_df = merged_syuzai_pledge_df[~merged_syuzai_pledge_df['取材名'].str.contains('ナビ子')]
        merged_syuzai_pledge_df = merged_syuzai_pledge_df.fillna('未調査')
        merged_syuzai_pledge_df = merged_syuzai_pledge_df.replace({'': '未調査'})
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


blog = Blog()
post_list = blog.get_post_list()
post_title_contentid_dict:dict[str:int] = {}
for post in post_list:
    post_title_contentid_dict[post.title] = int(post.id)

scraping = PledgeScraping()

for target_day_number in range(2,5):
    scraping.add_target_date(target_day_number)
    browser = scraping.login_scraping_site('chubu')
    prefecture_name_and_number_dict = scraping.get_prefecture_name_and_number_dict()
    for prefecture_name in prefecture_name_and_number_dict:
        if 'プレミアム会員登録' == browser.find_element(By.CLASS_NAME,"menu_child").text:
            browser = scraping.login_scraping_site('chubu')
        blog = Blog()
        print(prefecture_name,target_day_number)
        blog.add_target_date (target_day_number)
        blog.prefecture_name = prefecture_name
        print(prefecture_name)
        scraping_target_date_pledge_df = scraping.read_target_date_pledge_df(prefecture_name)
        read_convert_parlar_name_df = scraping.read_convert_parlar_name_df()
        merged_syuzai_pledge_df = scraping.generate_merged_syuzai_pledge_df()
        save_main_image_path_list = scraping.create_pledge_main_images()
        title = f"【{blog.prefecture_name}】{blog.target_date_string_jp } パチンコスロットイベント取材まとめ"
        if title in post_title_contentid_dict:
            update_content_id:int = int(post_title_contentid_dict[title])
            print('既存の記事を更新',update_content_id)
            files:list[Client] = blog.wp.call(methods.media.GetMediaLibrary({"parent_id": update_content_id}))
            for file in files:
                print('画像削除',file.id, file.title)
                ret = blog.wp.call(methods.posts.DeletePost(file.id))
                print(ret)
                #break

            main_text:str = blog.create_main_text(save_main_image_path_list,merged_syuzai_pledge_df)
            #blog.wp_update_post(update_content_id, main_text)
            blog.post_line(f'既存記事を更新しました。\n{prefecture_name}_{blog.target_date_string_jp}')
        else:
            print('新しい記事を作成')
            print(title)
            blog.generate_thumbnail()
            main_text:str = blog.create_main_text(save_main_image_path_list,merged_syuzai_pledge_df)
            #blog.post_blog(main_text)
            blog.post_line(f'新しい記事を作成しました。\n{prefecture_name}_{blog.target_date_string_jp}')
        #break
    #break


try:
    target_dir = r'image\temp_image'
    shutil.rmtree(target_dir)
except:
    pass
finally:
    os.mkdir(target_dir)