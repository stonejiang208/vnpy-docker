# 
from vnpy.event import EventEngine
from copy import copy
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# from vnpy.gateway.binance import BinanceGateway
from vnpy.gateway.bitmex import BitmexGateway
from vnpy.gateway.binance import BinanceGateway  
from vnpy.gateway.huobi import  HuobiGateway
from vnpy.gateway.okex import OkexGateway
# from vnpy.gateway.futu import FutuGateway
# from vnpy.gateway.ib import IbGateway
# from vnpy.gateway.ctp import CtpGateway
# from vnpy.gateway.ctptest import CtptestGateway
#from vnpy.gateway.mini import MiniGateway
# from vnpy.gateway.minitest import MinitestGateway
# from vnpy.gateway.femas import FemasGateway
# from vnpy.gateway.tiger import TigerGateway
# from vnpy.gateway.oes import OesGateway
from vnpy.gateway.okex import OkexGateway
# from vnpy.gateway.huobi import HuobiGateway
from vnpy.gateway.bitfinex import BitfinexGateway
# from vnpy.gateway.onetoken import OnetokenGateway
from vnpy.gateway.okexf import OkexfGateway
# from vnpy.gateway.xtp import XtpGateway
# from vnpy.gateway.hbdm import HbdmGateway
# from vnpy.gateway.tap import TapGateway
# from vnpy.gateway.tora import ToraGateway
# from vnpy.gateway.alpaca import AlpacaGateway
import datetime
from vnpy.app.cta_strategy import CtaStrategyApp
# from vnpy.app.csv_loader import CsvLoaderApp
# from vnpy.app.algo_trading import AlgoTradingApp
from vnpy.app.cta_backtester import CtaBacktesterApp
# from vnpy.app.data_recorder import DataRecorderApp
# from vnpy.app.risk_manager import RiskManagerApp
from vnpy.app.script_trader import ScriptTraderApp
from vnpy.trader.event import EVENT_TRADE, EVENT_ORDER, EVENT_LOG, EVENT_TICK, EVENT_CONTRACT
from vnpy.event import Event, EVENT_TIMER

from vnpy.app.rpc_service import RpcServiceApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from logging import INFO
from vnpy.trader.setting import SETTINGS
from time import sleep
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager
from vnpy.trader.utility import BarGenerator, ArrayManager
from vnpy.trader.object import (
    SubscribeRequest,
    TickData,
    BarData,
    ContractData
)

from pprint import pprint
from kafka import KafkaProducer
import time
import json

# pip install kafka-python
# producer = KafkaProducer(bootstrap_servers=['kafka:9092'])

SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True
vt_symbols = ["XBTUSD.BITMEX"]

binance_setting = {
    "key": "",
    "secret": "",
    "session_number": 3,
    "proxy_host": "",
    "proxy_port": "",
}

huobi_setting = {
    "API Key": "",
    "Secret Key": "",
    "会话数": 3,
    "代理地址": "",
    "代理端口": '',
}

okex_setting = {
    "API Key": "",
    "Secret Key": "",
    "Passphrase": "",
    "会话数": 3,
    "代理地址": "",
    "代理端口": '',
}

bitfinex_setting = {
    "key": "",
    "secret": "",
    "session": 3,
    "proxy_host": "",
    "proxy_port": "",
}

'''
SERVERNAME="mysql-vnpy"
docker run \
-e MYSQL_ROOT_PASSWORD=123456 \
-d \
--restart always \
-h ${SERVERNAME} \
--name=${SERVERNAME} \
-v /data/mysql-vnpy/:/var/lib/mysql \
mysql:latest --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --default-authentication-plugin=mysql_native_password
## 
## CREATE SCHEMA `vnpy` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ;
## create database vnpy default charset utf8 collate utf8_unicode_ci;
'''

db_setting = {
    'driver':'mysql',
    'database':'vnpy',
    'host':'mysql',
    'port':3306,
    'user':'root',
    'password':'123456'
}


class symbol_tick :
    bg = None
    def __init__(self):
        self.tick = None
        if not symbol_tick.bg:
            symbol_tick.bg = BarGenerator(symbol_tick.on_bar, 5, symbol_tick.on_5m_bar)

    def on_bar(bar: BarData):
        b = copy(bar)
        symbol_tick.bg.update_bar(b) # 驱动产生5mbar
        #database_manager.save_bar_data([b])

    def on_5m_bar(bar: BarData):
        pass

    def on_tick(self, tick):
        #print ("onticker {")
        self.tick = copy(tick)
        symbol_tick.bg.update_tick(self.tick)
        #pprint (tick)
        #print ("onticker }")
        # public with kafka
        #ts = int  (time.time() * 1000)
        if tick.name=="":
            print ("name is null",tick.gateway_name)
            return
        msg = {
            'ts': datetime.datetime.now().isoformat(),
            'tick':{
                'ex':tick.gateway_name,
                'name':tick.name,
                't':tick.datetime.isoformat(),
                'o':tick.open_price,
                'h':tick.high_price,
                'l':tick.low_price,
                'c':tick.last_price,
                'v':tick.volume,
                'depth':{
                    'b1':tick.bid_price_1,
                    'a1':tick.ask_price_1,
                    'bv1':tick.bid_volume_1,
                    'av1':tick.ask_volume_1
                }
            }
        }
        # to do
        print (json.dumps(msg))
        #msg = json.dumps(msg).encode('utf-8')
        #producer.send('test',msg)
ex_symbols = {} # 用来存储交易所币对
data_symbols = {} # 用来存储币对tick

def on_ticker(event: Event):
    tick = event.data
    symbol = tick.vt_symbol
    if symbol not in data_symbols:
        t = symbol_tick()
        data_symbols[symbol] = t
        t.on_tick(tick)
    else:
        data_symbols[symbol].on_tick(tick)

def on_contract(event: Event):
    exchange = event.data.exchange
    if exchange not in ex_symbols:
        ex_symbols[exchange] = []
    ex_symbols[exchange].append(event.data.symbol)

class huobi_ticker:
    def on_timer(event: Event):
        if (not huobi_ticker.gateway):
            return
        huobi_ticker.gateway.get_rest_ticker()
    gateway = None

def main():
    """"""
    #qapp = create_qapp()

    event_engine = EventEngine()

    main_engine = MainEngine(event_engine)
    main_engine.write_log("主引擎创建成功")

    #event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)

    event_engine.register(EVENT_TICK, on_ticker)
    event_engine.register(EVENT_CONTRACT, on_contract)
    event_engine.register(EVENT_TIMER, huobi_ticker.on_timer)
    main_engine.write_log("注册日志事件监听")
    # main_engine.add_gateway(BinanceGateway)
    # main_engine.add_gateway(CtpGateway)
    # main_engine.add_gateway(CtptestGateway)
    # main_engine.add_gateway(MiniGateway)
    # main_engine.add_gateway(MinitestGateway)
    # main_engine.add_gateway(FemasGateway)
    # main_engine.add_gateway(IbGateway)
    # main_engine.add_gateway(futuGateway)
    #binance = main_engine.add_gateway(BinanceGateway)
    #huobi = main_engine.add_gateway(HuobiGateway)
    #huobi_ticker.gateway = huobi
    #okex = main_engine.add_gateway(OkexGateway)
    bitfinex = main_engine.add_gateway(BitfinexGateway)
    #bitmex = main_engine.add_gateway(BitmexGateway)

    #main_engine.write_log("添加 gateways")
    # main_engine.add_gateway(TigerGateway)
    # main_engine.add_gateway(OesGateway)
    # main_engine.add_gateway(OkexGateway)
    # main_engine.add_gateway(HuobiGateway)
    # main_engine.add_gateway(OnetokenGateway)
    # main_engine.add_gateway(OkexfGateway)
    # main_engine.add_gateway(HbdmGateway)
    # main_engine.add_gateway(XtpGateway)
    # main_engine.add_gateway(TapGateway)
    # main_engine.add_gateway(ToraGateway)
    # main_engine.add_gateway(AlpacaGateway)
    
    #cta_engine = main_engine.add_app(CtaStrategyApp)
    #main_engine.write_log("添加 CtaStrategyApp")

    # main_engine.add_app(CsvLoaderApp)
    # main_engine.add_app(AlgoTradingApp)
    # main_engine.add_app(DataRecorderApp)
    # main_engine.add_app(RiskManagerApp)
    #main_engine.add_app(ScriptTraderApp)
    #main_engine.add_app(RpcServiceApp)

    #main_window = MainWindow(main_engine, event_engine)
    #main_window.showMaximized()

    #main_engine.connect(binance_setting, 'BINANCE')
    # 火币是否存在websocket全量ticker,还需要确认。 REST方式获取：https://api.huobipro.com/market/tickers/
    #main_engine.connect(huobi_setting, 'HUOBI')
    #main_engine.connect(okex_setting, 'OKEX')
    main_engine.connect(bitfinex_setting, 'BITFINEX')
    #main_engine.connect(bitmex_setting, 'BITMEX')

    main_engine.write_log("连接gateways")

    sleep (10)
    
    for k,v in ex_symbols.items():
        symbols = list(v)
        reqs = []
        print (str(len(symbols)) + '个symbols')

        if k == Exchange.HUOBI: # 火币不走subscribe
            continue

        for symbol in symbols:
            req = SubscribeRequest(symbol=symbol, exchange=k)
            reqs.append(req)
        main_engine.subscribe_all(reqs, k.value)

    while True:
        print('分隔符=================================================================')
        data = data_symbols.copy() # 因为data_symbols是多线程操作的对象，其实要加锁
        # for k, v in data.items():
        #     tick = v.tick
        #     print (f'{k}\t O:{tick.open_price}\t H:{tick.high_price}\t L:{tick.low_price}\t C:{tick.last_price}\t V:{tick.volume}\t {tick.datetime}')
        print(f'当前 {len(data)} symbols')
        sleep(1)
''' 
    req = SubscribeRequest(
                symbol='XBTUSD',
                exchange=Exchange.BITMEX
            )
    main_engine.subscribe(req, 'BITMEX')
   
    while True:
        sleep(5)

    cta_engine.init_engine()
    main_engine.write_log("CTA策略初始化完成")

    cta_engine.init_all_strategies()
    sleep(10)   # Leave enough time to complete strategy initialization
    main_engine.write_log("CTA策略全部初始化")

    cta_engine.start_all_strategies()
    main_engine.write_log("CTA策略全部启动")
'''
    #qapp.exec()


if __name__ == "__main__":
    main()
