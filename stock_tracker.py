import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Function to fetch stock data
def fetch_stock_data(stock_symbol):
    url = f"https://finance.yahoo.com/quote/{stock_symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Failed to retrieve data for {stock_symbol}")
        return None

# Function to parse stock data
def parse_stock_data(html_content, stock_symbol):
    soup = BeautifulSoup(html_content, "html.parser")
    price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})
    change_tag = soup.find("fin-streamer", {"data-field": "regularMarketChange"})
    volume_tag = soup.find("fin-streamer", {"data-field": "regularMarketVolume"})
    if price_tag and change_tag and volume_tag:
        price = float(price_tag.text.replace(',', ''))
        change = float(change_tag.text.replace('(', '').replace(')', '').replace(',', ''))
        volume = int(volume_tag.text.replace(',', ''))
        # Convert volume to a readable format
        if volume == 0:
            volume_str = "0"
        elif volume >= 10**7:
            volume_str = f"{volume / 10**7:.2f} Cr"
        elif volume >= 10**5:
            volume_str = f"{volume / 10**5:.2f} L"
        elif volume >= 10**3:
            volume_str = f"{volume / 10**3:.2f} K"
        else:
            volume_str = str(volume)
        return {
            "symbol": stock_symbol,
            "price": round(price, 2),
            "change": round(change, 2),
            "volume": volume_str
        }
    else:
        st.error(f"Failed to find the stock data for {stock_symbol}")
        return None

# Function to get stock details
def get_stock_details(stock_symbol):
    html_content = fetch_stock_data(stock_symbol)
    if html_content:
        return parse_stock_data(html_content, stock_symbol)
    return None

# Function to fetch stock symbol using Yahoo Finance API
def fetch_stock_symbol(company_name):
    search_url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "quotes" in data and len(data["quotes"]) > 0:
            return data["quotes"][0]["symbol"]
    return None

# Streamlit app layout
st.set_page_config(page_title="Stock Tracker 🚀", layout="centered")
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .title {
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
    }
    .subheader {
        color: #34495e;
    }
    table {
        font-size: larger;
    }
    thead th {
        font-weight: bold;
        background-color: #2c3e50;
        color: white;
        font-size: 16px;
    }
    tbody td {
        font-weight: normal;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("<h1 class='title'>Stock Insights Dashboard 📈</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='subheader'>Get real-time stock price updates</h2>", unsafe_allow_html=True)

# Form to handle user input
with st.form(key='input_form', clear_on_submit=True):
    company_input = st.text_input("Enter company names separated by commas", "", placeholder="E.g., Apple, Google, Microsoft")
    submit_button = st.form_submit_button(label='Fetch Data')

# Form submission
if submit_button:
    company_names = [c.strip() for c in company_input.split(',')]
    data = []
    for company in company_names:
        stock_symbol = fetch_stock_symbol(company)
        if stock_symbol:
            stock_details = get_stock_details(stock_symbol)
            if stock_details:
                data.append(stock_details)
        else:
            st.warning(f"Could not find stock symbol for {company}")

    # Creation of table and plots
    if data:
        df = pd.DataFrame(data)
        st.markdown("<h3>Stock Details</h3>", unsafe_allow_html=True)
        
        # Styling DataFrame as HTML
        html_table = df.to_html(index=False, classes=["dataframe", "table", "table-bordered", "table-hover"])
        st.markdown(html_table, unsafe_allow_html=True)

        # Create plot
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Bar(x=df['symbol'], y=df['price'], name='Price'))
        fig.add_trace(go.Bar(x=df['symbol'], y=df['change'], name='Change'))
        #fig.add_trace(go.Bar(x=df['symbol'], y=df['volume'], name='Volume'))
        fig.update_layout(barmode='group', title='Stock Prices and Changes')
        st.plotly_chart(fig)
