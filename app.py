
import streamlit as st
from io import BytesIO
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

def fetch_stock_data(stock_code: str) -> pd.DataFrame:
    df = pd.DataFrame(columns=['日付', '終値', '前週比率', '売買単価', '売買高(株)', '売り残(株)', '買い残(株)', '信用倍率'])
    page = 1

    while True:
        url = f"https://s.kabutan.jp/stocks/{stock_code}/historical_prices/margin/?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tr_elements = soup.find_all('tr')
        data_list = []

        for tr in tr_elements:
            th_element = tr.find('th', class_='sticky')
            if th_element:
                th_text = th_element.text
                td_texts = [td.text.replace(',', '') for td in tr.find_all('td')]
                row_data = [th_text] + td_texts
                data_list.append(row_data)

        if not data_list:
            break

        if len(data_list) > 3:
            df = pd.concat([df, pd.DataFrame(data_list[3:], columns=df.columns)], ignore_index=True)

        page += 1

    for col in df.columns:
        if col != '日付':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def plot_stock_data(df: pd.DataFrame) -> BytesIO:
    fig, ax = plt.subplots(figsize=(10, 6))
    dates = df['日付']
    for col in df.columns[1:]:
        plt.plot(dates, df[col], label=col)

    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('Stock Data')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

# Streamlit UI
st.title("株式信用倍率ビジュアライザー")

stock_code = st.text_input("株コードを4桁で入力してください（例：7203）", "")

if stock_code and len(stock_code) == 4 and stock_code.isdigit():
    with st.spinner("データを取得中..."):
        try:
            df = fetch_stock_data(stock_code)
            if df.empty:
                st.warning("データが見つかりませんでした。")
            else:
                st.subheader("📋 データテーブル")
                st.dataframe(df)

                st.subheader("📈 グラフ表示")
                img_buf = plot_stock_data(df)
                st.image(img_buf, caption="Stock Data", use_column_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
else:
    st.info("株コードを4桁で入力してください。")
