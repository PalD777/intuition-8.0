import yfinance as yf
import os
from flask import Flask, request, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from pretty_html_table import build_table
import requests
from create_strategy import get_starategy

matplotlib.use('Agg')
app = Flask(__name__)


class get_stock_all:
    def __init__(self, name_company,time,ask_for_symbol=False):

        name_company = name_company.replace(" ", "%20") #dealing with spaces
        df_list = self.read_yahoo_finance(name_company) 
        result_df = df_list[0]
        stock = self.get_symbol_for_stock(ask_for_symbol, result_df)
        info_table = pd.DataFrame.from_dict(stock.info, orient='index') #make dataframe from dictionary
        self.stock = stock 
        self.name = name_company
        self.info = stock.info
        self.history = stock.history(period=time)
        self.stocklist = result_df
        self.table = info_table

    def read_yahoo_finance(self, name_company):
        website_to_get = f'https://finance.yahoo.com/lookup?s={name_company}' #forming the url of the site
        r = requests.get(website_to_get,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        df_list = pd.read_html(r.text)
        return df_list

    def get_symbol_for_stock(self, ask_for_symbol, result_df):
        if not ask_for_symbol: #ask for symbol is parameter which says weather to show symbols or not
            stock = yf.Ticker(result_df['Symbol'][0]) #getting the symbol of the stock
        else:
            print(result_df)
            check_stock = input(
                'Is your stock the top one in the table? If yes then type Y; if not then type the symbol of the stocck from the above table: ')
            if check_stock.lower == 'y':
                stock = yf.Ticker(result_df['Symbol'][0]) #check details of the stock
            else:
                stock = yf.Ticker(check_stock)
        return stock

    def make_graph(self,destination):
        plt.plot(self.history['Open'])
        plt.savefig(destination)

    @classmethod
    def make_graph_two(cls, name_company1, name_company2, time):
        stock1 = cls(name_company1, time=time)
        stock2 = cls(name_company2, time=time)
        # Plot everything by leveraging the very powerful matplotlib package
        plt.plot(stock1.history['Open'], label=stock1.name)
        plt.plot(stock2.history['Open'], label=stock2.name)
        plt.legend()
        filePath = 'static/graph2.png'
        # As file at filePath is deleted now, so we should check if file exists or not not before deleting them
        plt.savefig(filePath)


def get_form_value(request,field):
    try:
        value_to_return = str(request.form[field])
    except:
        value_to_return = None
    return value_to_return