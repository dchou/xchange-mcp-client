# xchange-mcp-client

[xchange-mcp](https://github.com/dchou/xchange-mcp) 伺服器的 Python 客戶端。`XchangeMcpClient` 封裝 MCP HTTP API，讓你以熟悉的 ccxt 風格介面在 20+ 個加密貨幣交易所進行交易。

## 支援的交易所

### 中心化交易所 (CEX)

| 交易所 | 現貨 | 現貨槓桿 | 合約 | 測試網 |
|--------|------|---------|------|--------|
| Binance | ✓ | ✓ | ✓ | ✓ |
| Bybit | ✓ | ✓ | ✓ | ✓ |
| OKX | ✓ | ✓ | ✓ | ✓ |
| Gate.io | ✓ | ✓ | ✓ | ✓ |
| Bitget | ✓ | ✓ | ✓ | ✓ |
| MEXC | ✓ | ✓ | ✓ | - |
| HTX | ✓ | ✓ | ✓ | - |
| KuCoin | ✓ | - | ✓ | - |
| Bitfinex | ✓ | - | ✓ | ✓ |
| Deribit | ✓ | - | ✓ | ✓ |
| Pionex | ✓ | - | ✓ | - |
| Kraken / KrakenFutures | ✓ | - | ✓ | - |
| Coinbase | ✓ | - | - | - |
| Robinhood | ✓ | - | - | - |
| Alpaca | ✓ | - | - | ✓ |
| BingX | - | - | ✓ | - |
| Maicoin MAX | ✓ | - | - | - |
| BitoPro | ✓ | - | - | - |

> Maicoin MAX 與 BitoPro 為台灣本地交易所。

### 去中心化交易所 (DEX)

| 交易所 | 永續合約 | 測試網 |
|--------|---------|--------|
| Hyperliquid | ✓ | - |
| Backpack | ✓ | - |
| Aster | ✓ | - |
| Lighter | ✓ | - |

## 安裝

```bash
git clone https://github.com/dchou/xchange-mcp-client.git
cd xchange-mcp-client
pip install -r requirements.txt
```

**需求：** Python 3.10+

## MCP 伺服器

你可以使用託管伺服器或自行架設：

- **託管：** `https://xchange-mcp.ezcoin.cc/mcp`
- **自架：** 請參閱 [xchange-mcp](https://github.com/dchou/xchange-mcp) 的說明

## 快速開始

```python
import asyncio
from xchange_mcp_client import XchangeMcpClient

MCP_URL = "https://xchange-mcp.ezcoin.cc/mcp"

config = {
    "exchange_name": "bybit",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_SECRET_KEY",
    "is_testnet": True,
    "market_type": "swap",
}

async def main():
    async with XchangeMcpClient(url=MCP_URL, config=config) as client:
        # 查詢餘額
        balance = await client.fetch_balance()
        print("USDT 餘額:", balance.get("total", {}).get("USDT"))

        # 取得當前價格
        ticker = await client.fetch_ticker("BTC/USDT:USDT")
        price = ticker.get("last")
        print(f"BTC 價格: {price}")

        # 以市價下方 5% 掛限價買單
        order = await client.create_limit_order(
            symbol="BTC/USDT:USDT",
            side="buy",
            amount=0.002,
            price=price * 0.95,
        )
        print("訂單 ID:", order.get("id"))

asyncio.run(main())
```

## 設定說明

建立 `config` 字典以傳入交易所憑證：

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `exchange_name` | str | 是 | 交易所識別碼（例如 `"bybit"`、`"binance"`）|
| `api_key` | str | 否* | API Key（*私有端點必填）|
| `api_secret` | str | 否* | API Secret |
| `api_password` | str | 否 | Passphrase（OKX、Bitget、KuCoin）|
| `is_testnet` | bool | 否 | 使用測試網／模擬環境（預設：`False`）|
| `market_type` | str | 否 | `"spot"`、`"swap"`、`"margin"`（預設：`"swap"`）|
| `leverage` | int | 否 | 合約預設槓桿倍數 |
| `margin_mode` | str | 否 | `"cross"`（全倉）或 `"isolated"`（逐倉）|
| `position_mode` | str | 否 | `"one_way"`（單向）或 `"hedge"`（雙向）|

### 交易對格式

遵循 ccxt 統一交易對規範：
- **現貨：** `"BTC/USDT"`
- **永續合約：** `"BTC/USDT:USDT"`
- **現貨槓桿：** `"BTC/USDT"`

### MCP 伺服器 API Key（可選）

若自架伺服器需要驗證，請傳入 `mcp_api_key`：

```python
client = XchangeMcpClient(url=MCP_URL, config=config, mcp_api_key="your-server-key")
```

## API 參考

### 建構子

```python
XchangeMcpClient(url: str, config: dict = None, mcp_api_key: str = "")
```

建議以非同步上下文管理器使用——進入時自動連線，離開時自動關閉：

```python
async with XchangeMcpClient(url=MCP_URL, config=config) as client:
    ...
```

或手動管理生命週期：

```python
client = XchangeMcpClient(url=MCP_URL, config=config)
await client._initialize()
await client.connect()
# ... 執行操作 ...
await client.close()
await client.client.aclose()
```

---

### 帳戶

#### `fetch_balance(params={}) → dict`

取得帳戶餘額。

```python
balance = await client.fetch_balance()
# {"free": {"USDT": 1000.0}, "used": {...}, "total": {...}}
```

#### `fetch_positions(symbol=None) → dict`

取得持倉資訊。可傳入 symbol 進行篩選。

```python
positions = await client.fetch_positions("BTC/USDT:USDT")
```

---

### 訂單

#### `create_order(symbol, type, side, amount, price=None, params=None) → dict`

通用下單方法。

| 參數 | 類型 | 說明 |
|------|------|------|
| `symbol` | str | 統一交易對 |
| `type` | str | `"limit"`（限價）或 `"market"`（市價）|
| `side` | str | `"buy"`（買）或 `"sell"`（賣）|
| `amount` | float | 基礎幣種數量 |
| `price` | float | 限價單必填 |
| `params` | dict | 交易所特定額外參數 |

回傳已建立的訂單字典。

#### `create_limit_order(symbol, side, amount, price, params=None) → dict`

限價單快捷方法（等同 `create_order(..., type="limit", ...)`）。

#### `create_market_order(symbol, side, amount, params=None) → dict`

市價單快捷方法（等同 `create_order(..., type="market", ...)`）。

#### `cancel_order(order_id, symbol) → dict`

撤銷單筆掛單。

#### `cancel_all_orders(symbol=None) → dict`

撤銷所有掛單。傳入 symbol 可限制特定市場。

#### `fetch_order(id, symbol=None, params=None) → dict`

依 ID 查詢單筆訂單詳情。

#### `fetch_open_orders(symbol=None, params=None) → list`

取得所有掛單列表。

#### `fetch_closed_orders(symbol=None, since=None, limit=None, params=None) → list`

取得已成交／已關閉訂單列表。

#### `close_position(symbol, side, amount=None) → dict`

平倉。

| 參數 | 類型 | 說明 |
|------|------|------|
| `symbol` | str | 統一交易對 |
| `side` | str | `"long"`（多）或 `"short"`（空）|
| `amount` | float | 平倉數量；省略則全部平倉 |

#### `fetch_my_trades(symbol=None, limit=50, params=None) → list`

取得個人成交歷史。

#### `set_leverage(symbol, leverage) → dict`

設定合約槓桿倍數。

```python
await client.set_leverage("BTC/USDT:USDT", 10)
```

---

### 行情資料

#### `fetch_ticker(symbol, params=None) → dict`

取得當前行情，包含 `last`、`bid`、`ask`、`volume`。

#### `fetch_order_book(symbol, limit=None, params=None) → dict`

取得訂單簿，包含 `bids` 與 `asks` 列表。

#### `fetch_ohlcv(symbol, timeframe="1h", since=None, limit=None, params=None) → list`

取得 K 線資料，格式為 `[timestamp, open, high, low, close, volume]` 列表。

支援週期：`"1m"`、`"5m"`、`"15m"`、`"1h"`、`"4h"`、`"1d"` 等。

```python
candles = await client.fetch_ohlcv("BTC/USDT:USDT", timeframe="1h", limit=100)
```

---

### 槓桿借貸

#### `get_borrow_rate(asset) → dict`

取得槓桿資產的當前借貸利率。

```python
rate = await client.get_borrow_rate("BTC")
# {"asset": "BTC", "borrow_rate": 0.0001, ...}
```

#### `get_borrowed_amount(asset) → dict`

取得目前已借貸數量。

```python
result = await client.get_borrowed_amount("BTC")
borrowed = result.get("borrowed_amount", 0)
```

#### `get_borrowed_records(asset) → list`

取得借貸歷史紀錄。

#### `fetch_margin_config(symbol=None) → dict`

取得槓桿交易設定（最大槓桿、維持保證金率等）。

---

### 工具方法

#### `get_is_testnet() → bool`

若目前連線為測試網／模擬環境則回傳 `True`。

#### `get_filled_orders(symbol=None, since=None) → list`

取得已成交訂單及完整成交明細。

#### `get_closed_pnls(symbol=None) → list`

取得合約已實現盈虧歷史。

---

## 範例

請參閱 [`examples/`](examples/) 目錄：

- **`test_bybit.py`** — Bybit 槓桿交易：借貸利率、市價單、還款
- **`test_exchange_client.py`** — 多交易所完整方法測試

```bash
# 執行 Bybit 槓桿測試
python examples/test_bybit.py --url https://xchange-mcp.ezcoin.cc/mcp

# 互動式測試特定交易所
python examples/test_exchange_client.py -e bybit

# 測試多個交易所
python examples/test_exchange_client.py -e bybit,okx

# 使用自架伺服器
python examples/test_exchange_client.py --url http://localhost:8000/mcp -e binance
```

執行範例前，請將 `.env.example` 複製為 `.env` 並填入你的 API 憑證。

## 授權

MIT
