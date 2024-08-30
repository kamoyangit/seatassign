import streamlit as st
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from utils import check_password_admin, load_state, save_state, image_uploader, drowRRectangle, alphabet_position, generate_alphabets, check_password2
import pytz

# 日本のタイムゾーンを指定
jst = pytz.timezone('Asia/Tokyo')

# 画像ファイル名
default_image_filename = 'AAA.png'
private_image_filename = 'BBB.png'

# 矩形座標のパラメータの前処理
rectParams = ('200,159,27,23', '200,268,27,23', '167,104,27,23', '167,159,27,23', '167,268,27,23', '122,131,27,23', '122,186,27,23', '122,294,27,23', '197,375,27,23', '167,445,27,23', '125,372,27,23', '124,452,27,23')
rectParamsND = ('200,211,27,23', '168,211,27,23', '122,237,27,23', '167,362,27,23')

# 最大座席数を更新
def max_seats_update():
    seats = load_state()
    new_max_seats = st.number_input("最大座席数【モニタ有り】を入力して下さい  \nただし、12以下の数字にして下さい", min_value=2, max_value=12, value=seats['seatsnum'], step=1)
    if st.button("座席数の更新【モニタ有り】"):
        current_date = datetime.now(jst).date()
        if seats['seatsnum'] > new_max_seats:
            seats = {'date': current_date, 'seatsnum': new_max_seats, 'assigned': []}
        else:
            seats['seatsnum'] = new_max_seats
        save_state(seats)

# 最大座席数【ディスプレイなし】を更新
def max_seats_nd_update():
    seats = load_state()
    new_max_seats_nd = st.number_input("最大座席数【モニタなし】を入力して下さい  \nただし、4以下の数字にして下さい", min_value=2, max_value=4, value=seats['seatsnum_nd'], step=1)
    if st.button("座席数の更新【モニタなし】"):
        current_date = datetime.now(jst).date()
        if seats['seatsnum_nd'] > new_max_seats_nd:
            seats = {'date': current_date, 'seatsnum_nd': new_max_seats_nd, 'assigned_nd': []}
        else:
            seats['seatsnum_nd'] = new_max_seats_nd
        save_state(seats)

# 座席割当図の描画【ディスプレイ有り】
@st.dialog("座席確認")
def approve_button_disp(num):
    st.success(f'{num}')
    img = Image.open(default_image_filename)
    draw = ImageDraw.Draw(img)
    rect_params = drowRRectangle(rectParams[num-1])
    draw.rectangle(rect_params, outline="red", width=3)
    st.image(img, caption='座席割当図', width=300)
    # （右上の❎で閉じるようにする）
    # st.markdown('## ポップアップ画面は、右上の x で閉じてください ##')
    # ボタンで閉じると前の描画が実行されてNG(Ver1.38.0からOK)
    if st.button("確認しました"):
        st.rerun()

# 座席割当図の描画【ディスプレイなし】
@st.dialog("座席確認")
def approve_button_nodisp(num):
    st.success(f'{num}')
    img = Image.open(default_image_filename)
    draw = ImageDraw.Draw(img)
    rect = alphabet_position(num)
    rect_params = drowRRectangle(rectParamsND[rect-1])
    draw.rectangle(rect_params, outline="blue", width=3)
    st.image(img, caption='座席割当図', width=300)
    # （右上の❎で閉じるようにする）
    # st.markdown('## ポップアップ画面は、右上の x で閉じてください ##')
    # ボタンで閉じると前の描画が実行されてNG(Ver1.38.0からOK)
    if st.button("確認しました"):
        st.rerun()

# 管理者用のメイン関数
def admin_main():
    if check_password_admin():
        st.divider()
        seats = load_state()
        if seats is None:
            st.write(f'管理対象のデータがありません')
            return
        total_seats = seats['seatsnum']
        total_seats_nd = seats['seatsnum_nd']

        # 指定した番号の席の割り当てを開放する
        st.write(f'指定した座席番号を開放します')
        delete_seat = st.selectbox('開放する席の番号（モニタ有り）', (seats["assigned"]))
        if st.button('【Admin】座席を開放する  \n（モニタ有り）'):
            seats = load_state()
            total_seats = seats['seatsnum']
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if delete_seat in seats['assigned']:
                seats['assigned'].remove(delete_seat)
                available_seats.append(delete_seat)
                available_seats = list(set(available_seats))
                st.success(f'座席番号 {delete_seat} を開放しました。')
                save_state(seats)

        delete_seat_nd = st.selectbox('開放する席の番号（モニタなし）', (seats["assigned_nd"]))
        if st.button('【Admin】座席を開放する  \n（モニタなし）'):
            seats = load_state()
            total_seats = seats['seatsnum_nd']
            available_seats_nd = list(set(range(1, total_seats_nd + 1)) - set(seats['assigned_nd']))
            if delete_seat_nd in seats['assigned_nd']:
                seats['assigned_nd'].remove(delete_seat_nd)
                available_seats_nd.append(delete_seat_nd)
                available_seats_nd = list(set(available_seats_nd))
                st.success(f'座席番号 {delete_seat_nd} を開放しました。')
                save_state(seats)

        st.divider()
        image_uploader()

        st.divider()
        max_seats_update()
        max_seats_nd_update()

        st.divider()
        st.write(f'デバッグ用')
        if st.button("昨日の日付を書き込む"):
            seats = load_state()
            current_date = datetime.now(jst).date()
            current_max_seats = seats['seatsnum']
            current_max_seats_nd = seats['seatsnum_nd']
            yesterday = current_date - timedelta(days=1)
            seats = {'date': yesterday, 'seatsnum': current_max_seats, 'assigned': seats['assigned'], 'seatsnum_nd': current_max_seats_nd, 'assigned_nd': seats['assigned_nd']}
            st.write(f'書き込んだ日付は{yesterday}')
            save_state(seats)

# 座席を開放する関数
def release_seats():
    if check_password2():
        seats = load_state()
        if seats is None:
            st.write(f'管理対象のデータがありません')
            return
        total_seats = seats['seatsnum']
        st.write(f'指定した座席番号を開放します')

        st.divider()
        delete_seat = st.selectbox('開放する席【モニタ有り】の番号', (seats["assigned"]))
        if st.button('座席を開放する  \n【モニタ有り】'):
            seats = load_state()
            total_seats = seats['seatsnum']
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if delete_seat in seats['assigned']:
                seats['assigned'].remove(delete_seat)
                available_seats.append(delete_seat)
                available_seats = list(set(available_seats))
                st.success(f'座席番号 {delete_seat} を開放しました。')
                save_state(seats)

        st.divider()
        delete_seat_nd = st.selectbox('開放する席【モニタなし】の番号 ', (seats["assigned_nd"]))
        if st.button('座席を開放する  \n【モニタなし】'):
            seats = load_state()
            total_seats_nd = seats['seatsnum_nd']
            available_seats_nd = list(set(range(1, total_seats_nd + 1)) - set(seats['assigned_nd']))
            if delete_seat_nd in seats['assigned_nd']:
                seats['assigned_nd'].remove(delete_seat_nd)
                available_seats_nd.append(delete_seat_nd)
                available_seats_nd = list(set(available_seats_nd))
                st.success(f'座席番号 {delete_seat_nd} を開放しました。')
                save_state(seats)
