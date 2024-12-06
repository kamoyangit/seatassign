import streamlit as st
from datetime import datetime
from pathlib import Path
import pytz
from PIL import Image, ImageDraw

import random

from utils import check_password, load_state, save_state, drowRRectangle, generate_alphabets, alphabet_position
from seats import max_seats_update, max_seats_nd_update, release_seats, admin_main, approve_button_disp, approve_button_nodisp
from omikuji import omikuji_button_disp
from topic import topicToday_button_disp

from daytext import get_on_duty, change_on_duty

# 日本のタイムゾーンを指定
jst = pytz.timezone('Asia/Tokyo')

# 画像ファイル名
default_image_filename = 'AAA.png'
private_image_filename = 'BBB.png'

# 矩形座標のパラメータの前処理
rectParams = ('200,159,27,23', '200,268,27,23', '167,104,27,23', '167,159,27,23', '167,268,27,23', '122,131,27,23', '122,186,27,23', '122,294,27,23', '197,375,27,23', '167,445,27,23', '125,372,27,23', '124,452,27,23', '200,104,27,23')
rectParamsND = ('200,211,27,23', '168,211,27,23', '122,237,27,23', '167,362,27,23')

# 最大座席数
max_seats = 13
max_seats_nd = 4    # 10以下

def main():
    # アプリのタイトル表示
    st.title('座席ガチャ(V4.4.1)')

    if check_password():
        seats = load_state()
        if seats is None:
            total_seats = max_seats
            total_seats_nd = max_seats_nd
        else:
            total_seats = seats['seatsnum']
            total_seats_nd = seats['seatsnum_nd']

        # 日付が変わったら、座席をリセット
        current_date = datetime.now(jst).date()
        current_max_seats = total_seats
        current_max_seats_nd = total_seats_nd
        if seats is None or seats['date'] != current_date:
            seats = {'date': current_date, 'seatsnum': current_max_seats, 'assigned': [], 'seatsnum_nd': current_max_seats_nd, 'assigned_nd': []}
            # フェールセーフ
            save_state(seats)
        
        # ====================================================
        # 3つのカラムを作成
        col1, col2, col3 = st.columns(3)
        # ====================================================
        with col1:
            # おみくじボタンの機能
            if st.button("【おみくじ】を引く", key="omikuji_button"):
                omikuji_button_disp()
        # ====================================================
        with col2:
            # 今日のトピックの機能
            if st.button("【今日は何の日】", key="topic_button"):
                topicToday_button_disp()
        # ====================================================
        with col3:
            # 当番の表示
            st.write(f"今週の郵便当番：{get_on_duty()}さん")
        # ====================================================

        # 座席図の表示
        if Path(private_image_filename).exists():
            st.image(private_image_filename, caption='座席割当図', width=300)
        else:
            img = Image.open(default_image_filename)
            draw = ImageDraw.Draw(img)
            for rect in seats['assigned']:
                rect_params = drowRRectangle(rectParams[int(rect)-1])
                draw.rectangle(rect_params, outline="red", width=3)
            for rect in seats['assigned_nd']:
                rect = alphabet_position(rect)
                rect_params = drowRRectangle(rectParamsND[int(rect)-1])
                draw.rectangle(rect_params, outline="blue", width=3)
            st.image(img, caption='座席割当図', width=300)
        
        # 注意の文言
        st.write(f'＜座席割当ボタン＞は、1回だけ押してください')

        if st.button('座席割当ボタン  \n【モニタ有り】'):
            # フェールセーフ
            seats = load_state()
            total_seats = seats['seatsnum']
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if available_seats:
                assigned_seat = random.choice(available_seats)
                seats['assigned'].append(assigned_seat)
                approve_button_disp(assigned_seat)
                st.success(f'あなたの座席番号は ＜ {assigned_seat} ＞ です。')
                save_state(seats)
            else:
                st.error('空きの座席はありません。')

        st.write(f'割当座席数: {len(seats["assigned"])}  ／  残り座席数: {total_seats - len(seats["assigned"])}')

        st.divider()
        if st.button('座席割当ボタン  \n【モニタ無し】'):
            # フェールセーフ
            seats = load_state()
            total_seats_nd = seats['seatsnum_nd']
            available_seats_nd = list(set(generate_alphabets(total_seats_nd)) - set(seats['assigned_nd']))
            if available_seats_nd:
                assigned_seat_nd = random.choice(available_seats_nd)
                seats['assigned_nd'].append(assigned_seat_nd)
                approve_button_nodisp(assigned_seat_nd)
                st.success(f'あなたの座席番号は ＜ {assigned_seat_nd} ＞ です。')
                save_state(seats)
            else:
                st.error('空きの座席はありません。')

        st.write(f'割当座席数: {len(seats["assigned_nd"])}  ／  残り座席数: {total_seats_nd - len(seats["assigned_nd"])}')

        st.divider()
        release_seats()

        st.divider()
        change_on_duty()

        st.divider()
        admin_main()

if __name__ == "__main__":
    main()
