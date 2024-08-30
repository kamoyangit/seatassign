import streamlit as st
import random

# おみくじの結果と顔文字の辞書
omikuji_results = {
    "大吉": "大吉 😊",
    "中吉": "中吉 😌",
    "小吉": "小吉 🙂"
}

# ダイアログを表示する
@st.dialog("今日運勢")
def omikuji_button_disp():
    # セッションステートを初期化
    if 'count' not in st.session_state:
        st.session_state.count = 0
    st.session_state.count += 1
    result = random.choice(list(omikuji_results.keys()))
    message = f"結果は、 {omikuji_results[result]} です！"

    # countは、閉じる時にもカウントアップされる・・・    
    if st.session_state.count == 1:
        message += " 知らんけど。"
    elif st.session_state.count == 3:
        message += " 何度も、引かんといて。"
    elif st.session_state.count == 5:
        message += " ええ加減にして。"
    elif st.session_state.count > 5:
        message = "えーい、もう、凶じゃ！😭"
    st.write(message)
    if st.button("閉じる"):
        st.rerun()