import streamlit as st
import random
from datetime import datetime, timedelta
import pickle
import os
import pytz

# 日本のタイムゾーンを指定
jst = pytz.timezone('Asia/Tokyo')

# パスワードの確認
def check_password():
    # 環境変数を取得
    PASSWD = os.environ.get('PASS_KEY')

    password = st.text_input("パスワードを入力してください", type="password")
    if password == PASSWD:
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

# Adminパスワードの確認
def check_password_admin():
    # 環境変数を取得
    PASSWDADMIN = os.environ.get('ADMIN_KEY')

    passwordadmin = st.text_input("管理者用", type="password")
    if passwordadmin == PASSWDADMIN:
        return True
    else:
        return False

def admin_main():
    if check_password_admin():
        total_seats = 15  # 例として座席数を15に設定
        seats = load_state()
        if seats == None:
            return
        # 指定した番号の席の割り当てを開放する
        st.write(f'指定した座席割り当て席の番号を開放します')
        delete_seat = st.selectbox(
            '開放する席の番号',
            (seats["assigned"]))
        # st.write('開放する席の番号', delete_seat)
        if st.button('座席を開放する'):
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if delete_seat in seats['assigned']:
                seats['assigned'].remove(delete_seat)
                available_seats.append(delete_seat)
                available_seats = list(set(available_seats))
                st.success(f'座席番号 {delete_seat} を開放しました。')
                save_state(seats)
            else:
                st.error(f'開放する席はありません')
    
    # デバッグ用：昨日の日付を管理ファイルに書き込むボタン
        st.write(f'---------')
        st.write(f'デバッグ用')
        if st.button("昨日の日付を書き込む"):
            seats = load_state()
            # 現在の日付情報を取得
            # current_date = datetime.now().date()
            current_date = datetime.now(jst).date()
            # 1日前の日付情報を計算
            yesterday = current_date - timedelta(days=1)
            seats = {'date': yesterday, 'assigned': seats['assigned']}
            st.write(f'書き込んだ日付は{yesterday}')
            save_state(seats)

def main():
    # アプリのタイトル表示
    st.title('座席割り当てアプリ')

    if check_password():
        total_seats = 15  # 例として座席数を15に設定
        seats = load_state()

        # 日付が変わったら、座席をリセット
        # current_date = datetime.now().date()
        # タイムゾーンを指定する
        current_date = datetime.now(jst).date()
        if seats is None or seats['date'] != current_date:
            seats = {'date': current_date, 'assigned': []}

        # 座席図の表示
        st.image('AAA.png', caption='座席割り当て図', width=300)
        
        # 注意の文言
        st.write(f'座席割り当てのボタンは1回だけ押してください')

        if st.button('座席を割り当てる'):
            available_seats = list(set(range(1, total_seats + 1)) - set(seats['assigned']))
            if available_seats:
                assigned_seat = random.choice(available_seats)
                seats['assigned'].append(assigned_seat)
                st.success(f'あなたの座席番号は {assigned_seat} です。')
                save_state(seats)
            else:
                st.error('空きの座席はありません。')

        st.write(f'現在割り当てられた座席数: {len(seats["assigned"])}')
        st.write(f'残り座席数: {total_seats - len(seats["assigned"])}')
        st.write(f'{current_date}')

        # デバッグ用：割り当てられた座席のリストを表示
        # st.write('割り当てられた座席: ', seats['assigned'])

        st.write(f'---------')
        admin_main()

if __name__ == "__main__":
    main()
