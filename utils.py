import streamlit as st
import pickle
import os
from PIL import Image

# 新しい保存メソッド用
import requests
import base64

GAS_BASE_URL = "https://script.google.com/macros/s/AKfycbzUx2ECkHeXnZbtcbJUxbTmsBBQVlkhaiBCInGXfVEQhjUTi0jJKgArIz1mZoqyIJBSuw/exec"  # 例: https://script.google.com/macros/s/AKf.../exec

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

# パスワードの確認
def check_password3():
    # 環境変数を取得
    PASSWD3 = os.environ.get('PASS_KEY')
    password3 = st.text_input("郵便当番修正（当番がずれた場合には修正して下さい）", type="password")
    if password3 == PASSWD3:
        return True
    else:
        return False

# Adminパスワードの確認
def check_password_admin():
    # 環境変数を取得
    PASSWDADMIN = os.environ.get('ADMIN_KEY')
    passwordadmin = st.text_input("管理者用（一般ユーザの方はこの機能は使わないで下さい）", type="password")
    if passwordadmin == PASSWDADMIN:
        return True
    else:
        return False

# 状態のロード
def load_state():
    # ローカル保存用の古いコード
    '''
    try:
        with open('seats.pkl', 'rb') as f:
            seats = pickle.load(f)
    except (EOFError, FileNotFoundError):
        seats = None
    return seats
    '''
    # 新しい保存メソッド用
    # 環境変数を取得
    SECRET_TOKEN = os.environ.get('PASS_KEY')
    params = {"token": SECRET_TOKEN}
    response = requests.get(GAS_BASE_URL, params={"token": SECRET_TOKEN})
    if not response.ok:
        st.error(f"HTTPエラー: {response.status_code}")
        return None
    if not response.text.isascii():
        st.error(f"GAS応答にASCII以外が含まれています: {response.text}")
        return None
    if response.text in ["INVALID_TOKEN", "FILE_NOT_FOUND"]:
        st.error(f"GASエラー: {response.text}")
        return None
    # 問題なければデコード
    data = base64.b64decode(response.text)
    seats = pickle.loads(data)
    return seats

# 状態のセーブ
def save_state(seats):
    # ローカル保存用の古いコード
    '''
    with open('seats.pkl', 'wb') as f:
        pickle.dump(seats, f)
    '''
    # 新しい保存メソッド用
    # 環境変数を取得
    SECRET_TOKEN = os.environ.get('PASS_KEY')
    data = pickle.dumps(seats)
    encoded = base64.b64encode(data).decode("utf-8")
    params = {"token": SECRET_TOKEN}
    response = requests.post(GAS_BASE_URL, params=params, data=encoded)
    return response.text

# 画像ファイルのアップローダー
def image_uploader():
    uploaded_file = st.file_uploader("画像ファイル(BBB.png)を選択して下さい", type=['png'])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        save_path = '.'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file_path = os.path.join(save_path, uploaded_file.name)
        image.save(file_path)
        st.success(f"画像を保存しました")

# 矩形座標のパラメータの前処理
def drowRRectangle(params):
    rect_params = (params)
    rect_params = [int(param) for param in rect_params.split(',')]
    rect_params[2] = rect_params[0] + rect_params[2]
    rect_params[3] = rect_params[1] + rect_params[3]
    return rect_params

# アルファベットの生成
def generate_alphabets(n):
    alphabets = []
    for i in range(n):
        alphabet = chr(65 + i % 26)
        alphabets.append(alphabet)
    return alphabets

# アルファベットの位置を取得
def alphabet_position(letter):
    letter = letter.upper()
    position = ord(letter) - ord('A') + 1
    return position
