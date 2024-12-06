import streamlit as st
import json
import datetime
import os
import pytz

from utils import check_password3

STATE_FILE = "app_state.json"

default_state = {
    "arrays": ['鴨川', '西岡', '林', '工藤','小村', '佐々木', '袖山', '田中', '畑', '町野', '藤田', '松崎', '丸山', '市原', '今村', '柿本', '須藤'],
    "current_week": 0,
    "last_update": None
}

def create_initial_state_file():
    """初期状態のJSONファイルを生成する"""
    with open(STATE_FILE, 'w') as f:
        json.dump(default_state, f, indent=4)  # indentで読みやすく整形

def save_state(state):
    # last_update を文字列に変換
    state_copy = state.copy()  # 元の辞書をコピーして変更を元の辞書に反映させない
    state_copy["last_update"] = state_copy["last_update"].isoformat() if state_copy["last_update"] else None
    with open(STATE_FILE, 'w') as f:
        json.dump(state_copy, f, indent=4)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try:
                loaded_state = json.load(f)
                if loaded_state["last_update"]:
                    loaded_state["last_update"] = datetime.date.fromisoformat(loaded_state["last_update"])
                return loaded_state
            except json.JSONDecodeError:
                st.error("状態ファイルの読み込みに失敗しました。初期状態を使用します。")
                return default_state
    else:
        create_initial_state_file()
        return default_state

def increment_week(state):
    """現在の週を1つ進める"""
    state["current_week"] = (state["current_week"] + 1) % len(state["arrays"])
    return state

def decrement_week(state):
    """現在の週を1つ戻す"""
    state["current_week"] = (state["current_week"] - 1) % len(state["arrays"])
    return state

def check_and_update_week(state, today):
    """毎週月曜日に週を進めるチェックを行い、必要に応じて更新"""
    last_update = state.get("last_update")
    if last_update:
        # 前回の更新日と今日の日付が異なる週であれば、increment_weekを呼ぶ
        if last_update.isocalendar()[1] != today.isocalendar()[1]:
            state = increment_week(state)
    state["last_update"] = today
    return state

# 初期化状態を記録
@st.cache_data
def is_initialized():
    return False  # 初回起動時のみFalseを返す

app_state = load_state()
arrays = app_state["arrays"]
current_week = app_state["current_week"]
# today = datetime.date.today()
# 一旦UTCを計算して、JSTに変換して、本日の日付を取得する
# --------------------
utc_now = datetime.datetime.now(datetime.timezone.utc)
japan_tz = pytz.timezone('Asia/Tokyo')
japan_time = utc_now.astimezone(japan_tz)
today = japan_time.date()
# --------------------
# 初回ロード時に更新を確認
# if "initial_load" not in st.session_state:
#     st.session_state.initial_load = True
#     app_state = check_and_update_week(app_state, today)
#     save_state(app_state)
# 初期化フラグを確認
if not is_initialized():
    # 初期化処理を実行
    app_state = check_and_update_week(app_state, today)
    save_state(app_state)
    # キャッシュを更新して初期化済みを記録
    is_initialized = lambda: True
# --------------------
# 表示内容
# current_week = app_state["current_week"]

'''
st.write(f"今週の当番: {arrays[current_week]}")

if st.button("ひとつ進める"):
    app_state = increment_week(app_state)
    save_state(app_state)
    st.rerun()

if st.button("ひとつ戻す"):
    app_state["current_week"] = (app_state["current_week"] - 1) % len(arrays)
    save_state(app_state)
    st.rerun()
'''

# 最後に今日の日付で更新
app_state["last_update"] = today
save_state(app_state)

# ------------------
# 外部からコールする関数
# ------------------
# 当番の名前を返す関数
def get_on_duty():
    app_state = load_state()
    # --------------------
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    japan_tz = pytz.timezone('Asia/Tokyo')
    japan_time = utc_now.astimezone(japan_tz)
    today = japan_time.date()
    app_state = check_and_update_week(app_state, today)
    save_state(app_state)
    # --------------------
    current_week = app_state["current_week"]
    return arrays[current_week]

# 現在時刻を返す関数
def get_current_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    japan_tz = pytz.timezone('Asia/Tokyo')
    japan_time = utc_now.astimezone(japan_tz)
    return japan_time

# 座席を開放する関数
def change_on_duty():
    if check_password3():
        inc_dec_on_duty()

# ダイアログを表示する
@st.dialog("当番の修正")
def inc_dec_on_duty():
    # 当番の表示
    st.write(f"今週の郵便当番: {get_on_duty()} : {get_current_time()}")
    # 一週分進める
    if st.button("ひとつ進める"):
        app_state = load_state()
        app_state = increment_week(app_state)
        save_state(app_state)
        st.rerun()
    # 一週分戻す
    if st.button("ひとつ戻す"):
        app_state = load_state()
        app_state = decrement_week(app_state)
        save_state(app_state)
        st.rerun()
