import streamlit as st
import random
from datetime import datetime
import pickle
import os

# パスワードの確認
def check_password():
    password = st.text_input("パスワードを入力してください", type="password")
    if password == "dih2024":
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

def main():
    # アプリのタイトル表示
    st.title('座席割り当てアプリ')

    if check_password():
        total_seats = 15  # 例として座席数を15に設定
        seats = load_state()

        # 日付が変わったら、座席をリセット
        current_date = datetime.now().date()
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

        # デバッグ用：割り当てられた座席のリストを表示
        # st.write('割り当てられた座席: ', seats['assigned'])

if __name__ == "__main__":
    main()
