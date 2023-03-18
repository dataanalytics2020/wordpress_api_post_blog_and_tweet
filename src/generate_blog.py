

        title = f'{todouhuken_str} 明日のスロットイベントまとめ ' + tomorrow_str
        context_completed = ''
        context_list = context.split('\n\n')
        context_list = context_list[1:]
        #context_list = sorted(context_list)
        context_list_completed = []
        for context_tenpo in context_list:
            print('context_tenpo', context_tenpo)
            if '赤色' in context_tenpo:
                continue
            if '実践収録' in context_tenpo:
                continue
            elif '\n' in context_tenpo:
                context_list_completed.append(context_tenpo)
            else:
                continue
        for text in context_list_completed:
            print('text', text)
            context_completed += '\n\n' + text

        context_image = title + context_completed
        length = context_image.count('\n')
        print('length', length)
        print(context_image)

        #########文章作成部分####################
        context_1 = f'{todouhuken_str} {tomorrow_str} 明日のスロットイベントまとめ\n⚡️毎日前日17時配信⚡️\n'
        for tenpo_text in tenpo_only_text:
            context_1 += tenpo_text + '\n'
            if len(context_1) > 87:
                break

            print(len(context_1))
        context_1 += '\n\n' + '#スロット ' + '\n' + f'#{todouhuken_str} ' + '\n\n詳細はこちら \nbit.ly/3u5tZJN'
        print(context_1)

        #########画像作成部分####################
        # 投稿用イメージ作
        # recommend_image(todouhuken,context_image,length)
        # wpに画像投稿i
        # wp_post_image(save_image_jpg,todouhuken,tomorrow_str)

        n = 0
        text_1 = f'{todouhuken_str} 明日のイベントまとめ１ ' + '\n'
        text_2 = f'{todouhuken_str} 明日のイベントまとめ２ ' + '\n\n'
        text_3 = f'{todouhuken_str} 明日のイベントまとめ３' + '\n\n'
        text_4 = f'{todouhuken_str} 明日のイベントまとめ４' + '\n\n'
        for x in context_completed.split('■'):
            if n <= 8:
                text_1 += x
            elif 16 >= n > 8:
                text_2 += x
            elif 23 >= n > 16:
                text_3 += x
            else:
                text_4 += x
            n = n + 1

        #output_path = imgPath.replace('/Users/macbook/Desktop/eva_board_','')
        recommend_image2(todoufuken_kanji, text_1, text_1.count('\n'), 1)

        upload_image(save_image_jpg, save_image_jpg.replace('image/全媒体/',''))

        recommend_image2(todoufuken_kanji, text_2, text_2.count('\n'), 2)

        upload_image(save_image_jpg, save_image_jpg.replace('image/全媒体/',''))

        recommend_image2(todoufuken_kanji, text_3, text_3.count('\n'), 3)

        upload_image(save_image_jpg, save_image_jpg.replace('image/全媒体/',''))

        recommend_image2(todoufuken_kanji, text_4, text_4.count('\n'), 4)

        upload_image(save_image_jpg, save_image_jpg.replace('image/全媒体/',''))

        # スプレッドシート書き込み
        SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUT_FILE, SCOPE)
        gs = gspread.authorize(credentials)
        SPREADSHEET_KEY = '1WxS9gZtK1vusQr-iHYt65HggSNkbOmclGzX6ipkesUg'
        worksheet = gs.open_by_key(SPREADSHEET_KEY).worksheet('master')
        for syuzai in chousa_syuzai:
            syuzai_list.append(syuzai)
            print(syuzai)
            worksheet.append_row([syuzai, '未調査', '未調査'])

        syuzai_df()
        # 改造用
        syuzai_dict = {}

        tenpo_list = []
        syuzai_name_list = ['明日の取材一覧']
        tenpo_name_list = [f'東京都 {tomorrow_str}']
        tenpo_only_text = []
        chousa_syuzai = []
        context = ''
        tenpo_name = ''
        ichitenpo_syuzai = []
        syuzai_df()
        cols = ['tenpo_name', 'baitai', 'syuzai', 'kouyaku']
        tokyou_syuzai_df = pd.DataFrame(index=[], columns=cols)

        context = f'{h1_text} 取材まとめ'
        print(context)
        #number = ['②','③','④','⑤','⑥','⑦','⑧','⑨']
        n = 0
        for kiji in kiji_list:
            syuzai_list = kiji.find_all(class_='list_event_name_li')
            street_address = kiji.find_all(class_='oslha')[0].text
            hall_man = kiji.find(class_='osle_other1')
            tenpo_name = kiji.find(class_='oslh2').text.replace('店', '').replace('\n', '').replace(' ', '').replace('　', '')
            try:
                hall_man_text = hall_man.text
                hall_man_text = hall_man_text.replace('『', '').replace('』', '').replace('※', '')
                hall_man_text = re.sub(r'\[.*?\]', '', hall_man_text)
                hall_man_text = re.sub(r'\予想並び.*?\人', '', hall_man_text)
                hall_man_text = hall_man_text.replace(',', '\n      ')
            except:
                pass
            if len(syuzai_list) != 0:
                for syuzai_str in syuzai_list:
                    syuzai = syuzai_str.text
                    if syuzai.find('旧イベ') != 0:
                        if syuzai.find('ナビ子') != 0:
                            syuzai = syuzai.replace('編集部', '').replace('(', ' ').replace(')', '').replace('P-WORLD引用', '').replace('DMM', '').replace('スロット取材', '').replace('天草ヤスヲの', '').replace('ステーション', '').replace('予想人数多い', '').replace('\n', '').replace(' ', '')
                            if syuzai in ['周年日', '新台入替', '新台入替 ']:
                                continue
                                #context += '\n' + '　☆'+ syuzai
                            print(tenpo_name)
                            print(syuzai)
                            syuzai_name_list.append(syuzai)
                            tenpo_name_list.append(tenpo_name)
                            syuzai_dict[tenpo_name] = syuzai
                            if syuzai == 'ホールサーチマン ':
                                context += '\n\n' + '　☆' + syuzai + '\n' + '　　┗' + hall_man_text
                                record = pd.Series([tenpo_name, syuzai, syuzai, hall_man_text], index=tokyou_syuzai_df.columns)
                                tokyou_syuzai_df = tokyou_syuzai_df.append(record, ignore_index=True)
                                continue

                            elif syuzai == 'ホールサーチマン赤枠':
                                context += '\n\n' + '　☆' + 'ホールサーチマン  赤枠' + '\n' + '　　┗' + hall_man_text
                                record = pd.Series([tenpo_name, 'ホールサーチマン', syuzai, hall_man_text], index=tokyou_syuzai_df.columns)
                                tokyou_syuzai_df = tokyou_syuzai_df.append(record, ignore_index=True)
                                continue

                            elif syuzai == 'ホールサーチマン金枠':
                                context += '\n\n' + '　☆' + 'ホールサーチマン  金枠' + '\n' + '　　┗' + hall_man_text
                                record = pd.Series([tenpo_name, 'ホールサーチマン', syuzai, hall_man_text], index=tokyou_syuzai_df.columns)
                                tokyou_syuzai_df = tokyou_syuzai_df.append(record, ignore_index=True)
                                continue

                            elif syuzai == 'ホールサーチマンレインボー枠':
                                context += '\n\n' + '　☆' + 'ホールサーチマン  レインボー枠' + '\n' + '　　┗' + hall_man_text
                                record = pd.Series([tenpo_name, 'ホールサーチマン', syuzai, hall_man_text], index=tokyou_syuzai_df.columns)
                                tokyou_syuzai_df = tokyou_syuzai_df.append(record, ignore_index=True)
                                print(hall_man_text)
                                continue

                            elif syuzai == '熱盛アンケート':
                                context += '\n\n' + '　☆' + syuzai + '\n' + '　　┗' + hall_man_text
                                record = pd.Series([tenpo_name, 'ホールサーチマン', syuzai, hall_man_text], index=tokyou_syuzai_df.columns)
                                tokyou_syuzai_df = tokyou_syuzai_df.append(record, ignore_index=True)
                                print(hall_man_text)
                                continue

                            for row in df.itertuples():
                                if row[1] == syuzai:
                                    record = pd.Series([tenpo_name, str(row[2]), syuzai, str(row[3])], index=tokyou_syuzai_df.columns)
                                    tokyou_syuzai_df = tokyou_syuzai_df.append(record, ignore_index=True)
                                    context += '\n\n' + '　☆' + syuzai + '　【' + str(row[2]) + '】' + '\n' + '　　┗' + str(row[3])
                                    break
                                # else:
                                    # record = pd.Series([tenpo_name,str(row[2]),syuzai,str(row[3])], index=tokyou_syuzai_df.columns)
                                    # tokyou_syuzai_df = tokyou_syuzai_df.append(record, ignore_index=True)
                                    # context += '\n' + '　☆'+ syuzai + '　【'+ str(row[2]) + '】' + '\n' + '　　┗' + str(row[3])
                                    # break

                            if row[1] != syuzai:
                                context += '\n\n' + '　☆' + syuzai + '\n' + '　　┗' + '未調査'
                                record = pd.Series([tenpo_name, '未調査', syuzai, '未調査'], index=tokyou_syuzai_df.columns)
                                tokyou_syuzai_df = tokyou_syuzai_df.append(record, ignore_index=True)
                                chousa_syuzai.append(syuzai)

                            else:
                                record = pd.Series([tenpo_name, 'テスト', syuzai, 'テスト'], index=tokyou_syuzai_df.columns)

        tokyou_syuzai_df['syuzai'] = tokyou_syuzai_df['syuzai'].map(convert_string)
        tokyou_syuzai_df['tenpo_name'] = tokyou_syuzai_df['tenpo_name'].map(tenpo_convert_string)
        tokyou_syuzai_df_defalut = tokyou_syuzai_df = tokyou_syuzai_df.sort_values('syuzai')
        tokyou_syuzai_df_defalut
        baitai_list = ['スロパチ', '天草ヤスヲ', 'ホールサーチマン', 'ホール攻略', 'Gooパチ', 'パチスロ必勝本', 'スクープTV', 'ジャンバリ', '一撃_DMM', '一撃', 'アツ姫', '爆ガチ！']

        for baitai in baitai_list:
            context = f'''{h1_text} 取材まとめ'''
            image_context = f'{h1_text} 媒体別まとめ'
            todoufuken = h1_text.split('  ')[0]

            tokyou_syuzai_df_a = tokyou_syuzai_df_nokori = tokyou_syuzai_df_defalut[tokyou_syuzai_df_defalut['baitai'] == baitai]
            # display(tokyou_syuzai_df_a)
            tokyou_syuzai_df = tokyou_syuzai_df[tokyou_syuzai_df['baitai'] != baitai]
            previous_syuzai = ''
            #print('\n'  ,baitai)
            for syuzai in tokyou_syuzai_df_a.itertuples():
                print(syuzai)
            # syuzai_list.append(syuzai)
                if syuzai[1] != previous_syuzai:
                    #print('\n\n■',syuzai[1],'\n   ★',syuzai[3],'\n   ┗',syuzai[4],sep='')
                    context += '\n■' + str(syuzai[1]) + '\n    ★' + str(syuzai[3]) + '\n    ┗' + str(syuzai[4]) + '\n'
                    previous_syuzai = syuzai[1]
                else:
                    print('未調査！！！！', syuzai)
                    context += '\n    ★' + str(syuzai[3]) + '  【' + str(syuzai[2]) + '】' + '\n   ┗' + str(syuzai[4]) + '\n'
                    previous_syuzai = syuzai[1]
                    pass
                    pass
                    #print('   ★',syuzai[3],'\n   ┗',syuzai[4],sep='')

            length = context.count('\n')
            if length == 0:
                context = F'''{h1_text} 取材まとめ
                
                取材予定はありませんでした'''
                length = 4
            recommend_image(context, length)

            im1 = Image.open(win_path + f'{baitai}.jpg')
            im2 = Image.open(win_path + f'eva_board_{tomorrow_url}.jpg')
            get_concat_v(im1, im2).save(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai}.jpg')
            os.remove(win_path + f'eva_board_{tomorrow_url}.jpg')

        image_context = f'{h1_text} 取材まとめ'
        for syuzai in tokyou_syuzai_df.itertuples():
            print(syuzai)
            # syuzai_list.append(syuzai)
            if syuzai[1] != previous_syuzai:
                #print('\n\n■',syuzai[1],'\n   ★',syuzai[3],'\n   ┗',syuzai[4],sep='')
                image_context += '\n■' + str(syuzai[1]) + '\n    ★' + str(syuzai[3]) + ' 【' + str(syuzai[2]) + '】' + '\n    ┗' + str(syuzai[4]) + '\n'
                previous_syuzai = syuzai[1]
            else:
                print('未調査！！！！', syuzai)
                image_context += '\n    ★' + str(syuzai[3]) + ' 【' + str(syuzai[2]) + '】' + '\n    ┗' + str(syuzai[4]) + '\n'
                previous_syuzai = syuzai[1]
                pass
                #print('   ★',syuzai[3],'\n   ┗',syuzai[4],sep='')

            length = image_context.count('\n')
            if length == 0:
                image_context = F'''{h1_text} 取材まとめ
                
                取材予定はありませんでした'''
                length = 4
        recommend_image(image_context, length)

        im1 = Image.open(win_path + f'未調査.jpg')
        im2 = Image.open(win_path + f'eva_board_{tomorrow_url}.jpg')
        get_concat_v(im1, im2).save(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_未調査.jpg')
        #os.remove(win_path + f'eva_board_{tomorrow_url}.jpg')

        im1 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_スロパチ.jpg')
        im2 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_天草ヤスヲ.jpg')
        im3 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_ホールサーチマン.jpg')
        im4 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_ホール攻略.jpg')

        get_concat_h_multi_blank([im1, im2]).save(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_天草ヤスヲ_スロパチ_ホール_ホールサーチマン_ホール攻略.jpg')

        im1 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_Gooパチ.jpg')
        im2 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_パチスロ必勝本.jpg')
        im3 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_アツ姫.jpg')
        im4 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_爆ガチ！.jpg')

        get_concat_h_multi_blank([im1, im2, im3, im4]).save(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_Gooパチ_パチスロ必勝本_アツ姫_爆ガチ！.jpg')

        im1 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_ジャンバリ.jpg')
        im2 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_スクープTV.jpg')
        im3 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_一撃.jpg')
        im4 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_一撃_DMM.jpg')

        get_concat_h_multi_blank([im1, im2, im3, im4]).save(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_ジャンバリ_スクープTV_一撃_一撃_DMM.jpg')

        for number in [0, 4, 8]:
            im1 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai_list[number+0]}.jpg')
            im2 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai_list[number+1]}.jpg')
            get_concat_h_blank(im1, im2, (0, 64, 128)).save(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai_list[number+0]}_{baitai_list[number+1]}.jpg')

            im3 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai_list[number+2]}.jpg')
            im4 = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai_list[number+3]}.jpg')
            get_concat_h_blank(im3, im4, (0, 64, 128)).save(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai_list[number+2]}_{baitai_list[number+3]}.jpg')

            im1_ = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai_list[number+0]}_{baitai_list[number+1]}.jpg')
            im2_ = Image.open(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_{baitai_list[number+2]}_{baitai_list[number+3]}.jpg')

            get_concat_v(im1_, im2_).save(win_path + f'eva_board_{todoufuken}_{tomorrow_url}_comleted_{number}.jpg')

        for number in [0, 4, 8]:
            imgPath = win_path + f'eva_board_{todoufuken}_{tomorrow_url}_comleted_{number}.jpg'
            output_path = imgPath.replace(win_path + 'eva_board_', '')
            upload_image(imgPath, output_path)

        # Swin_path+'eva_board_千葉県_2021-04-13_未調査.jpg
        imgPath = win_path + f'eva_board_{todoufuken}_{tomorrow_url}_未調査.jpg'
        output_path = imgPath.replace(win_path + 'eva_board_', '')
        upload_image(imgPath, output_path)

        baitai_list = ['スロパチ', '天草ヤスヲ', 'ホールサーチマン', 'ホール攻略', 'Gooパチ', 'パチスロ必勝本', 'スクープTV', 'ジャンバリ', '一撃_DMM', '一撃', 'アツ姫', '爆ガチ！']

        for baitai in baitai_list:
            try:
                value = baitai_coutnt_dict[f'{baitai}']
                print(baitai, value, '件')
            except:
                print(baitai, '0')

        print('その他媒体・未調査')
        tokyou_syuzai_df['baitai'].value_counts().sum()

        todoufuken_kanji = h1_text.split('  ')[0]
        string_date = h1_text.split('  ')[1]
        string_date_only = string_date.split('(')[0]

        wp_context_1 = f'''<h2>{todoufuken_kanji}　パチンコ・スロット イベント 取材まとめ・オススメ店舗</h2>'''

        if text_1.count('\n') > 2:
            wp_context_1 += f'<a href="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/syuzai_report_{todoufuken_kanji}_{tomorrow_url}_1.jpg"><img src="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/syuzai_report_{todoufuken_kanji}_{tomorrow_url}_1.jpg" alt="{todoufuken}_{tomorrow_url}_パチンコ・パチスロ_イベント" class="alignnone size-full " /></a>'
        if text_2.count('\n') > 2:
            wp_context_1 += f'<a href="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/syuzai_report_{todoufuken_kanji}_{tomorrow_url}_2.jpg"><img src="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/syuzai_report_{todoufuken_kanji}_{tomorrow_url}_2.jpg" alt="{todoufuken}_{tomorrow_url}_パチンコ・パチスロ_イベント" class="alignnone size-full " /></a>'
        if text_3.count('\n') > 2:
            wp_context_1 += f'<a href="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/syuzai_report_{todoufuken_kanji}_{tomorrow_url}_3.jpg"><img src="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/syuzai_report_{todoufuken_kanji}_{tomorrow_url}_3.jpg" alt="{todoufuken}_{tomorrow_url}_パチンコ・パチスロ_イベント" class="alignnone size-full " /></a>'
        if text_4.count('\n') > 2:
            wp_context_1 += f'<a href="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/syuzai_report_{todoufuken_kanji}_{tomorrow_url}_4.jpg"><img src="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/syuzai_report_{todoufuken_kanji}_{tomorrow_url}_4.jpg" alt="{todoufuken}_{tomorrow_url}_パチンコ・パチスロ_イベント" class="alignnone size-full " /></a>'

        wp_context_2 = f'''[su_spoiler title="{todoufuken_kanji}の媒体毎の画像まとめ一覧" style="fancy" icon="chevron-circle" anchor="Hello" open="yes" ]
        <a href="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/{todoufuken}_{tomorrow_url}_comleted_0.jpg"><img src="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/{todoufuken}_{tomorrow_url}_comleted_0.jpg" alt="{todoufuken}_{tomorrow_url}_パチンコ・パチスロ_イベント" class="alignnone size-full " /></a>

        <a href="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/{todoufuken}_{tomorrow_url}_comleted_4.jpg"><img src="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/{todoufuken}_{tomorrow_url}_comleted_4.jpg" alt="{todoufuken}_{tomorrow_url}_パチンコ・パチスロ＿イベント"  class="alignnone size-full " /></a>

        <a href="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/{todoufuken}_{tomorrow_url}_comleted_8.jpg"><img src="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/{todoufuken}_{tomorrow_url}_comleted_8.jpg" alt="{todoufuken}_{tomorrow_url}_パチンコ・パチスロ_イベント" " class="alignnone size-full " /></a>

        <a href="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/{todoufuken}_{tomorrow_url}_未調査.jpg"><img src="http://slotana777.com/wp-content/uploads/{today.strftime("%Y/%m")}/{todoufuken}_{tomorrow_url}_未調査.jpg" alt="{todoufuken}_{tomorrow_url}_未調査_パチンコ・パチスロ" " class="alignnone size-full " /></a>
        [/su_spoiler]'''

        wp_context = wp_context_1 + wp_context_2

        baitai_list_error = ['スロパチ', '天草ヤスヲ', 'ホールサーチマン', 'ホール攻略', 'Gooパチ', 'パチスロ必勝本', 'スクープTV', 'ジャンバリ', '一撃_DMM', '一撃', 'アツ姫', '爆ガチ！']

        sumnail_text = ''
        # sumnail_len_list =
        tokyou_syuzai_df = tokyou_syuzai_df_defalut = tokyou_syuzai_df_defalut.sort_values(['tenpo_name', 'syuzai'])
        for baitai, error_baitai in zip(baitai_list, baitai_list_error):

            tokyou_syuzai_df_a = tokyou_syuzai_df_defalut[tokyou_syuzai_df_defalut['baitai'] == baitai]
            len_syuzai = len(tokyou_syuzai_df_a)

            # display(tokyou_syuzai_df_a)
            if len(tokyou_syuzai_df_a) != 0:
                # print('\n■',baitai,sep='')
                wp_context += '<h3>' + string_date_only + ' ' + todoufuken_kanji + ' スロット ' + baitai + '</h3>' + f'\n<img src="http://slotana777.com/wp-content/uploads/2021/04/{error_baitai}.jpg" alt="{error_baitai} タイトル画像" width="1000" height="400" class="alignnone size-full " />\n'
            else:
                pass

            past_syuzai = ''
            past_syuzai_name = ''

            for df_row in tokyou_syuzai_df_a.itertuples():
                # print(syuzai)

                if df_row[1] != past_syuzai:
                    if df_row[3] != past_syuzai_name:
                        if 'ホールサーチマン' == df_row[2]:
                            wp_context += '\n<h4>' + df_row[3] + '</h4>\n<h5>🟥公約　' + 'HPに三機種掲載されてる台が狙い目\n(※対象機種は上部の要まとめ画像参照)' + '</h5>\n・' + f'{df_row[1]}'
                        else:
                            # <a href="https://www.google.co.jp/search?q=サントロペ横須賀中央" target="_blank" rel="noopener">サントロペ横須賀中央</a>
                            wp_context += '\n<h4>' + df_row[3] + '</h4>\n<h5>🟥公約　' + df_row[4] + '</h5>\n・' + f'{df_row[1]}'
                    else:
                        wp_context += '\n・' + f'{df_row[1]}'

                past_syuzai = df_row[1]
                past_syuzai_name = df_row[3]

        wp_context += '\n<h3>パチンコ・スロット その他取材・未調査取材</h3>\n\n&nbsp; \n&nbsp; ' + image_context
        tenpo_only_text = wp_context.split('■')
        print(wp_context)
        wp_completed_footer += wp_context


    wp_completed_text_header = f'''[st-kaiwa1]【{string_date}】神奈川・埼玉・千葉　パチンコパチスロ　明日のホールイベント取材まとめ記事です。
    \nイベントの公約に基づき、高設定が投入される可能性が高いと予想されるホールを中心に公約内容も一緒にわかりやすく明日のイベントのある店舗を紹介しています。
    \n毎日更新されますので是非、ブックマークお願いします。[/st-kaiwa1]'''

    wp_completed_text_compted = wp_completed_text_header + wp_completed_footer


    if os.name == 'nt':
        font_path = r"C:\Windows\Fonts\ラノベPOP.otf"
    elif os.name == 'posix':
        font_path = "font/LightNovelPOPv2.otf"
    # def recommend_image(todouhuken,write_image_context):
    # image_path = r"C:\Users\81801\Desktop\twitter_anarytics_bot\recommend_syuzai_report\board_image.jpg" #win
    # image_path = win_path+'sumnail.png" #mac
    # image = Image.open(image_path)
    # draw = ImageDraw.Draw(image)


    # サムネイル

    # サムネイル作成

    # def recommend_image(todouhuken,write_image_context):
    # image_path = r"C:\Users\81801\Desktop\twitter_anarytics_bot\recommend_syuzai_report\board_image.jpg" #win
    image_path = win_path + '千葉.jpg'  # mac
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    write_image_context = f'''　　{string_date}
    埼玉・神奈川・千葉
    明日の取材まとめ'''


    font_path = r"font/LightNovelPOPv2.otf"
    # "font/LightNovelPOPv2.otf"
    # font/LightNovelPOPv2.otf

    # sizeは文字サイズです（とりあえず適当に50）
    font = ImageFont.truetype(font_path, size=180)

    # 文字を描く
    # 最初の(0,0)は文字の描画を開f始する座標位置です　もちろん、(10,10)などでもOK
    # fillはRGBで文字の色を決めています
    draw.multiline_text((155, 190), write_image_context, fill=(255, 255, 255), font=font, spacing=50, stroke_width=5, stroke_fill=(55, 55, 55))


    image.save(win_path + f'kantou_syuzaireport_{tomorrow_url}.jpg')
    # 元画像を読み込んでくる
    #write_image_context =f
    # image.save(win_path+f'{tenpo_name}_{tomorrow_str_tweet}.png")
    # 元画像を読み込んでくる

    # フォントを指定する（フォントファイルはWindows10ならC:\\Windows\\Fontsにあります）
    # フォントの読み込


    # sizeは文字サイズです（とりあえず適当に50）

    # 文字を描く
    # 最初の(0,0)は文字の描画を開f始する座標位置です　もちろん、(10,10)などでもOK
    # fillはRGBで文字の色を決めています

    sumnail_path = win_path + f'kantou_syuzaireport_{tomorrow_url}.jpg'


    # Set URL, ID, Password
    WORDPRESS_ID = "tsc953u"
    WORDPRESS_PW = "6tjc5306"
    WORDPRESS_URL = "https://slotana777.com/xmlrpc.php"
    wp = Client(WORDPRESS_URL, WORDPRESS_ID, WORDPRESS_PW)

    # for i in range(1,4):
    #     imgPath = win_path+f'heatmap/tokyo_heatmap_{tenpo_name}_{date_list[0]}_{i}.jpg'
    #     upload_image(imgPath, imgPath)
    #     time.sleep(1)


    # import


    # Picture file name & Upload
    imgPath = sumnail_path
    media_id = upload_image(imgPath, imgPath)

    # Blog Title

    title = f"【{string_date}】埼玉・神奈川・千葉　パチンコスロットイベント取材まとめ【関東】 "
    # Blog Content (html)
    body = f'''
    {wp_completed_text_compted}
    '''

    # publish or draft
    status = "publish"

    # Category keyword
    cat1 = '埼玉・神奈川・千葉 スロットイベントまとめ・オススメ店舗'
    cat2 = ''
    cat3 = ''

    # Tag keyword
    tag1 = f'{string_date[-4]}のつく日'
    tag2 = f'イベント取材まとめ'
    tag3 = f'スロット'
    tag4 = f'{tomorrow_url}'

    slug = f"kantou_syuzaireport_{tomorrow_url}"

    # Post
    post = WordPressPost()
    post.title = title
    post.content = body
    post.post_status = status
    post.terms_names = {
        "category": [cat1],
        "post_tag": [tag1, tag2, tag3, tag4],
    }
    post.slug = slug

    # Set eye-catch image

    post.thumbnail = media_id

    # Post Time
    #post.date = datetime.datetime.now() - datetime.timedelta(hours=9)

    wp.call(NewPost(post))
    print('記事書き込み完了')
    post_line(f'{tomorrow}分がブログ投稿完了')
except Exception as e:
    post_line(f'{tomorrow}分ブログ投稿失敗\n{e}')
