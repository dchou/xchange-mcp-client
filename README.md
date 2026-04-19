# xchange-mcp-client

A Python client for the [xchange-mcp](https://github.com/dchou/xchange-mcp) server. `XchangeMcpClient` wraps the MCP HTTP API to let you trade on 20+ crypto exchanges with a familiar, ccxt-style interface.

## Supported Exchanges

### Centralized (CEX)

| Exchange | Spot | Margin | Futures | Testnet |
|----------|------|--------|---------|---------|
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
| Kraken | ✓ | - | ✓ | - |
| Coinbase | ✓ | - | - | - |
| Robinhood | ✓ | - | - | - |
| Alpaca | ✓ | - | - | ✓ |
| BingX | - | - | ✓ | - |
| Maicoin MAX | ✓ | - | - | - |
| BitoPro | ✓ | - | - | - |

> Maicoin MAX and BitoPro are Taiwan-based exchanges.

### Decentralized (DEX)

| Exchange | Perpetuals | Testnet |
|----------|-----------|---------|
| Hyperliquid | ✓ | - |
| Backpack | ✓ | - |
| Aster | ✓ | - |
| Lighter | ✓ | - |


## Installation

```bash
git clone https://github.com/dchou/xchange-mcp-client.git
cd xchange-mcp-client
pip install -r requirements.txt
```

**Requirements:** Python 3.10+

## MCP Server

You can use the hosted server or self-host:

- **Hosted:** `https://xchange-mcp.ezcoin.cc/mcp`
- **Self-hosted:** See [xchange-mcp](https://github.com/dchou/xchange-mcp) for setup instructions

## Quick Start

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
        # Fetch balance
        balance = await client.fetch_balance()
        print("USDT balance:", balance.get("total", {}).get("USDT"))

        # Get current price
        ticker = await client.fetch_ticker("BTC/USDT:USDT")
        price = ticker.get("last")
        print(f"BTC price: {price}")

        # Place a limit buy order 5% below market
        order = await client.create_limit_order(
            symbol="BTC/USDT:USDT",
            side="buy",
            amount=0.002,
            price=price * 0.95,
        )
        print("Order ID:", order.get("id"))

asyncio.run(main())
```

## Configuration

Build a `config` dict to pass exchange credentials:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `exchange_name` | str | Yes | Exchange identifier (e.g. `"bybit"`, `"binance"`) |
| `api_key` | str | No* | API key (*required for private endpoints) |
| `api_secret` | str | No* | API secret |
| `api_password` | str | No | Passphrase (OKX, Bitget, KuCoin) |
| `is_testnet` | bool | No | Use testnet/demo environment (default: `False`) |
| `market_type` | str | No | `"spot"`, `"swap"`, `"margin"` (default: `"swap"`) |
| `leverage` | int | No | Default leverage for futures |
| `margin_mode` | str | No | `"cross"` or `"isolated"` |
| `position_mode` | str | No | `"one_way"` or `"hedge"` |

### Symbol format

Follow ccxt unified symbol conventions:
- **Spot:** `"BTC/USDT"`
- **Perpetual swap:** `"BTC/USDT:USDT"`
- **Margin:** `"BTC/USDT"`

### Optional MCP API key

If your self-hosted server requires authentication, pass `mcp_api_key`:

```python
client = XchangeMcpClient(url=MCP_URL, config=config, mcp_api_key="your-server-key")
```

## API Reference

### Constructor

```python
XchangeMcpClient(url: str, config: dict = None, mcp_api_key: str = "")
```

Use as an async context manager — it automatically connects on enter and closes on exit:

```python
async with XchangeMcpClient(url=MCP_URL, config=config) as client:
    ...
```

Or manage the lifecycle manually:

```python
client = XchangeMcpClient(url=MCP_URL, config=config)
await client._initialize()
await client.connect()
# ... do work ...
await client.close()
await client.client.aclose()
```

---

### Account

#### `fetch_balance(params={}) → dict`

Returns account balances.

```python
balance = await client.fetch_balance()
# {"free": {"USDT": 1000.0}, "used": {...}, "total": {...}}
```

#### `fetch_positions(symbol=None) → dict`

Returns open positions. Pass a symbol to filter.

```python
positions = await client.fetch_positions("BTC/USDT:USDT")
```

---

### Orders

#### `create_order(symbol, type, side, amount, price=None, params=None) → dict`

Generic order creation.

| Param | Type | Description |
|-------|------|-------------|
| `symbol` | str | Unified symbol |
| `type` | str | `"limit"` or `"market"` |
| `side` | str | `"buy"` or `"sell"` |
| `amount` | float | Order size in base currency |
| `price` | float | Required for limit orders |
| `params` | dict | Exchange-specific extra params |

Returns the created order dict.

#### `create_limit_order(symbol, side, amount, price, params=None) → dict`

Shortcut for `create_order(..., type="limit", ...)`.

#### `create_market_order(symbol, side, amount, params=None) → dict`

Shortcut for `create_order(..., type="market", ...)`.

#### `cancel_order(order_id, symbol) → dict`

Cancel a single open order.

#### `cancel_all_orders(symbol=None) → dict`

Cancel all open orders. Pass a symbol to limit to that market.

#### `fetch_order(id, symbol=None, params=None) → dict`

Fetch details for a single order by ID.

#### `fetch_open_orders(symbol=None, params=None) → list`

Returns list of open orders.

#### `fetch_closed_orders(symbol=None, since=None, limit=None, params=None) → list`

Returns list of closed/filled orders.

#### `close_position(symbol, side, amount=None) → dict`

Close an open position.

| Param | Type | Description |
|-------|------|-------------|
| `symbol` | str | Unified symbol |
| `side` | str | `"long"` or `"short"` |
| `amount` | float | Amount to close; omit to close entire position |

#### `fetch_my_trades(symbol=None, limit=50, params=None) → list`

Returns personal trade history.

#### `set_leverage(symbol, leverage) → dict`

Set leverage for a futures symbol.

```python
await client.set_leverage("BTC/USDT:USDT", 10)
```

---

### Market Data

#### `fetch_ticker(symbol, params=None) → dict`

Returns current ticker including `last`, `bid`, `ask`, `volume`.

#### `fetch_order_book(symbol, limit=None, params=None) → dict`

Returns order book with `bids` and `asks` lists.

#### `fetch_ohlcv(symbol, timeframe="1h", since=None, limit=None, params=None) → list`

Returns OHLCV candles as a list of `[timestamp, open, high, low, close, volume]`.

Supported timeframes: `"1m"`, `"5m"`, `"15m"`, `"1h"`, `"4h"`, `"1d"`, etc.

```python
candles = await client.fetch_ohlcv("BTC/USDT:USDT", timeframe="1h", limit=100)
```

---

### Margin

#### `get_borrow_rate(asset) → dict`

Returns current borrow rate for a margin asset.

```python
rate = await client.get_borrow_rate("BTC")
# {"asset": "BTC", "borrow_rate": 0.0001, ...}
```

#### `get_borrowed_amount(asset) → dict`

Returns currently borrowed amount.

```python
result = await client.get_borrowed_amount("BTC")
borrowed = result.get("borrowed_amount", 0)
```

#### `get_borrowed_records(asset) → list`

Returns borrowing history for an asset.

#### `fetch_margin_config(symbol=None) → dict`

Returns margin trading configuration (max leverage, maintenance margin, etc.).

---

### Utilities

#### `get_is_testnet() → bool`

Returns `True` if the session is connected to a testnet/demo environment.

#### `get_filled_orders(symbol=None, since=None) → list`

Returns filled orders with full trade details.

#### `get_closed_pnls(symbol=None) → list`

Returns closed PnL history for futures positions.

---

## Examples

See the [`examples/`](examples/) directory:

- **`test_bybit.py`** — Bybit margin trading: borrow rate, market orders, repayment
- **`test_exchange_client.py`** — Multi-exchange test suite covering all methods

```bash
# Run Bybit margin test
python examples/test_bybit.py --url https://xchange-mcp.ezcoin.cc/mcp

# Test a specific exchange interactively
python examples/test_exchange_client.py -e bybit

# Test multiple exchanges
python examples/test_exchange_client.py -e bybit,okx

# Use a custom server
python examples/test_exchange_client.py --url http://localhost:8000/mcp -e binance
```

Copy `.env.example` to `.env` and fill in your API credentials before running the examples.


## License

MIT
