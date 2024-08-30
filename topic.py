import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import pytz

# 日本のタイムゾーンを指定
jst = pytz.timezone('Asia/Tokyo')

# API-KEYを環境変数より取得
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# モデルの指定
model = genai.GenerativeModel('gemini-1.5-flash')

# 質問内容の文面
request_text = "は何の日か調べて、200文字以内で簡単な記事を作成してください"

# ダイアログを表示する
@st.dialog("TOPIC by Google-Gemini")
def topicToday_button_disp():
    # 今日は何の日かの情報をGeminiより取得
    month = datetime.now(jst).date().month
    day = datetime.now(jst).date().day
    response = model.generate_content(str(month) + "月" + str(day) + "日" + request_text)
    st.write(response.text)
    if st.button("だいたい、解りました"):
        st.rerun()