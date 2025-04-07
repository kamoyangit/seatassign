import streamlit as st
import requests
import json
import os

# Google Apps ScriptのURLをここに入力
GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyON58GOpyND-PZZ5NH5FG7uKtqvW0mIwk76TEn0aDiGKTSrbs-FZ3lOxH4mtvB0fwx/exec"  # ここにウェブアプリのURLを貼り付けてください。

def read_json_data():
    try:
        # 環境変数を取得
        SECRET_TOKEN = os.environ.get('PASS_KEY')
        params = {"operation": "read", "token": SECRET_TOKEN}
        response = requests.get(GOOGLE_APPS_SCRIPT_URL, params=params)
        response.raise_for_status()  # エラーレスポンスを検出
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error reading data: {e}")
        return None


def write_json_data(data):
    try:
        # 環境変数を取得
        SECRET_TOKEN = os.environ.get('PASS_KEY')
        params = {"operation": "write", "token": SECRET_TOKEN}
        response = requests.post(GOOGLE_APPS_SCRIPT_URL,
                                params=params,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps(data))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error writing data: {e}")
        return None

# ================================================================================
# 2025/04/07
# JSONファイルを作成する場合は、このgasFile.pyを使って、
# 必要な要素を「Key」と「Value」を個別に入力して、JSONファイルを作成すること
# JSONファイルを一般のエディタ等で編集すると、不正なJSONファイルとして扱われ、正しく動作しない
# ================================================================================
def main():
    st.title("JSON File Manager")

    if "json_data" not in st.session_state:
      st.session_state.json_data = {}

    if st.button("Read JSON"):
        data = read_json_data()
        if data:
            st.session_state.json_data = data
            st.write("Data loaded:")
            st.json(data)
        else:
            st.write("Failed to load data")
    

    # JSONデータを編集
    st.subheader("Edit JSON Data")
    key = st.text_input("Key")
    value = st.text_input("Value")
    
    if st.button("Add/Update"):
        if key:
            st.session_state.json_data[key] = value
            st.write("Updated data:")
            st.json(st.session_state.json_data)

    if st.button("Save JSON"):
       if st.session_state.json_data:
          result = write_json_data(st.session_state.json_data)
          if result:
              st.success("Successfully saved!")
              st.write(result)
          else:
              st.error("Failed to save")
       else:
          st.write("No data to save.")


if __name__ == "__main__":
    main()