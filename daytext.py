import streamlit as st
import json
import datetime
import os
import pytz

from utils import check_password3

# save_state, load_stateに加えて、クラウドアクセス用のread_file_JSON, update_file_JSON
from gasFile import read_json_data, write_json_data

STATE_FILE = "app_state.json"
EXIST_FLAG = False

default_state = {
    # "arrays": ['鴨川', '西岡', '林', '工藤','小村', '佐々木', '袖山', '田中', '畑', '町野', '藤田', '松崎', '丸山', '市原', '今村', '柿本', '須藤'],
    "arrays": ['鴨川', '西岡', '林', '工藤','小村', '袖山', '田中(佐)', '畑', '松崎', '丸山', '市原', '今村', '須藤', '大平', '田中(来)', '浜野', '木村', '加瀬谷'],
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
    # state_copy["last_update"] = state_copy["last_update"].isoformat() if state_copy["last_update"] else None
    # ==============================================================
    # last_update が存在する場合の処理
    if "last_update" in state_copy:
        value = state_copy["last_update"]

        if isinstance(value, datetime.date):
            # datetime オブジェクトなら isoformat に変換
            state_copy["last_update"] = value.isoformat()
        elif isinstance(value, str):
            try:
                # 文字列なら datetime にパース可能か確認
                datetime.datetime.fromisoformat(value)  # パース可能な形式か検証
                # 問題ないのでそのまま保持
            except ValueError:
                # 無効な形式の場合はエラーを投げる、または適切に処理
                raise ValueError(f"Invalid ISO8601 string: {value}")
        else:
            # それ以外の型の場合は None を設定
            state_copy["last_update"] = None
    # ==============================================================
    with open(STATE_FILE, 'w') as f:
        json.dump(state_copy, f, indent=4)

def load_state():
    global EXIST_FLAG
    if os.path.exists(STATE_FILE):
        EXIST_FLAG = True
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
        EXIST_FLAG = False
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

def save_to_server(state):
    """現在の週の情報を保存する"""
    state["current_week"] = int(state["current_week"])
    # ===================================================
    # 同期を取るため、サーバにアクセスする
    # 例えば、state["last_update"] が datetime.date 型の場合
    if isinstance(state.get("last_update"), datetime.date):
        state["last_update"] = str(state["last_update"])
    write_json_data(state)
    # ===================================================

def check_and_update_week(state, today):
    """毎週月曜日に週を進めるチェックを行い、必要に応じて更新"""
    last_update_str = state.get("last_update")
    # "last_update"の型の差異を吸収するための処理
    if last_update_str:
        try:
            # last_update が str 型の場合は datetime.date 型に変換
            if isinstance(last_update_str, str):
                last_update = datetime.datetime.strptime(last_update_str, "%Y-%m-%d").date()
            elif isinstance(last_update_str, datetime.date):
                last_update = last_update_str
            else:
                raise ValueError("Invalid type for last_update")
                
            # 前回の更新日と今日の日付が異なる週であれば、increment_weekを呼ぶ
            if last_update.isocalendar()[1] != today.isocalendar()[1]:
                state = increment_week(state)  # 元の state を更新
                # 登録日付を更新する（2025/04/14）
                state['last_update'] = today
                save_to_server(state)
            
        except ValueError as e:
            # エラーログを出力
             print(f"Error processing last_update: {e}")

    # state["current_week"] = str(state["current_week"])        
    return state

# 初期化状態を記録
@st.cache_data
def is_initialized():
    return False # 初回起動時のみFalseを返す


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
# 初期化フラグを確認（最初の起動された場合、アプリ自体が完全に再起動された場合：毎週月曜日）
if not is_initialized():
    # 初期化処理を実行(EXIST_FLAGが、Falseの場合には、アプリ自体が再起動されているケース)
    if EXIST_FLAG == False:
        # サーバにアクセスして、保存データを取得する
        app_state = read_json_data()
    # 週が新しくなったかどうかをチェックし、新しくなっていれば更新する
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
    # return arrays[current_week]
    return arrays[int(current_week)]

# 現在時刻を返す関数
def get_current_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    japan_tz = pytz.timezone('Asia/Tokyo')
    japan_time = utc_now.astimezone(japan_tz)
    return japan_time

# 当番を変更する関数
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
        save_to_server(app_state)
        st.rerun()
    # 一週分戻す
    if st.button("ひとつ戻す"):
        app_state = load_state()
        app_state = decrement_week(app_state)
        save_state(app_state)
        save_to_server(app_state)
        st.rerun()
