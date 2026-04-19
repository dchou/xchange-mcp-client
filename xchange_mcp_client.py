import httpx
import json
from typing import Optional, Dict, Any


class XchangeMcpClient:
    """HTTP-based MCP client (like the telegram bot).

    Provides a wrapper API similar to xchange's ExchangeClient for easy migration.
    """

    def __init__(self, url: str, config: dict = None, mcp_api_key: str = ""):
        """Initialize XchangeMcpClient.

        Args:
            url: MCP server URL
            config: Exchange configuration dict (same as xchange.ExchangeClient)
            mcp_api_key: Optional API key for MCP server authentication
        """
        self.url = url
        self.session_id = None
        self.mcp_session_id = None
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.mcp_api_key = mcp_api_key
        self._id = 1

        config = config or {}
        self.exchange_name = config.get("exchange_name", "")
        self.api_key = config.get("api_key", "")
        self.api_secret = config.get("api_secret", "")
        self.api_password = config.get("api_password")
        self.is_testnet = config.get("is_testnet", False)
        self.market_type = config.get("market_type", "swap")
        self.exchange_id = config.get("exchange_id")
        self.user_id = config.get("user_id")
        self.sub_account_id = config.get("sub_account_id")
        self.symbol = config.get("symbol")
        self.leverage = config.get("leverage")
        self.margin_mode = config.get("margin_mode")
        self.position_mode = config.get("position_mode")

    async def __aenter__(self):
        await self._initialize()
        if self.exchange_name:
            await self.connect()
        return self

    async def __aexit__(self, *args):
        try:
            await self.close()
        except Exception:
            pass
        await self.client.aclose()

    async def _next_id(self):
        self._id += 1
        return self._id

    async def _initialize(self):
        """Initialize MCP session."""
        resp = await self.client.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": await self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "xchange-mcp-client", "version": "1.0"},
                },
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )

        if resp.status_code != 200:
            raise Exception(f"Initialize failed: {resp.status_code} {resp.text}")

        self.mcp_session_id = resp.headers.get("mcp-session-id")
        if not self.mcp_session_id:
            raise Exception("Failed to get MCP session ID")

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call an MCP tool."""
        response = await self.client.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": await self._next_id(),
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": self.mcp_session_id,
            },
        )

        if response.status_code != 200:
            raise Exception(f"MCP call failed: {response.status_code} {response.text}")

        text = response.text
        for line in text.split("\n"):
            if line.startswith("data:"):
                data = line[5:].strip()
                if data:
                    try:
                        result = json.loads(data)
                        if "result" in result:
                            content = result["result"].get("content", [])
                            if content and content[0].get("type") == "text":
                                return json.loads(content[0]["text"])
                        if "error" in result:
                            return {"success": False, "error": result["error"]}
                    except:
                        pass

        return {"success": False, "error": "No response from MCP server"}

    def _parse_result(self, result):
        """Parse MCP tool result, handling None and error cases."""
        if result is None:
            return {"success": False, "error": "No response from MCP server"}
        if not isinstance(result, dict):
            return {"success": False, "error": f"Invalid response: {result}"}
        return result

    # ---------------------------------------------------------------------------
    # Connection methods
    # ---------------------------------------------------------------------------

    async def connect(self) -> bool:
        """Connect to exchange using configured credentials.

        Returns:
            True if connection successful, False otherwise.
        """
        if not self.exchange_name:
            raise ValueError("exchange_name is required")

        result = await self.call_tool(
            "init_exchange",
            {
                "exchange_name": self.exchange_name,
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "api_password": self.api_password,
                "is_testnet": self.is_testnet,
                "market_type": self.market_type,
                "exchange_id": self.exchange_id,
                "user_id": self.user_id,
                "sub_account_id": self.sub_account_id,
                "symbol": self.symbol,
                "leverage": self.leverage,
                "margin_mode": self.margin_mode,
                "position_mode": self.position_mode,
            },
        )

        if result.get("success"):
            self.session_id = result.get("session_id")
            return True
        return False

    async def close(self):
        """Close the exchange connection."""
        if self.session_id:
            try:
                await self.call_tool("close_exchange", {"session_id": self.session_id})
            except Exception:
                pass
            self.session_id = None

    # ---------------------------------------------------------------------------
    # Account methods
    # ---------------------------------------------------------------------------

    async def fetch_balance(self, params: Optional[Dict] = {}) -> Dict[str, Any]:
        """Get account balance."""
        result = await self.call_tool("fetch_balance", {"session_id": self.session_id})
        return result.get("balance", result)

    async def fetch_positions(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Fetch open positions."""
        result = await self.call_tool(
            "fetch_positions",
            {
                "session_id": self.session_id,
                "symbol": symbol,
            },
        )
        return result.get("positions", result)

    # ---------------------------------------------------------------------------
    # Order methods
    # ---------------------------------------------------------------------------

    async def create_order(
        self,
        symbol: str,
        type: str,
        side: str,
        amount: float,
        price: Optional[float] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create an order (market or limit)."""
        args = {
            "session_id": self.session_id,
            "symbol": symbol,
            "order_type": type,
            "side": side,
            "amount": amount,
        }
        if price is not None:
            args["price"] = price
        if params:
            args["params"] = params

        result = await self.call_tool("create_order", args)
        return result.get("order", result)

    async def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a limit order."""
        return await self.create_order(symbol, "limit", side, amount, price, params)

    async def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a market order."""
        return await self.create_order(symbol, "market", side, amount, None, params)

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an open order."""
        result = await self.call_tool(
            "cancel_order",
            {
                "session_id": self.session_id,
                "order_id": order_id,
                "symbol": symbol,
            },
        )
        return result.get("order", result)

    async def cancel_all_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Cancel all open orders."""
        result = await self.call_tool(
            "cancel_all_orders",
            {
                "session_id": self.session_id,
                "symbol": symbol,
            },
        )
        return result.get("cancelled", result)

    async def fetch_order(
        self,
        id: str,
        symbol: Optional[str] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Get order details."""
        result = await self.call_tool(
            "fetch_order",
            {
                "session_id": self.session_id,
                "order_id": id,
                "symbol": symbol,
            },
        )
        return result.get("order", result)

    async def fetch_open_orders(
        self,
        symbol: Optional[str] = None,
        params: Optional[Dict] = None,
    ) -> list:
        """Fetch open orders."""
        result = await self.call_tool(
            "fetch_open_orders",
            {
                "session_id": self.session_id,
                "symbol": symbol,
            },
        )
        return result.get("orders", [])

    async def fetch_closed_orders(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict] = None,
    ) -> list:
        """Fetch closed/filled orders."""
        args = {"session_id": self.session_id}
        if symbol:
            args["symbol"] = symbol
        result = await self.call_tool("fetch_closed_orders", args)
        return result.get("orders", [])

    async def close_position(
        self,
        symbol: str,
        side: str,
        amount: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Close an open position."""
        result = await self.call_tool(
            "close_position",
            {
                "session_id": self.session_id,
                "symbol": symbol,
                "side": side,
                "amount": amount,
            },
        )
        return result.get("order", result)

    async def fetch_my_trades(
        self,
        symbol: Optional[str] = None,
        limit: int = 50,
        params: Optional[Dict] = None,
    ) -> list:
        """Fetch personal trade history."""
        result = await self.call_tool(
            "fetch_my_trades",
            {
                "session_id": self.session_id,
                "symbol": symbol,
                "limit": limit,
            },
        )
        return result.get("trades", [])

    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Set leverage for a symbol."""
        result = await self.call_tool(
            "set_leverage",
            {
                "session_id": self.session_id,
                "symbol": symbol,
                "leverage": leverage,
            },
        )
        return result.get("result", result)

    # ---------------------------------------------------------------------------
    # Market data methods
    # ---------------------------------------------------------------------------

    async def fetch_ticker(
        self, symbol: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Get current ticker for symbol."""
        result = await self.call_tool(
            "fetch_ticker",
            {
                "session_id": self.session_id,
                "symbol": symbol,
            },
        )
        return result.get("ticker", result)

    async def fetch_order_book(
        self,
        symbol: str,
        limit: Optional[int] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Get order book for symbol."""
        result = await self.call_tool(
            "fetch_order_book",
            {
                "session_id": self.session_id,
                "symbol": symbol,
                "limit": limit,
            },
        )
        return result.get("order_book", result)

    async def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        since: Optional[int] = None,
        limit: Optional[int] = None,
        params: Optional[Dict] = None,
    ) -> list:
        """Fetch OHLCV (candlestick) data."""
        result = await self.call_tool(
            "fetch_ohlcv",
            {
                "session_id": self.session_id,
                "symbol": symbol,
                "timeframe": timeframe,
                "since": since,
                "limit": limit,
            },
        )
        return result.get("ohlcv", [])

    # ---------------------------------------------------------------------------
    # Margin methods
    # ---------------------------------------------------------------------------

    async def get_borrow_rate(self, asset: str) -> Dict[str, Any]:
        """Get borrow rate for a margin asset."""
        result = await self.call_tool(
            "get_borrow_rate",
            {
                "session_id": self.session_id,
                "asset": asset,
            },
        )
        return result.get("borrow_rate", result)

    async def get_borrowed_amount(self, asset: str) -> Dict[str, Any]:
        """Get borrowed amount for a margin asset."""
        result = await self.call_tool(
            "get_borrowed_amount",
            {
                "session_id": self.session_id,
                "asset": asset,
            },
        )
        return result.get("borrowed_amount", result)

    async def get_borrowed_records(self, asset: str) -> list:
        """Get borrowing records for a margin asset."""
        result = await self.call_tool(
            "get_borrowed_records",
            {
                "session_id": self.session_id,
                "asset": asset,
            },
        )
        return result.get("borrowed_records", [])

    async def fetch_margin_config(
        self,
        symbol: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch margin trading configuration."""
        result = await self.call_tool(
            "fetch_margin_config",
            {
                "session_id": self.session_id,
                "symbol": symbol,
            },
        )
        return result.get("margin_config", result)

    async def get_is_testnet(self) -> bool:
        """Check if the session is using testnet."""
        result = await self.call_tool(
            "is_testnet",
            {
                "session_id": self.session_id,
            },
        )
        return result.get("is_testnet", False)

    # ---------------------------------------------------------------------------
    # Additional methods
    # ---------------------------------------------------------------------------

    async def get_filled_orders(
        self,
        symbol: Optional[str] = None,
        since: Optional[int] = None,
    ) -> list:
        """Get filled orders with full trade history."""
        result = await self.call_tool(
            "get_filled_orders",
            {
                "session_id": self.session_id,
                "symbol": symbol,
                "since": since,
            },
        )
        return result.get("filled_orders", [])

    async def get_closed_pnls(
        self,
        symbol: Optional[str] = None,
    ) -> list:
        """Get closed PnL history."""
        result = await self.call_tool(
            "get_closed_pnls",
            {
                "session_id": self.session_id,
                "symbol": symbol,
            },
        )
        return result.get("pnls", [])
