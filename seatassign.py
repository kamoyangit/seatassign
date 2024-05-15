import streamlit as st
import random
from datetime import datetime, timedelta
import pickle
import os
import pytz
from PIL import Image
from pathlib import Path

# 日本のタイムゾーンを指定
jst = pytz.timezone('Asia/Tokyo')

# 画像ファイル名
default_image_filename = 'AAA.png'
private_image_filename = 'BBB.png'

# 最大座席数
max_seats = 15

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
    new_max_seats = st.number_input("最大座席数を入力して下さい", min_value=2, max_value=1000, value=seats['seatsnum'], step=1)
    if st.button("座席数の更新"):
        # Bugfix
        # タイムゾーンを指定する
        current_date = datetime.now(jst).date()
        if seats['seatsnum'] > new_max_seats:
            seats = {'date': current_date, 'seatsnum': new_max_seats,'assigned': []}
        else:
            seats['seatsnum'] = new_max_seats
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
        # 指定した番号の席の割り当てを開放する
        st.write(f'指定した座席割り当て席の番号を開放します')
        delete_seat = st.selectbox(
            '開放する席の番号',
            (seats["assigned"]))
        # st.write('開放する席の番号', delete_seat)
        if st.button('座席を開放する'):
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
            else:
                st.error(f'開放する席はありません')
    
        # イメージのアップロード処理
        st.divider()
        image_uploader()

        # 座席数の更新処理
        st.divider()
        max_seats_update()

        # デバッグ用：昨日の日付を管理ファイルに書き込むボタン
        st.divider()
        st.write(f'デバッグ用')
        if st.button("昨日の日付を書き込む"):
            seats = load_state()
            # 現在の日付情報を取得
            # current_date = datetime.now().date()
            current_date = datetime.now(jst).date()
            current_max_seats = seats['seatsnum']
            # 1日前の日付情報を計算
            yesterday = current_date - timedelta(days=1)
            seats = {'date': yesterday, 'seatsnum': current_max_seats,'assigned': seats['assigned']}
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
        st.write(f'指定した座席割り当て席の番号を開放します')
        delete_seat = st.selectbox(
            '開放する席の番号',
            (seats["assigned"]))
        # st.write('開放する席の番号', delete_seat)
        if st.button('座席を開放する'):
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
            else:
                st.error(f'開放する席はありません')

def main():
    # アプリのタイトル表示
    st.title('座席割り当てアプリ')

    if check_password():
        seats = load_state()
        if seats is None:
            total_seats = max_seats
        else:
            total_seats = seats['seatsnum']

        # 日付が変わったら、座席をリセット
        # current_date = datetime.now().date()
        # タイムゾーンを指定する
        current_date = datetime.now(jst).date()
        current_max_seats = total_seats
        if seats is None or seats['date'] != current_date:
            seats = {'date': current_date, 'seatsnum': current_max_seats,'assigned': []}
            # フェールセーフ
            save_state(seats) 

        # 座席図の表示
        # st.image('AAA.png', caption='座席割り当て図', width=300)
        if Path(private_image_filename).exists():
            st.image(private_image_filename, caption='座席割り当て図', width=300)
        else:
            st.image(default_image_filename, caption='座席割り当て図', width=300)
        
        # 注意の文言
        st.write(f'＜座席割り当てボタン＞は、1回だけ押してください')

        if st.button('座席割り当てボタン'):
            # フェールセーフ
            seats = load_state()
            total_seats = seats['seatsnum']
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if available_seats:
                assigned_seat = random.choice(available_seats)
                seats['assigned'].append(assigned_seat)
                st.success(f'あなたの座席番号は ＜ {assigned_seat} ＞ です。')
                save_state(seats)
            else:
                st.error('空きの座席はありません。')

        st.write(f'現在の割り当て座席数: {len(seats["assigned"])}  ／  残り座席数: {total_seats - len(seats["assigned"])}')
        # st.write(f'{current_date}')

        # デバッグ用：割り当てられた座席のリストを表示
        # st.write('割り当てられた座席: ', seats['assigned'])

        st.divider()
        release_seats()

        st.divider()
        admin_main()

if __name__ == "__main__":
    main()
