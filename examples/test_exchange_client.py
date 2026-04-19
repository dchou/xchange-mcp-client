"""Test script to iterate user_configs and test XchangeMcpClient methods via MCP server."""

import asyncio
import os
import sys
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xchange_mcp_client import XchangeMcpClient

from dotenv import load_dotenv

load_dotenv(".env")

user_configs = [
    # Testnet
    {
        "exchange_name": "binance",
        "account_name": "bnDSpotDemo",
        "api_key": os.environ.get("bnDSpotDemo_API_KEY"),
        "secret": os.environ.get("bnDSpotDemo_SECRET_KEY"),
        "is_testnet": True,
        "is_active": True,
        "market_type": "spot",
        "amount": 0.0002,
        "symbol": "BTC/USDT",
    },
    # binance does not support sapi testnet
    # {
    #     "exchange_name": "binance",
    #     "account_name": "bnDDemo",
    #     "api_key": os.environ.get("bnDDemo_API_KEY"),
    #     "secret": os.environ.get("bnDDemo_SECRET_KEY"),
    #     "is_testnet": True,
    #     "is_active": True,
    #     "market_type": "swap",
    #     "amount": 0.002,
    #     "symbol": "BTC/USDT",
    # },
    {
        "exchange_name": "binance",
        "account_name": "bnDDemo",
        "api_key": os.environ.get("bnDDemo_API_KEY"),
        "secret": os.environ.get("bnDDemo_SECRET_KEY"),
        "is_testnet": True,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.002,          # notional must be no smaller than 100
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "bybit",
        "account_name": "bbDDemo",
        "api_key": os.environ.get("bbDDemo_API_KEY"),
        "secret": os.environ.get("bbDDemo_SECRET_KEY"),
        "is_testnet": True,
        "is_active": True,
        "market_type": "spot",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "bybit",
        "account_name": "bbDDemo",
        "api_key": os.environ.get("bbDDemo_API_KEY"),
        "secret": os.environ.get("bbDDemo_SECRET_KEY"),
        "is_testnet": True,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "bybit",
        "account_name": "bbDDemo",
        "api_key": os.environ.get("bbDDemo_API_KEY"),
        "secret": os.environ.get("bbDDemo_SECRET_KEY"),
        "is_testnet": True,
        "is_active": True,
        "market_type": "margin",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "okx",
        "account_name": "okDDemo",
        "api_key": os.environ.get('okDDemo_API_KEY'),
        "secret": os.environ.get('okDDemo_SECRET_KEY'),
        "passphrase": os.environ.get('okDDemo_PASSPHRASE'),
        "is_testnet": True,
        "is_active": True,
        "market_type": "spot",
        "amount": 0.01,
        "symbol": "BTC/USDT"
    },
    {
        "exchange_name": "okx",
        "account_name": "okDDemo",
        "api_key": os.environ.get('okDDemo_API_KEY'),
        "secret": os.environ.get('okDDemo_SECRET_KEY'),
        "passphrase": os.environ.get('okDDemo_PASSPHRASE'),
        "is_testnet": True,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.01,
        "symbol": "BTC/USDT",
        "position_mode": "one_way",
        "margin_mode": "cross",
        "leverage": 10,
    },
    {
        "exchange_name": "okx",
        "account_name": "okDDemo",
        "api_key": os.environ.get('okDDemo_API_KEY'),
        "secret": os.environ.get('okDDemo_SECRET_KEY'),
        "passphrase": os.environ.get('okDDemo_PASSPHRASE'),
        "is_testnet": True,
        "is_active": True,
        "market_type": "margin",
        "amount": 0.01,
        "symbol": "BTC/USDT"
    },
    {
        "exchange_name": "bitget",
        "account_name": "bgBDemo",
        "api_key": os.environ.get("bgBDemo_API_KEY"),
        "secret": os.environ.get("bgBDemo_SECRET_KEY"),
        "passphrase": os.environ.get("bgBDemo_PASSPHRASE"),
        "is_testnet": True,
        "is_active": True,
        "market_type": "spot",
        "position_mode": "hedge",
        "margin_mode": "cross",
        "leverage": 10,
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "bitget",
        "account_name": "bgD1",
        "api_key": os.environ.get("bgBDemo_API_KEY"),
        "secret": os.environ.get("bgBDemo_SECRET_KEY"),
        "passphrase": os.environ.get("bgBDemo_PASSPHRASE"),
        "is_testnet": True,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "bitget",
        "account_name": "bgD1",
        "api_key": os.environ.get("bgBDemo_API_KEY"),
        "secret": os.environ.get("bgBDemo_SECRET_KEY"),
        "passphrase": os.environ.get("bgBDemo_PASSPHRASE"),
        "is_testnet": True,
        "is_active": True,
        "market_type": "margin",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    # LIVE
    {
        "exchange_name": "hyperliquid",
        "account_name": "hlD",
        "api_key": os.environ.get("hlD_API_KEY"),
        "secret": os.environ.get("hlD_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.002,
        "symbol": "BTC/USDC",
    },
    {
        "exchange_name": "pionex",
        "account_name": "poD",
        "api_key": os.environ.get("poD_API_KEY"),
        "secret": os.environ.get("poD_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "spot",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "kraken",
        "account_name": "kkDSpot",
        "api_key": os.environ.get("kkDSpot_API_KEY"),
        "secret": os.environ.get("kkDSpot_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "spot",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "krakenfutures",
        "account_name": "kkDPerp",
        "api_key": os.environ.get("kkDPerp_API_KEY"),
        "secret": os.environ.get("kkDPerp_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.002,
        "symbol": "BTC/USD",
    },
    {
        "exchange_name": "bingx",
        "account_name": "bxDDebug",
        "api_key": os.environ.get("bxDDebug_API_KEY"),
        "secret": os.environ.get("bxDDebug_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "mexc",
        "account_name": "mxD",
        "api_key": os.environ.get("mxD_API_KEY"),
        "secret": os.environ.get("mxD_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "spot",
        "amount": 0.001,
        "symbol": "BTC/USDC",
    },
    {
        "exchange_name": "mexc",
        "account_name": "mxD",
        "api_key": os.environ.get("mxD_API_KEY"),
        "secret": os.environ.get("mxD_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.001,
        "symbol": "BTC/USDC",
    },
    {
        "exchange_name": "htx",
        "account_name": "hbDDebug",
        "api_key": os.environ.get("hbDDebug_API_KEY"),
        "secret": os.environ.get("hbDDebug_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "spot",
        "amount": 20,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "htx",
        "account_name": "hbDDebug",
        "api_key": os.environ.get("hbDDebug_API_KEY"),
        "secret": os.environ.get("hbDDebug_SECRET_KEY"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "kucoin",
        "account_name": "kcD",
        "api_key": os.environ.get("kcD_API_KEY"),
        "secret": os.environ.get("kcD_SECRET_KEY"),
        "passphrase": os.environ.get("kcD_PASSPHRASE"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "spot",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
    {
        "exchange_name": "kucoin",
        "account_name": "kcD",
        "api_key": os.environ.get("kcD_API_KEY"),
        "secret": os.environ.get("kcD_SECRET_KEY"),
        "passphrase": os.environ.get("kcD_PASSPHRASE"),
        "is_testnet": False,
        "is_active": True,
        "market_type": "swap",
        "amount": 0.002,
        "symbol": "BTC/USDT",
    },
]

SPOT_ONLY_EXCHANGES = [
    "pionex",
    "kraken",
    "alpaca",
    "mexc",
    "max",
    "bitopro",
    "robinhood",
]


def get_unified_symbol(symbol: str, market_type: str) -> str:
    """Convert symbol based on market type."""
    if not symbol:
        return symbol

    base, quote = symbol.split("/")

    if market_type == "swap":
        if quote in ["USDT", "USDC", "USD"]:
            return f"{base}/{quote}:{quote}"
        return f"{base}/{quote}"
    elif market_type in ("margin", "spot"):
        return f"{base}/{quote}"
    return symbol


async def test_full_cases(config: dict, client: XchangeMcpClient) -> dict:
    exchange_name = config.get("exchange_name")

    results = {
        "exchange": exchange_name,
        "account": config.get("account_name"),
        "status": {},
    }

    try:
        base_coin = config["symbol"].split("/")[0]
        quote_coin = config["symbol"].split("/")[1]

        symbol = get_unified_symbol(config["symbol"], config.get("market_type"))

        print(f"{exchange_name} symbol= {symbol}")

        amount = config.get("amount", 0.002)

        results["status"]["connect"] = "success"

        balance = await client.fetch_balance()
        results["status"]["fetch_balance"] = "success"
        if balance.get("total", {}).get(quote_coin, "N/A") != "N/A":
            print(
                f"  ✓ Balance: {balance.get('total', {}).get(quote_coin)} {quote_coin}"
            )
        elif balance.get("total", {}).get("USDC", "N/A") != "N/A":
            print(f"  ✓ Balance: {balance.get('total', {}).get('USDC')} USDC")
        else:
            print(f"  ✓ Balance: N/A")

        is_testnet = await client.get_is_testnet()

        if is_testnet:
            market_order = await client.create_market_order(
                symbol=symbol, side="sell", amount=amount
            )
            market_order_id = market_order.get("id")

            if market_order_id == "-1":
                results["status"]["create_market_order(sell)"] = (
                    f"failed: {market_order.get('code')} {market_order.get('msg')}"
                )
                print(
                    f"  ✗ Market order failed: {market_order.get('code')} {market_order.get('msg')}"
                )
            else:
                results["status"]["create_market_order"] = "success"
                fetched_order = await client.fetch_order(market_order_id, symbol)
                results["status"]["fetch_order"] = "success"
                print(
                    f"  ✓ Market order filled: order_id: {market_order_id} @ {fetched_order.get('average')} {fetched_order.get('amount')} {fetched_order.get('status')}"
                )

            borrowed_result = await client.get_borrowed_amount(base_coin)
            borrowed_amount = (
                borrowed_result.get("borrowed_amount", 0)
                if isinstance(borrowed_result, dict)
                else 0
            )

            if borrowed_amount and borrowed_amount > 0:
                market_order = await client.create_market_order(
                    symbol=symbol, side="buy", amount=borrowed_amount
                )
                market_order_id = market_order.get("id")

                if market_order_id == "-1":
                    results["status"]["create_market_order(buy)"] = (
                        f"failed: {market_order.get('code')} {market_order.get('msg')}"
                    )
                    print(
                        f"  ✗ Market order failed: {market_order.get('code')} {market_order.get('msg')}"
                    )
                else:
                    results["status"]["create_market_order(buy)"] = "success"
                    fetched_order = await client.fetch_order(market_order_id, symbol)
                    results["status"]["fetch_order"] = "success"
                    print(
                        f"  ✓ Market order filled: order_id: {market_order_id} @ {fetched_order.get('average')} {fetched_order.get('amount')} {fetched_order.get('status')}"
                    )

        ticker = await client.fetch_ticker(symbol)
        current_price = ticker.get("last")
        results["status"]["fetch_ticker"] = "success"
        if not current_price:
            print(f"  x Ticker: {symbol} failed to fetch_ticker")
            return results
        else:
            print(f"  ✓ Ticker: {symbol} @ {current_price}")

        limit_price = current_price * 0.95

        order = await client.create_limit_order(
            symbol=symbol, side="buy", amount=amount, price=limit_price
        )
        order_id = order.get("id")

        if order_id == "-1":
            results["status"]["create_limit_order"] = (
                f"failed: {order.get('code')} {order.get('msg')}"
            )
            print(
                f"  ✗ Limit order failed: @ {limit_price} {order.get('code')} {order.get('msg')}"
            )
        else:
            results["status"]["create_limit_order"] = "success"
            print(f"  ✓ Limit order created: order_id: {order_id} @ {limit_price}")

            fetched_order = await client.fetch_order(order_id, symbol)
            results["status"]["fetch_order"] = "success"
            print(
                f"  ✓ Order fetched: {fetched_order.get('id')} {fetched_order.get('status')}"
            )

        open_orders = await client.fetch_open_orders(symbol)
        results["status"]["fetch_open_orders"] = "success"
        print(f"  ✓ fetch_open_orders fetched: {len(open_orders)} order(s)")
        if open_orders:
            for o in open_orders:
                print(
                    f"  {o.get('datetime')} {o.get('id')} {o.get('clientOrderId')} {o.get('symbol')} side: {o.get('side')} amount: {o.get('amount')}"
                )

        closed_orders = await client.fetch_closed_orders(symbol)
        results["status"]["fetch_closed_orders"] = "success"
        print(f"  ✓ fetch_closed_orders fetched: {len(closed_orders)} order(s)")

        if order_id != "-1":
            cancelled = await client.cancel_order(order_id, symbol)
            results["status"]["cancel_order"] = "success"
            print(f"  ✓ Order cancelled: {order_id} {cancelled.get('status')}")

        cancelled_all = await client.cancel_all_orders(symbol)
        results["status"]["cancel_all_orders"] = "success"
        cancelled_count = 0
        for o in cancelled_all:
            if o.get("id") is not None:
                print(f"  ✓ cancel_all_orders {o.get('id')} {o.get('status')}")
                cancelled_count += 1
        print(f"  ✓ cancel_all_orders: {cancelled_count} orders")

        if is_testnet and config["market_type"] == "swap":
            order = await client.close_position(symbol, side="long", amount=amount)
            results["status"]["close_position"] = "success"

    except Exception as e:
        import traceback

        traceback.print_exc()
        error_msg = str(e)
        results["status"]["error"] = error_msg
        print(f"  ✗ Error: {exchange_name} {error_msg}")

    return results


async def test_exchange_methods(config: dict, mcp_url: str, mcp_api_key: str) -> dict:
    """Test all exchange methods with a single config."""
    exchange_name = config.get("exchange_name")

    client_config = {
        "exchange_name": exchange_name,
        "api_key": config.get("api_key"),
        "api_secret": config.get("secret"),
        "api_password": config.get("passphrase"),
        "is_testnet": config.get("is_testnet", False),
        "market_type": config.get("market_type"),
        "symbol": config.get("symbol"),
    }

    async with XchangeMcpClient(
        url=mcp_url, config=client_config, mcp_api_key=mcp_api_key
    ) as client:
        results = await test_full_cases(config, client)

    return results


def parse_args():
    all_names = sorted({c["exchange_name"] for c in user_configs})

    parser = argparse.ArgumentParser(
        description="Test XchangeMcpClient methods via MCP server."
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("MCP_SERVER_URL", "https://xchange-mcp.ezcoin.cc/mcp"),
        help="xchange-mcp server URL",
    )
    parser.add_argument(
        "--mcp-api-key",
        default=os.environ.get("MCP_API_KEY", ""),
        help="API key for xchange-mcp authentication",
    )
    parser.add_argument(
        "-e",
        "--exchange",
        metavar="EXCHANGE",
        help=(
            "Comma-separated exchange name(s) to test, or 'all'. "
            f"Available: {', '.join(all_names)}"
        ),
    )
    return parser.parse_args()


def resolve_exchanges(arg: str | None) -> list[str]:
    """Return the list of exchange names to run based on the -e argument."""
    all_names = sorted({c["exchange_name"] for c in user_configs})

    if arg is None:
        print("Available exchanges: " + ", ".join(all_names))
        raw = input("Enter exchange(s) to test (comma-separated, or 'all'): ").strip()
    else:
        raw = arg.strip()

    if raw.lower() == "all":
        return all_names

    selected = [e.strip() for e in raw.split(",") if e.strip()]
    unknown = [e for e in selected if e not in all_names]
    if unknown:
        print(f"Warning: unknown exchange(s) ignored: {', '.join(unknown)}")
    return [e for e in selected if e in all_names]


async def main():
    args = parse_args()
    test_exchange_names = resolve_exchanges(args.exchange)

    if not test_exchange_names:
        print("No valid exchanges selected. Exiting.")
        return

    print("=" * 60)
    print(f"Testing XchangeMcpClient Methods: {', '.join(test_exchange_names)}")
    print(f"MCP URL: {args.url}")
    print("=" * 60)

    all_results = []
    for config in user_configs:
        exchange_name = config.get("exchange_name")
        if exchange_name not in test_exchange_names:
            continue

        print(f"\nTesting {exchange_name} {config.get('market_type','')} {config['account_name']}...")

        if "market_type" not in config:
            config["market_type"] = "swap"
        if exchange_name in SPOT_ONLY_EXCHANGES:
            config["market_type"] = "spot"

        result = await test_exchange_methods(config, args.url, args.mcp_api_key)
        all_results.append(result)

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for result in all_results:
        print(f"\n{result['exchange']} ({result['account']}):")
        for method, status in result["status"].items():
            print(f"  - {method}: {status}")


if __name__ == "__main__":
    asyncio.run(main())
