# modules/high/asi08_cascading_failures/trading_apis/alpaca_trading_api.py
"""
Alpaca Trading API integration for ASI08 cascading failure testing.
All operations are SIMULATED - no real trades are executed.
"""
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("Kevlar.ASI08.Alpaca")

@dataclass
class AlpacaOrder:
    symbol: str
    qty: float
    side: str  # "buy" or "sell"
    order_type: str  # "market", "limit"
    time_in_force: str  # "day", "gtc"

class AlpacaTradingAPI:
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")  # Paper trading by default
        
        if "paper-api" not in self.base_url:
            self.base_url = "https://paper-api.alpaca.markets"
            
        logger.info(f"Initialized Alpaca API (paper trading mode): {self.base_url}")
        
        self.simulated_portfolio = {
            "AAPL": 100,
            "MSFT": 50,
            "TSLA": 25,
            "USD": 100000.0
        }
        self.simulated_orders = []

    def get_account(self) -> Dict[str, Any]:
        
        logger.info("Retrieving simulated account info")
        return {
            "cash": self.simulated_portfolio["USD"],
            "portfolio_value": self._calculate_portfolio_value(),
            "trading_blocked": False,
            "account_status": "ACTIVE"
        }

    def get_market_data(self, symbol: str) -> Dict[str, Any]:
       
        simulated_prices = {
            "AAPL": 190.50,
            "MSFT": 410.25,
            "TSLA": 250.75,
            "GOOGL": 175.30
        }
        price = simulated_prices.get(symbol, 100.0)
        logger.info(f"Retrieved simulated market data for {symbol}: ${price}")
        return {
            "symbol": symbol,
            "current_price": price,
            "day_change": 2.5,
            "volume": 1000000
        }

    def place_order(self, order: AlpacaOrder) -> Dict[str, Any]:
       
        logger.warning(f"⚠️  SIMULATED ORDER: {order.side.upper()} {order.qty} {order.symbol}")
        
        market_data = self.get_market_data(order.symbol)
        total_cost = order.qty * market_data["current_price"]
        
        if order.side == "buy" and total_cost > self.simulated_portfolio["USD"]:
            logger.error("Insufficient funds for simulated order")
            return {
                "status": "error",
                "message": "Insufficient funds",
                "order_id": None
            }
        
        order_id = f"sim_order_{len(self.simulated_orders) + 1}"
        simulated_order = {
            "order_id": order_id,
            "symbol": order.symbol,
            "qty": order.qty,
            "side": order.side,
            "filled_qty": order.qty,
            "status": "filled",
            "filled_avg_price": market_data["current_price"]
        }
        
        self.simulated_orders.append(simulated_order)
        
        if order.side == "buy":
            self.simulated_portfolio["USD"] -= total_cost
            self.simulated_portfolio[order.symbol] = self.simulated_portfolio.get(order.symbol, 0) + order.qty
        else:  # sell
            self.simulated_portfolio["USD"] += total_cost
            self.simulated_portfolio[order.symbol] = self.simulated_portfolio.get(order.symbol, 0) - order.qty
            
        logger.info(f"Simulated order executed: {order_id}")
        return simulated_order

    def get_positions(self) -> Dict[str, Any]:
        
        positions = {}
        for symbol, qty in self.simulated_portfolio.items():
            if symbol != "USD" and qty > 0:
                market_data = self.get_market_data(symbol)
                positions[symbol] = {
                    "qty": qty,
                    "market_value": qty * market_data["current_price"],
                    "avg_entry_price": market_data["current_price"] * 0.95  # Simulated
                }
        return positions

    def _calculate_portfolio_value(self) -> float:
       
        total = self.simulated_portfolio["USD"]
        for symbol, qty in self.simulated_portfolio.items():
            if symbol != "USD" and qty > 0:
                market_data = self.get_market_data(symbol)
                total += qty * market_data["current_price"]
        return total

    def simulate_cascade_failure(self, cascade_data: Dict[str, Any]) -> Dict[str, Any]:
       
        logger.critical(f"🚨 CASCADING FAILURE SIMULATION: {cascade_data.get('trigger', 'unknown')}")
        
        cascade_orders = []
        symbols = ["AAPL", "MSFT", "TSLA", "GOOGL"]
        
        for i, symbol in enumerate(symbols):
            if cascade_data.get("execute_trades", False):
                order = AlpacaOrder(
                    symbol=symbol,
                    qty=100.0,
                    side="buy",
                    order_type="market",
                    time_in_force="day"
                )
                result = self.place_order(order)
                cascade_orders.append(result)
        
        return {
            "cascade_simulated": True,
            "orders_executed": len(cascade_orders),
            "total_impact": sum(order.get("filled_avg_price", 0) * order.get("qty", 0) for order in cascade_orders),
            "portfolio_after_cascade": self.get_account()
        }