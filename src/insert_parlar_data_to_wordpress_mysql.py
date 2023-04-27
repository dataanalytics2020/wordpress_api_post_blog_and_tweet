
import pandas as pd
import datetime
import time
import unicodedata
import string
import requests
import mysql.connector
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from sshtunnel import SSHTunnelForwarder
import pymysql as db
import pandas as pd
import datetime
import sshtunnel
import os
# .env ファイルをロードして環境変数へ反映
from dotenv import load_dotenv
load_dotenv('.env')
# 環境変数を参照

def removal_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans( '', '',string.punctuation  + '！'+ '　'+ ' '+'・'+'～' + '‐'))
    return text

def post_line_text(message,token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message" :  message}
    post = requests.post(url ,headers = headers ,params=payload) 

def post_line_text_and_image(message,image_path,token):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message" :  message}
    #imagesフォルダの中のgazo.jpg
    print('image_path',image_path)
    files = {"imageFile":open(image_path,'rb')}
    post = requests.post(url ,headers = headers ,params=payload,files=files) 

def insert_data_bulk(df,cnx):
    insert_sql = f"""INSERT INTO {os.getenv('WORDPRESS_DB_TABLE')}(店舗名, 日付, Nのつく日, 都道府県, 機種名, 台番号, G数, 差枚, BB, RB,ART, BB確率, RB確率, ART確率, 合成確率) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cur = cnx.cursor()
    cur.executemany(insert_sql, df.values.tolist())
    cnx.commit()
    print("Insert bulk data")

def delete_data(cnx,day):
    cursor = cnx.cursor()
    target_days_ago = datetime.date.today() - datetime.timedelta(days=day)
    target_days_ago_str = target_days_ago.strftime('%Y-%m-%d')
    target_days_ago_str
    sql = f"DELETE FROM {os.getenv('WORDPRESS_DB_TABLE')} WHERE 日付 < '{target_days_ago_str} 00:00:00';"
    cursor.execute(sql)
    cnx.commit()

prefecture_list = ['東京都','静岡県','岐阜県','愛知県','三重県','新潟県','富山県','石川県','福井県','山梨県','長野県','神奈川県','千葉県','埼玉県','群馬県','栃木県','茨城県','福島県','山形県','秋田県','宮城県','岩手県','青森県','北海道']#,'東京都''静岡県','岐阜県','愛知県','三重県'

line_token = os.getenv('LINE_TOKEN')
#print(line_token)
for prefecture in prefecture_list:
    try:
        post_line_text(f'{prefecture}MYSQL追加処理を開始します',line_token)
        cols = ['機種名', '台番号', 'G数', '差枚', 'BB', 'RB', 'ART', 'BB確率', 'RB確率', 'ART確率','合成確率','店舗名']
        ichiran_all_tennpo_df = pd.DataFrame(index=[], columns=cols)
        yesterday = datetime.date.today() + datetime.timedelta(days=-3)
        url = f'https://{os.getenv("SCRAPING_DOMAIN")}/%E3%83%9B%E3%83%BC%E3%83%AB%E3%83%87%E3%83%BC%E3%82%BF/{prefecture}/'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find_all('table')
        tenpo_ichiran_df =pd.read_html(str(table))[-1]
        print(tenpo_ichiran_df)
        all_parlar_count_number = str(len(tenpo_ichiran_df))
        post_line_text(f'{prefecture}は{all_parlar_count_number}の店舗が掲載されいます',line_token)
        count = 0
        error_count = 0
        for i, tenpo_name in enumerate(tenpo_ichiran_df['ホール名'] ):#tenpo_ichiran_df['ホール名']
            try:
                #time.sleep(1)
                print(i,tenpo_name)
                url = f'https://{os.getenv("SCRAPING_DOMAIN")}/{yesterday.strftime("%Y-%m-%d")}-{tenpo_name}'
                res = requests.get(url)
                soup = BeautifulSoup(res.text, 'html.parser')
                table = soup.find(id = "all_data_table")
                dfs =pd.read_html(str(table))
                #display(tenpo_df)
                #time.sleep(1)
                for df in  dfs:
                    try:
                        if '機種名' in list(df.columns):
                            ichiran_df = df
                            ichiran_df['日付'] = yesterday.strftime('%Y-%m-%d')
                            ichiran_df['店舗名'] = tenpo_name
                            #print(tenpo_name)
                            ichiran_df['Nのつく日'] = yesterday.strftime('%d')[-1]
                            ichiran_df['都道府県'] = prefecture 
                            ichiran_df['機種名'] = ichiran_df['機種名'].map(removal_text)
                            ichiran_all_tennpo_df =  pd.concat([ichiran_all_tennpo_df, ichiran_df])
                            print('成功',i,tenpo_name)
                            break
                        else:
                            print('見つかりませんでした',i,tenpo_name)
                        count += 1
                    except Exception as e:
                        print(tenpo_name,e)
                        error_count += 1
                        #time.sleep(1)
                        continue
            except Exception as e:
                print(tenpo_name,e)
                continue

            # if i > 0:
            #     break
        cols = ichiran_all_tennpo_df.columns.tolist()
        cols = cols[-4:] + cols[:-4]
        ichiran_all_tennpo_df = ichiran_all_tennpo_df[cols]  #    OR    df = df.ix[:, cols]
        ichiran_all_tennpo_df['ART']= ichiran_all_tennpo_df['ART'].fillna(0)
        ichiran_all_tennpo_df['BB']= ichiran_all_tennpo_df['BB'].fillna(0)
        ichiran_all_tennpo_df['RB']= ichiran_all_tennpo_df['RB'].fillna(0)
        ichiran_all_tennpo_df['差枚']= ichiran_all_tennpo_df['差枚'].fillna(0)
        ichiran_all_tennpo_df['G数']= ichiran_all_tennpo_df['G数'].fillna(0)
        ichiran_all_tennpo_df = ichiran_all_tennpo_df.fillna('')
        #print(ichiran_all_tennpo_df.iloc[:5])
        # SSH 接続 踏み台接続
        with sshtunnel.SSHTunnelForwarder(
            (os.getenv('SSH_USERNAME'), 10022), 
            ssh_username="pachislot777", 
            ssh_private_key_password=os.getenv('SSH_PRIVATE_KEY_PASSWORD'), 
            ssh_pkey=r"sercret\akasaka.key", 
            remote_bind_address=("mysql8055.xserver.jp", 3306 )
            ) as server:

            # SSH接続確認
            print(f"local bind port: {server.local_bind_port}")
            # データベース接続
            cnx = mysql.connector.connect(
                host="localhost", 
                port=server.local_bind_port, 
                user=os.getenv('WORDPRESS_DB_ID'), 
                password=os.getenv('DB_PASSWORD'), 
                database=os.getenv('WORDPRESS_DB_NAME'), 
                charset="utf8",
                use_pure=True
                )

            # 接続確認
            print(f"sql connection status: {cnx.is_connected()}")
            cursor = cnx.cursor()
            insert_data_bulk(ichiran_all_tennpo_df,cnx)
            tenpo_name_number = len(ichiran_all_tennpo_df['店舗名'].unique())
            post_line_text(f'{prefecture} {tenpo_name_number}/{all_parlar_count_number}件のSQL追加処理に成功しました',line_token)
            delete_data(cnx,35)
            # 終了
            cnx.close()

    except Exception as e:
        print(e)
        post_line_text(f'{prefecture}処理失敗{e}',line_token)

    finally:
        print('終了')
        
# except Exception as e :
#     t, v, tb = sys.exc_info()
#     blog.post_line(f'\n{traceback.format_tb(tb)}\n\n{e}')