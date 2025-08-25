import streamlit as st
import pandas as pd

st.set_page_config(page_title="互動式報表查詢", layout="wide")

# 1. 設定你的 Google Sheets CSV 連結
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1CzTqb7TRRCE_uroXbEE_rVmbm0WzgbXtwwpo8PZIXrc/export?format=csv"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(GSHEET_CSV_URL)
    return df

def main():
    st.title("Google Sheet 即時資料查詢")

    df = load_data()

    st.sidebar.header("篩選條件")

    # 假設 Google Sheet 有 '日期' 欄位，先轉格式
    if '日期' in df.columns:
        df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
        start, end = st.sidebar.date_input("日期範圍",
                                           [df['日期'].min(), df['日期'].max()])
        mask = df['日期'].between(start, end)
        df = df.loc[mask]

    # 加入一個通用的欄位篩選功能
    key_col = st.sidebar.selectbox("選擇篩選欄位", options=[col for col in df.columns if df[col].nunique() < 50], index=0)
    selected = st.sidebar.multiselect(f"篩選 {key_col}", options=df[key_col].dropna().unique())
    if selected:
        df = df[df[key_col].isin(selected)]

    st.write(f"目前顯示：共 {len(df)} 筆資料")

    st.dataframe(df)

    # 如果有數值欄位，顯示圖表
    numeric_cols = df.select_dtypes(include='number').columns
    if len(numeric_cols) > 0:
        chart_col = st.selectbox("選擇數值欄位畫圖", options=numeric_cols)
        st.line_chart(df.set_index('日期')[chart_col] if '日期' in df.columns else df[chart_col])

if __name__ == "__main__":
    main()
