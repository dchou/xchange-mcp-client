# xchange-mcp-client

[xchange-mcp](https://github.com/dchou/xchange-mcp) 服务器的 Python 客户端。`XchangeMcpClient` 封装 MCP HTTP API，让你以熟悉的 ccxt 风格接口在 20+ 个加密货币交易所进行交易。

## 支持的交易所

### 中心化交易所 (CEX)

| 交易所 | 现货 | 现货杠杆 | 合约 | 测试网 |
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

> Maicoin MAX 与 BitoPro 为台湾本地交易所。

### 去中心化交易所 (DEX)

| 交易所 | 永续合约 | 测试网 |
|--------|---------|--------|
| Hyperliquid | ✓ | - |
| Backpack | ✓ | - |
| Aster | ✓ | - |
| Lighter | ✓ | - |

## 安装

```bash
git clone https://github.com/dchou/xchange-mcp-client.git
cd xchange-mcp-client
pip install -r requirements.txt
```

**环境要求：** Python 3.10+

## MCP 服务器

可使用托管服务器或自行部署：

- **托管：** `https://xchange-mcp.ezcoin.cc/mcp`
- **自部署：** 请参阅 [xchange-mcp](https://github.com/dchou/xchange-mcp) 的说明

## 快速开始

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
        # 查询余额
        balance = await client.fetch_balance()
        print("USDT 余额:", balance.get("total", {}).get("USDT"))

        # 获取当前价格
        ticker = await client.fetch_ticker("BTC/USDT:USDT")
        price = ticker.get("last")
        print(f"BTC 价格: {price}")

        # 以市价下方 5% 挂限价买单
        order = await client.create_limit_order(
            symbol="BTC/USDT:USDT",
            side="buy",
            amount=0.002,
            price=price * 0.95,
        )
        print("订单 ID:", order.get("id"))

asyncio.run(main())
```

## 配置说明

构建 `config` 字典以传入交易所凭证：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `exchange_name` | str | 是 | 交易所标识符（如 `"bybit"`、`"binance"`）|
| `api_key` | str | 否* | API Key（*私有端点必填）|
| `api_secret` | str | 否* | API Secret |
| `api_password` | str | 否 | Passphrase（OKX、Bitget、KuCoin）|
| `is_testnet` | bool | 否 | 使用测试网/模拟环境（默认：`False`）|
| `market_type` | str | 否 | `"spot"`、`"swap"`、`"margin"`（默认：`"swap"`）|
| `leverage` | int | 否 | 合约默认杠杆倍数 |
| `margin_mode` | str | 否 | `"cross"`（全仓）或 `"isolated"`（逐仓）|
| `position_mode` | str | 否 | `"one_way"`（单向）或 `"hedge"`（双向）|

### 交易对格式

遵循 ccxt 统一交易对规范：
- **现货：** `"BTC/USDT"`
- **永续合约：** `"BTC/USDT:USDT"`
- **现货杠杆：** `"BTC/USDT"`

### MCP 服务器 API Key（可选）

若自部署服务器需要验证，请传入 `mcp_api_key`：

```python
client = XchangeMcpClient(url=MCP_URL, config=config, mcp_api_key="your-server-key")
```

## API 参考

### 构造函数

```python
XchangeMcpClient(url: str, config: dict = None, mcp_api_key: str = "")
```

建议以异步上下文管理器使用——进入时自动连接，退出时自动关闭：

```python
async with XchangeMcpClient(url=MCP_URL, config=config) as client:
    ...
```

或手动管理生命周期：

```python
client = XchangeMcpClient(url=MCP_URL, config=config)
await client._initialize()
await client.connect()
# ... 执行操作 ...
await client.close()
await client.client.aclose()
```

---

### 账户

#### `fetch_balance(params={}) → dict`

获取账户余额。

```python
balance = await client.fetch_balance()
# {"free": {"USDT": 1000.0}, "used": {...}, "total": {...}}
```

#### `fetch_positions(symbol=None) → dict`

获取持仓信息。可传入 symbol 进行筛选。

```python
positions = await client.fetch_positions("BTC/USDT:USDT")
```

---

### 订单

#### `create_order(symbol, type, side, amount, price=None, params=None) → dict`

通用下单方法。

| 参数 | 类型 | 说明 |
|------|------|------|
| `symbol` | str | 统一交易对 |
| `type` | str | `"limit"`（限价）或 `"market"`（市价）|
| `side` | str | `"buy"`（买）或 `"sell"`（卖）|
| `amount` | float | 基础币种数量 |
| `price` | float | 限价单必填 |
| `params` | dict | 交易所特定额外参数 |

返回已创建的订单字典。

#### `create_limit_order(symbol, side, amount, price, params=None) → dict`

限价单快捷方法（等同 `create_order(..., type="limit", ...)`）。

#### `create_market_order(symbol, side, amount, params=None) → dict`

市价单快捷方法（等同 `create_order(..., type="market", ...)`）。

#### `cancel_order(order_id, symbol) → dict`

撤销单笔挂单。

#### `cancel_all_orders(symbol=None) → dict`

撤销所有挂单。传入 symbol 可限制特定市场。

#### `fetch_order(id, symbol=None, params=None) → dict`

按 ID 查询单笔订单详情。

#### `fetch_open_orders(symbol=None, params=None) → list`

获取所有挂单列表。

#### `fetch_closed_orders(symbol=None, since=None, limit=None, params=None) → list`

获取已成交/已关闭订单列表。

#### `close_position(symbol, side, amount=None) → dict`

平仓。

| 参数 | 类型 | 说明 |
|------|------|------|
| `symbol` | str | 统一交易对 |
| `side` | str | `"long"`（多）或 `"short"`（空）|
| `amount` | float | 平仓数量；省略则全部平仓 |

#### `fetch_my_trades(symbol=None, limit=50, params=None) → list`

获取个人成交历史。

#### `set_leverage(symbol, leverage) → dict`

设置合约杠杆倍数。

```python
await client.set_leverage("BTC/USDT:USDT", 10)
```

---

### 行情数据

#### `fetch_ticker(symbol, params=None) → dict`

获取当前行情，包含 `last`、`bid`、`ask`、`volume`。

#### `fetch_order_book(symbol, limit=None, params=None) → dict`

获取订单簿，包含 `bids` 与 `asks` 列表。

#### `fetch_ohlcv(symbol, timeframe="1h", since=None, limit=None, params=None) → list`

获取 K 线数据，格式为 `[timestamp, open, high, low, close, volume]` 列表。

支持周期：`"1m"`、`"5m"`、`"15m"`、`"1h"`、`"4h"`、`"1d"` 等。

```python
candles = await client.fetch_ohlcv("BTC/USDT:USDT", timeframe="1h", limit=100)
```

---

### 杠杆借贷

#### `get_borrow_rate(asset) → dict`

获取杠杆资产的当前借贷利率。

```python
rate = await client.get_borrow_rate("BTC")
# {"asset": "BTC", "borrow_rate": 0.0001, ...}
```

#### `get_borrowed_amount(asset) → dict`

获取当前已借贷数量。

```python
result = await client.get_borrowed_amount("BTC")
borrowed = result.get("borrowed_amount", 0)
```

#### `get_borrowed_records(asset) → list`

获取借贷历史记录。

#### `fetch_margin_config(symbol=None) → dict`

获取杠杆交易配置（最大杠杆、维持保证金率等）。

---

### 工具方法

#### `get_is_testnet() → bool`

若当前连接为测试网/模拟环境则返回 `True`。

#### `get_filled_orders(symbol=None, since=None) → list`

获取已成交订单及完整成交明细。

#### `get_closed_pnls(symbol=None) → list`

获取合约已实现盈亏历史。

---

## 示例

请参阅 [`examples/`](examples/) 目录：

- **`test_bybit.py`** — Bybit 杠杆交易：借贷利率、市价单、还款
- **`test_exchange_client.py`** — 多交易所完整方法测试

```bash
# 运行 Bybit 杠杆测试
python examples/test_bybit.py --url https://xchange-mcp.ezcoin.cc/mcp

# 交互式测试特定交易所
python examples/test_exchange_client.py -e bybit

# 测试多个交易所
python examples/test_exchange_client.py -e bybit,okx

# 使用自部署服务器
python examples/test_exchange_client.py --url http://localhost:8000/mcp -e binance
```

运行示例前，请将 `.env.example` 复制为 `.env` 并填入你的 API 凭证。

## 许可证

MIT
