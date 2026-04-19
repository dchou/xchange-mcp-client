"""Test script for Bybit margin trading via XchangeMcpClient.

Usage:
    python test_bybit.py --url https://xchange-mcp.ezcoin.cc/mcp
"""

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xchange_mcp_client import XchangeMcpClient

from dotenv import load_dotenv

load_dotenv(".env")


async def main_async():
    parser = argparse.ArgumentParser(
        description="Test xchange-mcp via xchange-compatible API"
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
    args = parser.parse_args()

    config = {
        "exchange_name": "bybit",
        "api_key": os.environ.get("bbDDemo_API_KEY", ""),
        "api_secret": os.environ.get("bbDDemo_SECRET_KEY", ""),
        "is_testnet": True,
        "market_type": "margin",
        "symbol": "BTC/USDT",
        "amount": 0.002,
    }

    print("=" * 60)
    print(f"Testing xchange-mcp via xchange-compatible API")
    print(f"URL: {args.url}")
    print("=" * 60)

    async with XchangeMcpClient(
        url=args.url,
        config={
            "exchange_name": config["exchange_name"],
            "api_key": config["api_key"],
            "api_secret": config["api_secret"],
            "is_testnet": config["is_testnet"],
            "market_type": config["market_type"],
        },
        mcp_api_key=args.mcp_api_key,
    ) as client:
        print(f"\n1. Init exchange... (done in __init__)")
        print(f"Session ID: {client.session_id}")

        print(f"\n2. Get borrow rate...")
        result = await client.get_borrow_rate("BTC")
        print(f"get_borrow_rate: {result}")

        print(f"\n3. Get borrowed amount...")
        result = await client.get_borrowed_amount("BTC")
        print(f"get_borrowed_amount: {result}")

        print(f"\n4. Get borrowed records...")
        result = await client.get_borrowed_records("BTC")
        print(f"get_borrowed_records: {result}")

        print(f"\n5. Check is_testnet...")
        is_testnet = await client.get_is_testnet()
        print(f"is_testnet: {is_testnet}")

        if is_testnet:
            print(f"\n6. Fetch balance...")
            result = await client.fetch_balance()
            print(f"fetch_balance: {result}")

            print(f"\n7. Create market order (sell)...")
            result = await client.create_market_order(
                symbol=config["symbol"],
                side="sell",
                amount=config["amount"],
            )
            print(f"create_market_order: {result}")
            order_id = result.get("id")

            if order_id and order_id != "-1":
                await asyncio.sleep(1)
                print(f"\n8. Fetch order...")
                result = await client.fetch_order(
                    id=order_id,
                    symbol=config["symbol"],
                )
                print(f"fetch_order: {result}")

            print(f"\n9. Get borrowed amount after trade...")
            borrowed_result = await client.get_borrowed_amount("BTC")
            print(f"get_borrowed_amount: {borrowed_result}")

            borrowed_amount = (
                borrowed_result.get("borrowed_amount", 0)
                if isinstance(borrowed_result, dict)
                else 0
            )

            if borrowed_amount and borrowed_amount > 0:
                print(f"\n10. Create market order (buy) to repay...")
                result = await client.create_market_order(
                    symbol=config["symbol"],
                    side="buy",
                    amount=borrowed_amount,
                )
                print(f"create_market_order: {result}")
                await asyncio.sleep(1)

                print(f"\n11. Get borrowed amount after repay...")
                result = await client.get_borrowed_amount("BTC")
                print(f"get_borrowed_amount: {result}")

        print(f"\n12. Close exchange... (done in __exit__)")
        print(f"close_exchange: {{'success': True}}")

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
