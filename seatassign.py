import streamlit as st
import random
from datetime import datetime, timedelta
import pickle
import os
import pytz
from PIL import Image, ImageDraw
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

# 日本のタイムゾーンを指定
jst = pytz.timezone('Asia/Tokyo')

# 画像ファイル名
default_image_filename = 'AAA.png'
private_image_filename = 'BBB.png'

# 最大座席数
max_seats = 12
max_seats_nd = 4    # 10以下

# ディスプレイのある座席の座標
rectParams = (  '200,159,27,23'
              , '200,268,27,23'
              , '167,104,27,23'
              , '167,159,27,23'
              , '167,268,27,23'
              , '122,131,27,23'
              , '122,186,27,23'
              , '122,294,27,23'
              , '197,375,27,23'
              , '167,445,27,23'
              , '125,372,27,23'
              , '124,452,27,23')

# ディスプレイのない座席の座標
rectParamsND = ('200,211,27,23'
              , '168,211,27,23'
              , '122,237,27,23'
              , '167,362,27,23')

# ディスプレイのない座席の名前
nameND = ['A','B','C','D','E','F','G','H','I','J']

# パスワードの確認
def check_password():
    # 環境変数を取得
    PASSWD = os.environ.get('PASS_KEY')

    password = st.text_input("パスワードを入力してください", type="password")
    if password == PASSWD:
        return True
    else:
        return False

# パスワードの確認
def check_password2():
    # 環境変数を取得
    PASSWD2 = os.environ.get('PASS_KEY')

    password2 = st.text_input("座席開放用（誤って複数座席を取得した場合は、不要な座席を開放して下さい）", type="password")
    if password2 == PASSWD2:
        return True
    else:
        return False

def load_state():
    try:
        with open('seats.pkl', 'rb') as f:
            seats = pickle.load(f)
    except (EOFError, FileNotFoundError):
        seats = None
    return seats

def save_state(seats):
    with open('seats.pkl', 'wb') as f:
        pickle.dump(seats, f)

def image_uploader():
    # 画像ファイルのアップローダー
    uploaded_file = st.file_uploader("画像ファイル(BBB.png)を選択して下さい", type=['png'])

    # ファイルがアップロードされた場合、画像を表示
    if uploaded_file is not None:
        # PILを使用して画像を読み込み
        image = Image.open(uploaded_file)
    
        # Streamlitで画像を表示
        # st.image(image, caption='アップロードされた画像', use_column_width=True)

        # 保存先のディレクトリを指定
        save_path = '.'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
    
        # 保存するファイル名を指定（オリジナルのファイル名を使用）
        file_path = os.path.join(save_path, uploaded_file.name)
    
        # 画像を保存
        image.save(file_path)
    
        # 保存したことをユーザーに通知
        # st.success(f"画像が保存されました: {file_path}")
        st.success(f"画像を保存しました")

def max_seats_update():
    seats = load_state()
    new_max_seats = st.number_input("最大座席数【ディスプレイ付】を入力して下さい  \nただし、12以下の数字にして下さい", min_value=2, max_value=12, value=seats['seatsnum'], step=1)
    if st.button("座席数の更新【ディスプレイ付】"):
        # Bugfix
        # タイムゾーンを指定する
        current_date = datetime.now(jst).date()
        if seats['seatsnum'] > new_max_seats:
            seats = {'date': current_date, 'seatsnum': new_max_seats,'assigned': []}
        else:
            seats['seatsnum'] = new_max_seats
        save_state(seats)

def max_seats_nd_update():
    seats = load_state()
    new_max_seats_nd = st.number_input("最大座席数【ディスプレイなし】を入力して下さい  \nただし、4以下の数字にして下さい", min_value=2, max_value=4, value=seats['seatsnum_nd'], step=1)
    if st.button("座席数の更新【ディスプレイなし】"):
        # Bugfix
        # タイムゾーンを指定する
        current_date = datetime.now(jst).date()
        if seats['seatsnum_nd'] > new_max_seats_nd:
            seats = {'date': current_date, 'seatsnum_nd': new_max_seats_nd,'assigned_nd': []}
        else:
            seats['seatsnum_nd'] = new_max_seats_nd
        save_state(seats)

# Adminパスワードの確認
def check_password_admin():
    # 環境変数を取得
    PASSWDADMIN = os.environ.get('ADMIN_KEY')

    passwordadmin = st.text_input("管理者用（一般ユーザの方はこの機能は使わないで下さい）", type="password")
    if passwordadmin == PASSWDADMIN:
        return True
    else:
        return False

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

        delete_seat = st.selectbox(
            '開放する席の番号（ディスプレイ有り）',
            (seats["assigned"]))
        # st.write('開放する席の番号', delete_seat)
        if st.button('【Admin】座席を開放する  \n（ディスプレイ有り）'):
            # フェールセーフ
            seats = load_state()
            total_seats = seats['seatsnum']
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if delete_seat in seats['assigned']:
                seats['assigned'].remove(delete_seat)
                available_seats.append(delete_seat)
                available_seats = list(set(available_seats))
                st.success(f'座席番号 {delete_seat} を開放しました。')
                save_state(seats)
                # Auto Refresh
                st_autorefresh(interval=2000, limit=2, key="fizzbuzzcounter")
            else:
                st.error(f'開放する席はありません')
        
        delete_seat_nd = st.selectbox(
            '開放する席の番号（ディスプレイ無し）  \n”ABCD”は、”1234”と読み替えて下さい',
            (seats["assigned_nd"]))
        # st.write('開放する席の番号', delete_seat)
        if st.button('【Admin】座席を開放する  \n（ディスプレイ無し）'):
            # フェールセーフ
            seats = load_state()
            total_seats = seats['seatsnum_nd']
            available_seats_nd = list(set(range(1, total_seats_nd + 1)) - set(seats['assigned_nd']))
            if delete_seat_nd in seats['assigned_nd']:
                seats['assigned_nd'].remove(delete_seat_nd)
                available_seats_nd.append(delete_seat_nd)
                available_seats_nd = list(set(available_seats_nd))
                st.success(f'座席番号 {nameND[int(delete_seat_nd)-1]} を開放しました。')
                save_state(seats)
                # Auto Refresh
                st_autorefresh(interval=2000, limit=2, key="fizzbuzzcounter")
            else:
                st.error(f'開放する席はありません')
    
        # イメージのアップロード処理
        st.divider()
        image_uploader()

        # 座席数の更新処理
        st.divider()
        max_seats_update()
        max_seats_nd_update()

        # デバッグ用：昨日の日付を管理ファイルに書き込むボタン
        st.divider()
        st.write(f'デバッグ用')
        if st.button("昨日の日付を書き込む"):
            seats = load_state()
            # 現在の日付情報を取得
            # current_date = datetime.now().date()
            current_date = datetime.now(jst).date()
            current_max_seats = seats['seatsnum']
            current_max_seats_nd = seats['seatsnum_nd']
            # 1日前の日付情報を計算
            yesterday = current_date - timedelta(days=1)
            seats = {'date': yesterday, 'seatsnum': current_max_seats,'assigned': seats['assigned'], 'seatsnum_nd': current_max_seats_nd,'assigned_nd': seats['assigned_nd']}
            st.write(f'書き込んだ日付は{yesterday}')
            save_state(seats)

def release_seats():
    if check_password2():
        seats = load_state()
        if seats is None:
             st.write(f'管理対象のデータがありません')
             return
        total_seats = seats['seatsnum']
        # 指定した番号の席の割り当てを開放する
        st.write(f'指定した座席番号を開放します')

        st.divider()
        delete_seat = st.selectbox(
            '開放する席【ディスプレイ有り】の番号',
            (seats["assigned"]))
        # st.write('開放する席の番号', delete_seat)
        if st.button('座席を開放する  \n【ディスプレイ有り】'):
            # フェールセーフ
            seats = load_state()
            total_seats = seats['seatsnum']
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if delete_seat in seats['assigned']:
                seats['assigned'].remove(delete_seat)
                available_seats.append(delete_seat)
                available_seats = list(set(available_seats))
                st.success(f'座席番号 {delete_seat} を開放しました。')
                save_state(seats)
                # Auto Refresh
                # st_autorefresh(interval=2000, limit=2, key="fizzbuzzcounter")
            else:
                st.error(f'開放する席はありません')

        st.divider()
        delete_seat_nd = st.selectbox(
            '開放する席【ディスプレイ無し】の番号  \n”ABCD”は、”1234”と読み替えて下さい',
            (seats["assigned_nd"]))
        # st.write('開放する席の番号', delete_seat)
        if st.button('座席を開放する  \n【ディスプレイなし】'):
            # フェールセーフ
            seats = load_state()
            total_seats_nd = seats['seatsnum_nd']
            available_seats_nd = list(set(range(1, total_seats_nd + 1)) - set(seats['assigned_nd']))
            if delete_seat_nd in seats['assigned_nd']:
                seats['assigned_nd'].remove(delete_seat_nd)
                available_seats_nd.append(delete_seat_nd)
                available_seats_nd = list(set(available_seats_nd))
                st.success(f'座席番号 {nameND[int(delete_seat_nd)-1]} を開放しました。')
                save_state(seats)
                # Auto Refresh
                # st_autorefresh(interval=2000, limit=2, key="fizzbuzzcounter")
            else:
                st.error(f'開放する席はありません')

# 矩形座標のパラメータの前処理
def drowRRectangle(params):
    # 矩形の位置とサイズを指定
    rect_params = (params)
    rect_params = [int(param) for param in rect_params.split(',')]
    # width/heightを正しく代入する処理を追加
    rect_params[2] = rect_params[0] + rect_params[2]
    rect_params[3] = rect_params[1] + rect_params[3]
    return rect_params

def main():
    # アプリのタイトル表示
    st.title('座席割当アプリ(V2)')

    if check_password():
        seats = load_state()
        if seats is None:
            total_seats = max_seats
            total_seats_nd = max_seats_nd
        else:
            total_seats = seats['seatsnum']
            total_seats_nd = seats['seatsnum_nd']

        # 日付が変わったら、座席をリセット
        # current_date = datetime.now().date()
        # タイムゾーンを指定する
        current_date = datetime.now(jst).date()
        current_max_seats = total_seats
        current_max_seats_nd = total_seats_nd
        if seats is None or seats['date'] != current_date:
            seats = {'date': current_date, 'seatsnum': current_max_seats,'assigned': [], 'seatsnum_nd': current_max_seats_nd,'assigned_nd': []}
            # フェールセーフ
            save_state(seats) 

        # 座席図の表示
        # st.image('AAA.png', caption='座席割り当て図', width=300)
        if Path(private_image_filename).exists():
            st.image(private_image_filename, caption='座席割当図', width=300)
        else:
            # st.image(default_image_filename, caption='座席割り当て図', width=300)
            # デフォルトイメージを使用する場合の処理
            img = Image.open(default_image_filename)
            # 矩形を描画
            draw = ImageDraw.Draw(img)
            # ディスプレイ有りの席に対する処理
            for rect in seats['assigned']:
                rect_params = drowRRectangle(rectParams[int(rect)-1])
                draw.rectangle(rect_params, outline="red", width=3)
            # ディスプレイ無しの席に対する処理
            for rect in seats['assigned_nd']:
                rect_params = drowRRectangle(rectParamsND[int(rect)-1])
                draw.rectangle(rect_params, outline="blue", width=3)
            # 画像と矩形を表示
            st.image(img, caption='座席割当図', width=300)
        
        # 注意の文言
        st.write(f'＜座席割当ボタン＞は、1回だけ押してください')

        st.divider()
        if st.button('座席割当ボタン  \n【ディスプレイ有り】'):
            # フェールセーフ
            seats = load_state()
            total_seats = seats['seatsnum']
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if available_seats:
                assigned_seat = random.choice(available_seats)
                seats['assigned'].append(assigned_seat)
                st.success(f'あなたの座席番号は ＜ {assigned_seat} ＞ です。')
                save_state(seats)
                # Auto Refresh
                # st_autorefresh(interval=2000, limit=2, key="fizzbuzzcounter")
            else:
                st.error('空きの座席はありません。')

        st.write(f'現在の割当座席数: {len(seats["assigned"])}  ／  残り座席数: {total_seats - len(seats["assigned"])}')
        # st.write(f'{current_date}')

        st.divider()
        if st.button('座席割当ボタン  \n【ディスプレイ無し】'):
            # フェールセーフ
            seats = load_state()
            total_seats_nd = seats['seatsnum_nd']
            available_seats_nd = list(set(range(1, total_seats_nd + 1)) - set(seats['assigned_nd']))
            if available_seats_nd:
                assigned_seat_nd = random.choice(available_seats_nd)
                seats['assigned_nd'].append(assigned_seat_nd)
                st.success(f'あなたの座席番号は ＜ {nameND[int(assigned_seat_nd)-1]} ＞ です。')
                save_state(seats)
                # Auto Refresh
                # st_autorefresh(interval=2000, limit=2, key="fizzbuzzcounter")
            else:
                st.error('空きの座席はありません。')

        st.write(f'現在の割当座席数: {len(seats["assigned_nd"])}  ／  残り座席数: {total_seats_nd - len(seats["assigned_nd"])}')

        # デバッグ用：割り当てられた座席のリストを表示
        # st.write('割り当てられた座席: ', seats['assigned'])

        st.divider()
        release_seats()

        st.divider()
        admin_main()

if __name__ == "__main__":
    main()
