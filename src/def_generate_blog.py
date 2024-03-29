# -*- coding: utf-8 -*-
from dotenv import load_dotenv
try:
    from src.utils import *
except:
    from utils import *
    
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from chromedriver_py import binary_path # this will get you the path variable
from selenium.webdriver.chrome.service import Service as ChromeService
#psycopg2のインポート
import psycopg2
import psycopg2.extras


# .envファイルの内容を読み込見込む
load_dotenv()
print('ライブラリの読み込み完了')
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


    def get_post_list(self) -> list[any]:
        '''投稿一覧を取得する関数
        一回で100記事まで取得できる'''
        post_list:list[WordPressPost] = self.wp.call(methods.posts.GetPosts({"number": 600, "offset":0}))
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
            main_text  += f'''\n<a href="{image_url_head_text}{output_path}">\n<img src="{image_url_head_text}{output_path}" alt="{self.prefecture_name}_{self.target_date_string_sql}_パチンコ・パチスロ_イベント" class="alignnone size-full " /></a>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7061697582316562"
     crossorigin="anonymous"></script>
<!-- 中間広告A -->
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-7061697582316562"
     data-ad-slot="8181342037"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>'''
            main_text  +='''\n<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>'''
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
                ad_num = 0
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
                    ad_num += 1
                    if ad_num % 2 == 0:
                        input_by_pledge_text += '''<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7061697582316562" crossorigin="anonymous"></script>
<!-- 中間広告A -->
<ins class="adsbygoogle"
    style="display:block"
    data-ad-client="ca-pub-7061697582316562"
    data-ad-slot="8181342037"
    data-ad-format="auto"
    data-full-width-responsive="true"></ins>
    <script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>'''
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
        #res = requests.get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE')
        import chromedriver_binary
        svc = webdriver.ChromeService(binary_path=chromedriver_binary.chromedriver_filename)
        browser = webdriver.Chrome(options=options)#login_scraping_site

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
    
    def read_target_date_pledge_df(self,prefecture_name:str,area_name:str):
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
                browser = self.login_scraping_site(area_name)
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
                record_df =  pd.DataFrame(record)
                furture_syuzai_list_df = pd.concat([furture_syuzai_list_df,record_df.T])

        self.furture_syuzai_list_df = furture_syuzai_list_df
        return self.furture_syuzai_list_df

    def read_convert_parlar_name_df(self):

        users = os.getenv('HEROKU_PSGR_USER')    # DBにアクセスするユーザー名(適宜変更)
        dbnames = os.getenv('HEROKU_PSGR_DATABASE')   # 接続するデータベース名(適宜変更)
        passwords = os.getenv('HEROKU_PSGR_PASSWORD')  # DBにアクセスするユーザーのパスワード(適宜変更)
        host = os.getenv('HEROKU_PSGR_HOST')     # DBが稼働しているホスト名(適宜変更)
        port = 5432        # DBが稼働しているポート番号(適宜変更)
        # PostgreSQLへ接続
        conn = psycopg2.connect("user=" + users +" dbname=" + dbnames +" password=" + passwords, host=host, port=port)
        conn.autocommit = True
        conn.autocommit
        # PostgreSQLにデータ登録
        cursor = conn.cursor()

        sql = f'''SELECT * 
                    FROM pledge'''#AND (取材ランク = 'S' OR 取材ランク = 'A')
        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        cols = [col.name for col in cursor.description]
        report_df = pd.DataFrame(result, columns=cols)
        #report_df.to_csv('csv/test_location_df.csv',encoding='utf_8_sig',index=False)
        #cols = [col[0] for col in cursorsor.description]
        convert_parlar_name_df = pd.DataFrame(cursor.fetchall(),columns = ['id','取材名','媒体名','公約内容','取得日','更新日','取材ランク'])
        convert_parlar_name_df = convert_parlar_name_df[['id','取材名','媒体名','公約内容','取得日']]
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
print('クラスの読み込み完了')
try:
    for area_name in ['hokkaido','chubu','tohoku','kanto']:
        blog = Blog()
        post_list = blog.get_post_list()
        post_title_contentid_dict:dict[str:int] = {}
        for post in post_list:
            post_title_contentid_dict[post.title] = int(post.id)

        scraping = PledgeScraping()

        for target_day_number in range(0,6):
            scraping.add_target_date(target_day_number)
            browser = scraping.login_scraping_site(area_name)
            prefecture_name_and_number_dict = scraping.get_prefecture_name_and_number_dict()
            for prefecture_name in prefecture_name_and_number_dict:
                browser = scraping.login_scraping_site(area_name)
                blog = Blog()
                print(prefecture_name,target_day_number)
                blog.add_target_date (target_day_number)
                blog.prefecture_name = prefecture_name
                print(prefecture_name)
                scraping_target_date_pledge_df = scraping.read_target_date_pledge_df(prefecture_name,area_name)
                read_convert_parlar_name_df = scraping.read_convert_parlar_name_df()
                merged_syuzai_pledge_df = scraping.generate_merged_syuzai_pledge_df()
                save_main_image_path_list = scraping.create_pledge_main_images()
                title = f"【{blog.prefecture_name}】{blog.target_date_string_jp} パチンコスロットイベント取材まとめ"
                if title in post_title_contentid_dict:
                    update_content_id:int = int(post_title_contentid_dict[title])
                    print('既存の記事を更新します',update_content_id)
                    files:list[Client] = blog.wp.call(methods.media.GetMediaLibrary({"parent_id": update_content_id}))
                    for file in files:
                        print('画像削除',file.id, file.title)
                        ret = blog.wp.call(methods.posts.DeletePost(file.id))
                        print(ret)
                        #break

                    main_text:str = blog.create_main_text(save_main_image_path_list,merged_syuzai_pledge_df)
                    generate_by_pledge_text = blog.generate_by_pledge_text(merged_syuzai_pledge_df,scraping)
                    main_text  += generate_by_pledge_text
                    blog.wp_update_post(update_content_id, main_text )
                    blog.post_line(f'既存記事を更新しました。\n{prefecture_name}_{blog.target_date_string_jp}')
                else:
                    print('新しい記事を作成します')
                    print(title)
                    blog.generate_thumbnail()
                    main_text:str = blog.create_main_text(save_main_image_path_list,merged_syuzai_pledge_df)
                    generate_by_pledge_text = blog.generate_by_pledge_text(merged_syuzai_pledge_df,scraping)
                    main_text  += generate_by_pledge_text
                    blog.post_blog(main_text)
                    blog.post_line(f'新しい記事を作成しました。\n{prefecture_name}_{blog.target_date_string_jp}')
                #break
            #break
        #break

except Exception as e :
    t, v, tb = sys.exc_info()
    print(f'\n{traceback.format_tb(tb)}\n\n{e}')
    blog.post_line(f'{e}\n{traceback.format_tb(tb)}\n\n{e}')

finally:
    try:
        target_dir = r'image\temp_image'
        shutil.rmtree(target_dir)
    except:
        pass
    finally:
        os.mkdir(target_dir)
        browser.quit()
        #error_pledge_name_list = list(set(blog.error_pledge_name_list))
        #blog.post_line(f'\nエラー媒体名一覧\n{error_pledge_name_list}')
        #blog.post_line(f'全ての処理が終わりました。')