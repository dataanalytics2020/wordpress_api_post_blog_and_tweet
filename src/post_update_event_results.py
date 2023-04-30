import pandas as pd
from datetime import  date, timedelta
import time
import unicodedata
import string
import requests
import mysql.connector
import os
import codecs
import base64
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
try:
    from utils import *
except:
    from src.utils import *

# .env ファイルをロードして環境変数へ反映
from dotenv import load_dotenv
load_dotenv('.env')
# 環境変数を参照

def removal_text(text:str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans( '', '',string.punctuation  + '！'+ '　'+ ' '+'・'+'～' + '‐'))
    return text

def post_line_text(message:str,token:str) -> None:
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message" :  message}
    post = requests.post(url ,headers = headers ,params=payload) 

def post_line_text_and_image(message:str,image_path:str,token:str) -> None:
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization" : "Bearer "+ token}
    payload = {"message" :  message}
    #imagesフォルダの中のgazo.jpg
    print('image_path',image_path)
    files = {"imageFile":open(image_path,'rb')}
    post = requests.post(url ,headers = headers ,params=payload,files=files) 

def insert_data_bulk(df:pd.DataFrame,cnx) -> None:
    insert_sql = f"""INSERT INTO {os.getenv('WORDPRESS_DB_TABLE')}(店舗名, 日付, Nのつく日, 都道府県, 機種名, 台番号, G数, 差枚, BB, RB,ART, BB確率, RB確率, ART確率, 合成確率) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cur = cnx.cursor()
    cur.executemany(insert_sql, df.values.tolist())
    cnx.commit()
    print("Insert bulk data")

def delete_data(cnx,day:int) -> None:
    cursor = cnx.cursor()
    target_days_ago = datetime.date.today() - datetime.timedelta(days=day)
    target_days_ago_str = target_days_ago.strftime('%Y-%m-%d')
    target_days_ago_str
    sql = f"DELETE FROM {os.getenv('WORDPRESS_DB_TABLE')} WHERE 日付 < '{target_days_ago_str} 00:00:00';"
    cursor.execute(sql)
    cnx.commit()
    
def query_prefecture_parlar_data(cnx,prefecture_name:str , past_target_day_number:int) -> pd.DataFrame :
    past_target_day:date = datetime.date.today() - timedelta(days=past_target_day_number)
    str_past_target_day:str = past_target_day.strftime('%Y-%m-%d')
    # SQLを実行する
    #SELECT 引っ張ってきたい列名　FROM　テーブル名 WHERE 条件列 = 'ジャグ（文字列の完全一致）' " 
    column_name = [ '店舗名','日付','Nのつく日', '都道府県', '機種名', '台番号', 'G数', '差枚', \
                    'BB', 'RB', 'ART', 'BB確率','RB確率', 'ART確率', '合成確率', 'id']
    print(column_name)
    with cnx.cursor() as cursor:
        sql = f"SELECT * FROM {os.getenv('WORDPRESS_DB_TABLE')} WHERE 都道府県 = '{prefecture_name}' AND 日付 = '{str_past_target_day} 00:00:00' ;" #AND 機種名 = '主役は銭形3'
        cursor.execute(sql)
        # # Select結果を取り出す
        #results = cursor.fetchall()
        print(sql)
        past_target_date_prefecture_parlar_data_df = pd.DataFrame(data=cursor.fetchall(), index = None, columns = column_name)
    return past_target_date_prefecture_parlar_data_df


def generate_processed_kisyubetu_df(_df):
    kisyubetu_master_df = _df.groupby('機種名').sum()
    kisyubetu_master_df['総台数'] = _df.groupby('機種名').size()
    kisyubetu_master_df = kisyubetu_master_df.reset_index(drop=False).reset_index().rename(columns={'index': '機種順位','ゲーム数': 'G数'})
    kisyubetu_master_df['機種順位'] = kisyubetu_master_df['機種順位'] + 1
    kisyubetu_master_df[['機種順位','機種名','総台数','G数','差枚']]
    kisyubetu_win_daissuu_list = []
    kisyubetu_master_df_list = []
    for kisyu_name in kisyubetu_master_df['機種名']:
        kisyu_df = _df.query('機種名 == @kisyu_name')
        kisyubetu_master_df_list.append(kisyu_df)
        kisyu_win_daisuu = len(kisyu_df[kisyu_df['差枚'] > 0])
        kisyubetu_win_daissuu_list.append(kisyu_win_daisuu)
    kisyubetu_master_df['勝率'] = kisyubetu_win_daissuu_list
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'].astype(str)
    kisyubetu_master_df['総台数'] = kisyubetu_master_df['総台数'].astype(int)
    kisyubetu_master_df['平均G数'] = kisyubetu_master_df['G数'] / kisyubetu_master_df['総台数']
    kisyubetu_master_df['平均G数'] = kisyubetu_master_df['平均G数'].astype(int)
    kisyubetu_master_df = kisyubetu_master_df[kisyubetu_master_df['総台数'] > 2 ]
    kisyubetu_master_df['差枚'] = kisyubetu_master_df['差枚'].astype(int)
    kisyubetu_master_df['平均差枚'] = kisyubetu_master_df['差枚'] / kisyubetu_master_df['総台数']
    kisyubetu_master_df['平均差枚'] = kisyubetu_master_df['平均差枚'].astype(int)
    kisyubetu_master_df['総台数'] = kisyubetu_master_df['総台数'].astype(str)
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'] + '/' + kisyubetu_master_df['総台数']
    kisyubetu_master_df['勝率'] = kisyubetu_master_df['勝率'].map(lambda x : '(' + x + '台) ' + str(round(int(x.split('/')[0])/int(x.split('/')[1])*100,1))  + '%')
    kisyubetu_master_df = kisyubetu_master_df[['機種順位','機種名','勝率','総台数','G数','平均G数','差枚','平均差枚']]
    kisyubetu_master_df = kisyubetu_master_df.sort_values('平均差枚',ascending=False)
    kisyubetu_master_df['機種順位'] = list(range(1,len(kisyubetu_master_df)+1))
    return kisyubetu_master_df

class UtilsDataClass(Blog):
    def __init__(self):
        super().__init__()
        
    def generate_thumbnail(self) :
        image_path = r'image\image_source\千葉.jpg'  # mac
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        write_image_context = f'''{self.target_date_string_jp }\n{self.prefecture_name}\n※店舗結果掲載済\n取材予定まとめ'''
        font_path = r"font/LightNovelPOPv2.otf"
        font = ImageFont.truetype(font_path, size=200)
        draw.multiline_text((160, 0), write_image_context, fill=(255, 255, 255),align='center',font=font, spacing=15, stroke_width=5, stroke_fill=(55, 55, 55))
        thumbnail_image_path = fr'image\temp_image\thumbnail_{self.target_date}_{self.prefecture_name}.jpg'
        image.save(thumbnail_image_path)
        self.thumbnail_image_path = thumbnail_image_path

    def wp_update_post(self,content_id:int,content_text:str,thumbnail_media_id:int,now:str,after_title) -> dict:
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
                'status': 'publish',
                'featured_media':thumbnail_media_id,
                'date':now,
                'title':after_title}
        res = requests.post(f"{WP_URL}/wp-json/wp/v2/posts/{content_id}", headers=headers, json=post)
        if res.ok:
            print("投稿の更新 成功 code:{res.status_code}")
            return json.loads(res.text)
        else:
            print(f"投稿の更新 失敗 code:{res.status_code} reason:{res.reason} msg:{res.text}")
            return {}

target_day:int = 1
for prefecture in ['静岡県','岐阜県','愛知県','三重県','新潟県','富山県','石川県','福井県','山梨県','長野県','群馬県','栃木県','茨城県','福島県','山形県','秋田県','宮城県','岩手県','青森県','北海道','千葉県','埼玉県','神奈川県','東京都']:
    
    try:
        twitter = UtilsTwitterClass()
        utilsdata = UtilsDataClass()
        utilsdata.add_target_date(-(target_day))
        utilsdata.prefecture_name =prefecture

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
            past_target_date_prefecture_parlar_data_df = query_prefecture_parlar_data(cnx,prefecture, target_day)
            # 終了
            #display(past_target_date_prefecture_parlar_data_df)
            cnx.close()

        event_results_text:str =f'<br><h5><span class="hatenamark2 on-color">{utilsdata.target_date_string_jp} {prefecture}のTOP20の結果を掲載しています。タップで上位機種など詳細が見れます。</h5>'
        extract_prefecture_tenpo_data_df = past_target_date_prefecture_parlar_data_df
        tenpobetsu_all_tenpo_df =  extract_prefecture_tenpo_data_df.groupby('店舗名').sum()
        tenpobetsu_all_tenpo_df['総台数'] =  extract_prefecture_tenpo_data_df.groupby('店舗名').size()
        tenpobetsu_all_tenpo_df['平均G数'] = tenpobetsu_all_tenpo_df['G数'] / tenpobetsu_all_tenpo_df['総台数']
        tenpobetsu_all_tenpo_df['平均G数'] = tenpobetsu_all_tenpo_df['平均G数'].astype(int)
        tenpobetsu_all_tenpo_df['平均差枚'] = tenpobetsu_all_tenpo_df['差枚'] / tenpobetsu_all_tenpo_df['総台数']
        tenpobetsu_all_tenpo_df['平均差枚'] = tenpobetsu_all_tenpo_df['平均差枚'].astype(int)
        tenpobetsu_all_tenpo_df = tenpobetsu_all_tenpo_df.sort_values('平均差枚',ascending=False)
        tenpobetsu_all_tenpo_df = tenpobetsu_all_tenpo_df.reset_index()
        tenpobetsu_all_tenpo_df['店舗出率'] =(((tenpobetsu_all_tenpo_df['G数'] * 3) + tenpobetsu_all_tenpo_df['差枚']) / (tenpobetsu_all_tenpo_df['G数'] * 3) )*100
        tenpobetsu_all_tenpo_df['店舗出率'] = tenpobetsu_all_tenpo_df['店舗出率'].map(lambda x : round(x,1))

        for i,(index , record) in enumerate(tenpobetsu_all_tenpo_df.iterrows()):
            #print(record['店舗名'])
            tenpo_zendai_df = past_target_date_prefecture_parlar_data_df[past_target_date_prefecture_parlar_data_df['店舗名'] == record['店舗名']]
            kisyubetsu_df = generate_processed_kisyubetu_df(tenpo_zendai_df)
            if int(record['平均差枚']) > 0:
                heikin_samai = '+' + str(record['平均差枚'])
            else:
                heikin_samai =  str(record['平均差枚'])#[su_spoiler title="4/6(木)愛知県 1位/159店舗　<br>◆プレイランドキャッスル大曽根 <br>5331G +63枚" style="fancy" icon="chevron-circle" anchor="Hello"]
            tweet_text =f'''[su_spoiler title="{utilsdata.target_date_string_jp} {prefecture} {i+1}位/{len(tenpobetsu_all_tenpo_df.index.unique())}店舗
    {record['店舗名'].replace('店','')} 
    平均G数 {record['平均G数']}G　平均差枚 {heikin_samai}枚
    全体出率 {record['店舗出率']}%" style="fancy" icon="chevron-circle" anchor="Hello"]\n'''
            kisyu_count = 0
            gaiyou_df = pd.DataFrame({
                    '平均G数': f'{record["平均G数"]}G',
                    '店舗平均差枚': f'{heikin_samai}枚',
                    '店舗出率': f'{record["店舗出率"]}%',
                    '全体勝率': f'{len(tenpo_zendai_df[tenpo_zendai_df["差枚"] > 0])}/{str(record["総台数"])}',
                    '1000枚↑': f'{str(len(tenpo_zendai_df[tenpo_zendai_df.差枚 > 1000]))}/{record["総台数"]}({round(len(tenpo_zendai_df[tenpo_zendai_df.差枚 > 1000])/record["総台数"]*100,1)}%)',
                    '3000枚↑': f'{str(len(tenpo_zendai_df[tenpo_zendai_df.差枚 > 3000]))}/{record["総台数"]}({round(len(tenpo_zendai_df[tenpo_zendai_df.差枚 > 3000])/record["総台数"]*100,1)}%)'},index=[0]).T
            gaiyou_df.columns = [f'概要']
            #display(gaiyou_df)
            #print(gaiyou_df.to_html(header=None))
            tweet_text += gaiyou_df.to_html(header=None) + '\n'
            # for _,kisyu_betsu_record in kisyubetsu_df.iterrows():
            #     tweet_text += f"\n {kisyu_count+1}位 ▼{kisyu_betsu_record['機種名']}{kisyu_betsu_record['勝率']}\n    ・平均差枚 +{kisyu_betsu_record['平均差枚']}枚 平均G数 {kisyu_betsu_record['平均G数']}G"
            #     kisyu_count += 1
            #     if kisyu_count >= 5:
            #         break
            tweet_text += kisyubetsu_df[['機種名','平均G数','平均差枚','勝率']][:10].to_html(index=False)
            tweet_text += '\n[/su_spoiler]'
            #post_line_text(tweet_text,line_area_token[prefecture])
            if i >= 20:
                break

            event_results_text += tweet_text
        print(event_results_text)
        #break

        title = f"【{utilsdata.prefecture_name}】{utilsdata.target_date_string_jp } パチンコスロットイベント取材まとめ"
        print(title)
        after_title = '※店舗結果掲載済 ' + title

        post_list = utilsdata.get_post_list()
        post_title_contentid_dict:dict[str:int] = {}
        for post in post_list:
            post_title_contentid_dict[post.title] = int(post.id)

        update_content_id:int = int(post_title_contentid_dict[title])
        post = utilsdata.wp.call(methods.posts.GetPost(update_content_id))

        header_text = post.content.split('<h3>更新時間')[0]
        update_time_text:str = f'\n<h3>※店舗結果更新済み 更新時間:{datetime.datetime.now().strftime("%m月%d日%H時%m分")}</h3>'
        footer_text = post.content.split('分</h3>')[-1]
        new_content = header_text + update_time_text + event_results_text +footer_text
        print(new_content)

        title = f"【{utilsdata.prefecture_name}】{utilsdata.target_date_string_jp } パチンコスロットイベント取材まとめ"
        print(title)
        after_title = '※店舗結果掲載済 ' + title

        update_content_id:int = int(post_title_contentid_dict[title])
        print('既存の記事を更新します',update_content_id)

        utilsdata.generate_thumbnail()
        output_thumbnail_path = f'thumbnail_{utilsdata.target_date}_{utilsdata.prefecture_name}_results.jpg'
        media_id = utilsdata.upload_image(utilsdata.thumbnail_image_path, output_thumbnail_path)
        now:str= datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        utilsdata.wp_update_post(update_content_id,new_content,media_id,now,after_title)
        utilsdata.post_line(f'{utilsdata.target_date_string_jp}{prefecture}の事後結果更新が完了しました')
    #break
    except Exception as e :
        t, v, tb = sys.exc_info()
        utilsdata.post_line(f'\n{traceback.format_tb(tb)}\n\n{e}')
        utilsdata.post_line(f'エラー{utilsdata.target_date_string_jp}{prefecture}{e}')
        #break    
        continue
try:
    target_dir = r'image\temp_image'
    shutil.rmtree(target_dir)
except:
    pass
finally:
    os.mkdir(target_dir)
    error_pledge_name_list = list(set(utilsdata.error_pledge_name_list))
    utilsdata.post_line(f'\nエラー媒体名一覧\n{error_pledge_name_list}')
    utilsdata.post_line(f'全ての処理が終わりました。')