#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 21:32:54 2021

@author: juan
"""

from web3 import Web3
from datetime import datetime
import pandas as pd
from flask import Flask, render_template
import defi.defi_tools as dft
import plotly.graph_objects as go
import json
import plotly



w3 = Web3(Web3.HTTPProvider(
    'https://mainnet.infura.io/v3/6495c030a0984fa989fa24ce8b5600b0'))

#w32 = Web3(Web3.HTTPProvider(
#    'https://28S2zG0yrCRsiJkvyzxEqia1Fah:0dc985c785c62b6faaead7abf5436dec@eth2-beacon-mainnet.infura.io'))


last = w3.eth.get_block('latest')

app = Flask(__name__)

@app.route('/')
def principal():
    
    nro_last_block = last.number
    nros = []
    trans_cant = []
    miners = []
    tiempo = []
    for a in range(nro_last_block, nro_last_block-10, -1):
        block = w3.eth.get_block(a)
        nros.append(a)
        tiempo.append(datetime.fromtimestamp(block.timestamp))
        trans_cant.append(len(block.transactions))
        miners.append(block.miner)
    
    df = pd.DataFrame()
    df["Nro"] = nros
    df["Time"] = tiempo
    df["Trans"] = trans_cant
    df["Miner"] = miners
    tabla = df
    cols = tabla.columns
    
    tiempo = datetime.fromtimestamp(last.timestamp)

    
    
    return render_template('principal.html',
                           data=tabla, 
                           cols = cols, passstatic_url_path='/static')
    
    
@app.route('/infoblock/<block>', methods = ["GET"])
def infoblock(block):
    
    block = int(block)
    block_info = w3.eth.get_block(block)
    tiempo = datetime.fromtimestamp(block_info.timestamp)
    transactions = block_info.transactions
    miner = block_info.miner
    difficulty = block_info.difficulty
    size = block_info.size
    gasused = block_info.gasUsed
    gaslimit = block_info.gasLimit
    basefeepergas = block_info.baseFeePerGas
    
    return render_template("infoblock.html", tiempo = tiempo,
                           transactions = len(transactions),
                           miner = miner,
                           difficulty = difficulty,
                           size = size,
                           gasused = gasused,
                           gaslimit = gaslimit,
                           bloque = block,
                           basefeepergas = basefeepergas, passstatic_url_path='/static')
    

@app.route('/transactions/<block>', methods = ["GET"])
def transactions(block):
    
    block = int(block)
    block_info = w3.eth.get_block(block)
    
    
    transactions = block_info.transactions
    list_transactions = []
    for i in transactions:
        list_transactions.append(i.hex())
    
    
    return render_template("transactions.html", data = list_transactions,
                           
                           bloque = block,
                           passstatic_url_path='/static')
    
    
@app.route('/infotransaction/<tran_hash>', methods = ["GET"])    
def infotransaction(tran_hash):
    transaction = w3.eth.get_transaction(tran_hash)
    block_number = transaction.blockNumber
    tran_from = getattr(transaction, "from")
    tran_to = transaction.to
    gas = transaction.gas
    gasprice = transaction.gasPrice
    value = transaction.value
    return render_template("infotransaction.html", block_number = block_number,
                           tran_from = tran_from,
                           tran_to = tran_to,
                           gas = gas,
                           gasprice = gasprice,
                           value = value,
                           passstatic_url_path='/static')
    
    
@app.route('/infoadress/<adress>', methods = ["GET"])
def infoadress(adress):
    balance = w3.eth.get_balance(adress)
    return render_template("infoadress.html", adress = adress,
                           balance = balance,
                           passtatic_url_path="/static")



@app.route('/cripto.html')
def cripto():
    #df = priceMulti(fsyms=["BTC","ETH","LTC","XRP"], tsyms=["USD","EUR","ARS","BTC", "ETH"])
    #df = df.reset_index()
    df = dft.geckoList().head(9)
    tickers = list(df.id)
    imagenes = list(df.image)
    zipobj=zip(tickers,imagenes)
    dic_imagen = dict(zipobj)
    df.drop(["image", "fully_diluted_valuation", "market_cap_change_24h",
             "market_cap_change_percentage_24h", "circulating_supply", "total_supply",
             "max_supply", "ath","ath_change_percentage", "ath_date", "atl",
             "atl_change_percentage", "atl_date", "roi", "market_cap_rank",
             "price_change_24h", "last_updated", "market_cap", "total_volume"],axis=1, inplace=True)
    df = df.rename({'price_change_percentage_24h': '%'}, axis='columns')
    cols = df.columns
    
    nombres = ["bitcoin", "ethereum", "ripple", "cardano", "binancecoin", "bitcoin-cash",
           "dogecoin", "tether"]
    tabla = pd.DataFrame()
    for nombre in nombres:
        lista = dft.geckoHistorical(nombre)
        lista["variacion"]=lista.price.pct_change()
        lista.drop(["market_caps", "total_volumes","price"], axis=1, inplace=True)
        tabla[nombre] = lista.variacion

    tabla.dropna(inplace=True)
    corr = tabla.corr()


    layout = go.Layout(xaxis_showgrid=True, yaxis_showgrid=True, xaxis_zeroline=True, yaxis_zeroline=True, title="Mapa de Correlación")
    
    heatmap = go.Heatmap(z=corr.values, y=corr.columns.values, x=corr.index.values, colorscale="Viridis")
    figure = go.Figure(data=[heatmap],layout=layout)
    figure['layout'].update(margin=dict(l=0,r=0,b=10,t=30))
    plot_json = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('cripto.html', data = df, cols=cols, plot_json = plot_json)


@app.route('/infocripto/<criptoname>')
def infocripto(criptoname):
    df2 = dft.geckoList()
    tickers = list(df2.id)
    imagenes = list(df2.image)
    zipobj=zip(tickers,imagenes)
    dic_imagen = dict(zipobj)
    df = dft.geckoMarkets(criptoname)
    df2 = dft.geckoHistorical(criptoname).round(4)
    df2.reset_index(inplace=True)
    
    
    
    df.reset_index(inplace=True)
    df.drop(["trust_score"], axis=1, inplace=True)
    cols=df2.columns
    return render_template("infocripto.html", data=df2[::-1], cols=cols, imagen=dic_imagen[criptoname],
                           nombre=criptoname)





