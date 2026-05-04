#!/usr/bin/env python3
"""
リアルタイムテクニカル指標データ取得スクリプト
yfinance を使用して21銘柄のOHLC・テクニカル指標を自動取得
"""

import yfinance as yf
import pandas as pd
import json
import math
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 対象銘柄
TICKERS = {
    'STRONG_BUY': ['AMD', 'AVGO', 'MU', 'TSM', 'GOOGL', 'SOXL', 'SMH', '1570.T', 'QQQ'],
    'BUY': ['NVDA', 'QCOM', 'ASML', 'AMAT', 'LRCX', 'MSFT', 'TECL', 'AMZN'],
    'SELL': ['PLTR', 'ORCL', 'ARKK'],
    'STRONG_SELL': ['META']
}

def get_close_series(df):
    """DataFrameから Close 列を取得（マルチインデックス対応）"""
    if isinstance(df.columns, pd.MultiIndex):
        return df['Close'].squeeze()
    return df['Close']

def get_ohlc(df):
    """DataFrame から OHLC を取得（マルチインデックス対応）"""
    close = get_close_series(df)
    high = df['High'].squeeze() if isinstance(df.columns, pd.MultiIndex) else df['High']
    low = df['Low'].squeeze() if isinstance(df.columns, pd.MultiIndex) else df['Low']
    volume = df['Volume'].squeeze() if isinstance(df.columns, pd.MultiIndex) else df['Volume']
    return {'close': close, 'high': high, 'low': low, 'volume': volume}

def calculate_rsi(data, period=14):
    """RSI計算"""
    close = get_close_series(data)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_val = rsi.iloc[-1]
    return int(rsi_val) if not pd.isna(rsi_val) else 50

def calculate_sma(data, period):
    """SMA計算"""
    close = get_close_series(data)
    sma = close.rolling(window=period).mean()
    return round(sma.iloc[-1], 2)

def calculate_atr(data, period=14):
    """ATR計算"""
    ohlc = get_ohlc(data)
    high = ohlc['high']
    low = ohlc['low']
    close = ohlc['close']

    high_low = high - low
    high_close = abs(high - close.shift())
    low_close = abs(low - close.shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(period).mean()
    return round(atr.iloc[-1], 2)

def calculate_bolinger_bands(data, period=20, std_dev=2):
    """ボリンジャーバンド計算"""
    close = get_close_series(data)
    sma = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return round(upper.iloc[-1], 2), round(sma.iloc[-1], 2), round(lower.iloc[-1], 2)

def calculate_support_resistance(data, period=20):
    """サポート・レジスタンス計算"""
    ohlc = get_ohlc(data)
    high = ohlc['high']
    low = ohlc['low']
    close = ohlc['close']

    high_data = high.rolling(window=period).max()
    low_data = low.rolling(window=period).min()

    resistance = round(high_data.iloc[-1], 2)
    support = round(low_data.iloc[-1], 2)
    pivot = round((resistance + support + close.iloc[-1]) / 3, 2)

    return {
        'resistance': resistance,
        'support': support,
        'pivot': pivot,
        'current': round(close.iloc[-1], 2)
    }

def calculate_fibonacci(data, period=20):
    """フィボナッチレベル計算"""
    ohlc = get_ohlc(data)
    high = ohlc['high']
    low = ohlc['low']

    high_val = high.rolling(window=period).max().iloc[-1]
    low_val = low.rolling(window=period).min().iloc[-1]
    diff = high_val - low_val

    return {
        '236': round(high_val - diff * 0.236, 2),
        '382': round(high_val - diff * 0.382, 2),
        '500': round(high_val - diff * 0.500, 2),
        '618': round(high_val - diff * 0.618, 2)
    }

def calculate_macd(data):
    """MACD計算"""
    close = get_close_series(data)
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9).mean()

    return 'BULLISH' if macd_line.iloc[-1] > signal_line.iloc[-1] else 'BEARISH'

def get_ohlc_history(data, days=60):
    """過去N日間のOHLC履歴を取得（キャンドルチャート用）"""
    ohlc = get_ohlc(data)
    close = ohlc['close']
    high = ohlc['high']
    low = ohlc['low']

    # 直近N日分を取得
    recent_data = close.tail(days)
    if len(recent_data) < days:
        recent_data = close

    history = []
    for date in recent_data.index:
        try:
            history.append({
                'date': str(date)[:10],
                'open': round(float(data.loc[date, 'Open'] if isinstance(data.columns, pd.MultiIndex) else data.loc[date, 'Open']), 2),
                'high': round(float(high.loc[date]), 2),
                'low': round(float(low.loc[date]), 2),
                'close': round(float(close.loc[date]), 2)
            })
        except:
            pass

    return history

def fetch_ticker_data(ticker):
    """1銘柄のテクニカルデータを取得"""
    try:
        # 過去1年のデータを取得
        data = yf.download(ticker, start=datetime.now() - timedelta(days=365),
                          end=datetime.now(), progress=False, interval='1d')

        if len(data) < 200:
            return None

        # 必要なデータを計算
        return {
            'sr': calculate_support_resistance(data),
            'fib': calculate_fibonacci(data),
            'sma': {
                'sma20': calculate_sma(data, 20),
                'sma50': calculate_sma(data, 50),
                'sma200': calculate_sma(data, 200)
            },
            'rsi': calculate_rsi(data),
            'macd': calculate_macd(data),
            'atr': calculate_atr(data),
            'bbUpper': calculate_bolinger_bands(data)[0],
            'bbMiddle': calculate_bolinger_bands(data)[1],
            'bbLower': calculate_bolinger_bands(data)[2],
            'ohlcHistory': get_ohlc_history(data, 60),
            'is_new': False
        }
    except Exception as e:
        print(f"❌ {ticker}: {str(e)[:50]}")
        return None

def main():
    """メイン処理"""
    print("🚀 yfinance リアルタイムデータ取得開始...")

    technical_data = {}

    # 全銘柄を順序付けて取得
    all_tickers = []
    for category in TICKERS.values():
        all_tickers.extend(category)

    total = len(all_tickers)
    for idx, ticker in enumerate(all_tickers, 1):
        print(f"[{idx:2d}/{total}] {ticker:6s}", end=' ')
        data = fetch_ticker_data(ticker)

        if data:
            technical_data[ticker] = data
            print("✅")
        else:
            print("⏭️ ")

    # JSONファイルに保存
    output_path = Path(__file__).parent / 'technical_data.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(technical_data, f, indent=2, ensure_ascii=False)

    print(f"\n✨ 完了: {len(technical_data)}/{total}銘柄")
    print(f"📁 保存先: {output_path}")
    print(f"⏰ 更新日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return len(technical_data) > 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
