
# -*- coding: utf-8 -*-
try:
    from src.utils import *
except:
    from utils import *
    
from dotenv import load_dotenv
load_dotenv(".env")

print('読み込み完了')


def get_concat_v_blank(im_list, color=(0, 0, 0)):
    dst = Image.new('RGB', (1000,max(im.height for im in im_list)), color)
    for i,im in enumerate(im_list):
        if i == 0:
            dst.paste(im, (0, 0))
        else:
            dst.paste(im, (0, im_list[i-1].height))
    return dst

def get_concat_h_blank(im_list, color=(0, 0, 0)):
    
    dst = Image.new('RGB', (1000*len(im_list),max(im.height for im in im_list)), color)
    for i,im in enumerate(im_list):
        print(i)
        if i == 0:
            dst.paste(im, (0, 0))
        else:
            dst.paste(im, ((i)*1000,0))
    return dst


# アスペクト比を固定して、幅が指定した値になるようリサイズする。
def scale_to_width(img_path, width):
    img = Image.open(img_path)
    height = round(img.height * width / img.width)
    return img.resize((width, height))

def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                      for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst

scraping = PledgeScraping()
target_day_number = 1
scraping.add_target_date(target_day_number)
browser = scraping.login_scraping_site('kanto')
prefecture_name_and_number_dict = scraping.get_prefecture_name_and_number_dict()

#pledge_imageフォルダの中身をリスト化
pledge_image_path_list = []
for pledge_image_path in glob.glob(r'image\pledge_image\*'):
    pledge_image = str(pledge_image_path).replace('image\\pledge_image\\','').replace('.jpg','')
    pledge_image_path_list.append(pledge_image)
    
rank_color_dict:dict[str:tuple] = {'S':(255,0,0),'A':(0,128,0),'B':(255,255,0),'C':(0,0,255),'・':(255,255,255)}
prefecture_wp_url_dict ={'神奈川県':'http://bit.ly/3MByjN60',
                         '千葉県':'http://bit.ly/3Gzq54c',
                        '埼玉県':'http://bit.ly/414nHdR'}

for prefecture_name in ['埼玉県','千葉県','神奈川県']:
    for target_dir in [r'image\temp_concat_image_dir',r'image\temp_tweet_image_dir',r'image\temp_image']:
        try:
            shutil.rmtree(target_dir)
        except:
            pass
        finally:
            os.mkdir(target_dir)

    blog = Blog()
    twitter = UtilsTwitterClass()
    print(prefecture_name,target_day_number)
    blog.add_target_date (target_day_number)
    blog.prefecture_name = prefecture_name
    print(prefecture_name)
    scraping_target_date_pledge_df = scraping.read_target_date_pledge_df(prefecture_name)
    read_convert_parlar_name_df = scraping.read_convert_parlar_name_df()
    merged_syuzai_pledge_df = scraping.generate_merged_syuzai_pledge_df()
    save_main_image_path_list = scraping.create_pledge_main_images()

    title = f"【{blog.prefecture_name}】{blog.target_date_string_jp} パチンコスロットイベント取材まとめ"
    input_by_pledge_text = f'\n<h2>{scraping.prefecture_name} {scraping.target_date_string_jp} 媒体別取材まとめ</h2>\n'
    pledge_name_list:list[str] = list(merged_syuzai_pledge_df['媒体名'].unique())
    for pledge_name in ['リニューアルオープン','フリー','その他取材・企画','その他','未調査']:
        try:
            pledge_name_list.remove(pledge_name)
            pledge_name_list.append(pledge_name)
        except:
            pass
    error_pledge_name_list = []

    #リストの先頭に旧イベを追加
    if '旧イベ' in pledge_name_list:
        pledge_name_list.remove('旧イベ')
        pledge_name_list.insert(0, '旧イベ')

    if 'ドリスロ' in pledge_name_list:
        pledge_name_list.remove('ドリスロ')
        pledge_name_list.insert(2, 'ドリスロ')

    for pledge_name in pledge_name_list:
        extract_pledge_name_df = merged_syuzai_pledge_df[merged_syuzai_pledge_df['媒体名'] == pledge_name]
        #display(extract_pledge_name_df)
        concat_generate_pledge_image_list:list[Image] = []
        if pledge_name in pledge_image_path_list:
            print(pledge_name)
            image = Image.open(fr'image\pledge_image\{pledge_name}.jpg')
            concat_generate_pledge_image_list.append(image)
        else:
            print('error',pledge_name)
            #取材別のヘッダー画像を作成
            image = Image.open(r'image\pledge_image\eva_pledge_banner.jpg')
            draw = ImageDraw.Draw(image)
            #フォントを指定する（フォントファイルはWindows10ならC:\\Windows\\Fontsにあります）
            font_path = r"font\NotoSerifJP-Black.otf"
            font = ImageFont.truetype(font_path, size=80)
            draw.multiline_text((180,10), f'{pledge_name}\n{blog.target_date_string_jp} {prefecture_name}', fill=(255,255,255), font=font,spacing=10)
            #画像を保存する
            image.save(fr'image\temp_image\test_{blog.target_date_string_jp}_{pledge_name}.jpg')
            concat_generate_pledge_image_list.append(image)
        #write_pledge_text = ''

        for rank in ['S','A','B','C','・']:
            extract_syuzai_name_df  = extract_pledge_name_df[extract_pledge_name_df['取材ランク'] == rank]
            print(rank)
            if len(extract_syuzai_name_df) == 0:
                continue
            #display(extract_syuzai_name_df)
            write_pledge_text = ''
            for syuzai_name in extract_syuzai_name_df['取材名'].unique():
                print('1',syuzai_name)
                write_pledge_text += '\n\n' + syuzai_name 
                extract_parlar_name_df  = extract_pledge_name_df[extract_pledge_name_df['取材名'] == syuzai_name]
                pre_pledge_name = ''
                image = Image.open(fr'image\image_source\eva_board.jpg')
                for i,row in extract_parlar_name_df.iterrows():
                    #print(row)
                    if pre_pledge_name != row['取材名']:
                        write_pledge_text += f'\n┗公約 : {row["公約内容"]}'
                        write_pledge_text += f'\n　 ◆{row["店舗名"]}'
                    else:
                        write_pledge_text += f'\n　 ◆{row["店舗名"]}'
                        
                    pre_pledge_name = row['取材名']
                draw = ImageDraw.Draw(image)
                #フォントを指定する（フォントファイルはWindows10ならC:\\Windows\\Fontsにあります）
                font_path = r"font\LightNovelPOPv2.otf"
                font = ImageFont.truetype(font_path, size=50)
                draw = ImageDraw.Draw(image)
                draw.multiline_text((50, -100), write_pledge_text, fill=(255,255,255),align='left',font=font, spacing=15)
                save_image_jpg = r'image\temp_image\\' +fr'{prefecture_name}_{blog.target_date_string_jp}_{pledge_name}_{rank}.jpg'
                image_length = write_pledge_text.count('\n')
                print(image_length)
                print('length', image_length)
                length_croped = image_length * 70  # 500
                print(length_croped)
                im_crop = image.crop((0, 0, 1000, length_croped))
                im_crop.save(save_image_jpg, quality=100)
                
                line_width = 20  # line width（枠線一本の幅）
                waku_color = rank_color_dict[rank] # 枠線の色（RGB）

                # 元になる画像からImageオブジェクトを作成
                src_im = Image.open(save_image_jpg)
                sw, sh = src_im.size  # 元の画像のサイズを取得

                # キャンバスを作成
                # この画像に枠線と元の画像を合成する
                cw, ch = sw + line_width * 2, sh + line_width * 2  # キャンバスのサイズを元の画像から生成
                canvas_im = Image.new('RGB', (cw, ch))

                # キャンバスのImageDrawオブジェクトを作成
                canvas = ImageDraw.Draw(canvas_im)

                # キャンバスを単色で塗りつぶす
                canvas.rectangle([(0, 0), (cw, ch)], fill=waku_color)

                # キャンバスの画像に元の画像を貼り付け
                canvas_im.paste(src_im, (line_width, line_width))
                canvas_im.save(save_image_jpg)
            concat_generate_pledge_image_list.append(canvas_im)
                #break
            #break
        # if len(extract_pledge_name_df ) != 0:
        #     # print('\n■',baitai,sep='')
        #     write_pledge_text += '<h3>' + string_date_only + ' ' + todoufuken_kanji + ' スロット ' + baitai + '</h3>' + f'\n<img src="http://slotana777.com/wp-content/uploads/2021/04/{error_baitai}.jpg" alt="{error_baitai} タイトル画像" width="1000" height="400" class="alignnone size-full " />\n'
        # else:
        #     pass
        #break

        get_concat_v_multi_resize(concat_generate_pledge_image_list).save(fr'image\temp_concat_image_dir\{prefecture_name}_{blog.target_date_string_jp}_{pledge_name}.jpg')

    #ディレクトリの中を時間順にリストで取得する
    concat_temp_image__list = []
    for file in sorted(glob.glob(r'image\temp_concat_image_dir\*.jpg'), key=os.path.getmtime):
        print(file)
        #画像を開く
        image = Image.open(file)
        concat_temp_image__list.append(image)
        #画像をリサイズする

    temp_list = []
    self_image_count_num = 0
    for y in range(len(concat_temp_image__list)):
        self_image_count_num += 1
        temp_list.append(concat_temp_image__list[y])
        if len(temp_list) == 6:
            self_image_count_num += 1
            print('ここで関数実行とselfに挿入',temp_list)
            save_image_jpg = r'image\temp_tweet_image_dir\pillow_concat_h_blank_' +fr'{self_image_count_num}.jpg'
            get_concat_h_blank(temp_list, (169, 206, 255)).save(save_image_jpg)
            scale_to_width(save_image_jpg, 3800).save(save_image_jpg)
            twitter.image_path_list.append(save_image_jpg)
            temp_list = []
            
            if self_image_count_num == 4:
                break

    if len(temp_list) != 0:
        self_image_count_num += 1
        print('ここで関数実行とselfに挿入',temp_list)
        save_image_jpg = r'image\temp_tweet_image_dir\pillow_concat_h_blank_' +fr'{self_image_count_num}.jpg'
        get_concat_h_blank(temp_list, (169, 206, 255)).save(save_image_jpg)
        scale_to_width(save_image_jpg, 3800).save(save_image_jpg)
        twitter.image_path_list.append(save_image_jpg)
    else:
        pass

    tweet_text:str = f'{prefecture_name} '+ scraping.target_date_string_jp + '明日の媒体別まとめ' 

    for i,parlar_name in enumerate(merged_syuzai_pledge_df['店舗名'].unique()):
        tweet_text += '\n' + parlar_name
        if i > 3:
            break
    tweet_text += '\n' + '他' + str(len(merged_syuzai_pledge_df['店舗名'].unique()) - 4) + '店舗'
    tweet_text += '\n' + '詳細はこちら' + '\n' + prefecture_wp_url_dict[prefecture_name]
    print(tweet_text)

    twitter.tweet_text = tweet_text
    twitter.id =os.getenv('TWITTER_KANTO_ID')
    twitter.pw =os.getenv('TWITTER_KANTO_PW')
    twitter.twitter_login()
    twitter.post_tweet()
    
    for target_dir in [r'image\temp_concat_image_dir',r'image\temp_tweet_image_dir',r'image\temp_image']:
        try:
            shutil.rmtree(target_dir)
        except:
            pass
        finally:
            os.mkdir(target_dir)

    #break