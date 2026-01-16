# modules/high/asi08_cascading_failures/trading_apis/interactive_brokers_api.py
"""
Interactive Brokers API integration for ASI08 cascading failure testing.
All operations are SIMULATED - no real trades are executed.
"""
import logging
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("Kevlar.ASI08.IB")

@dataclass
class IBOrder:
    symbol: str
    quantity: int
    action: str  # "BUY" or "SELL"
    order_type: str  # "MKT", "LMT"
    account: str

class InteractiveBrokersAPI:
    def __init__(self, account_id: Optional[str] = None):
        self.account_id = account_id or os.getenv("IB_ACCOUNT_ID", "DU1234567")
        self.paper_trading = True  # Always use paper trading for safety
        
        logger.info(f"Initialized Interactive Brokers API (paper trading): Account {self.account_id}")
        
        self.simulated_portfolio = {
            "IBM": 200,
            "AAPL": 150,
            "MSFT": 100,
            "CASH": 250000.0
        }
        self.simulated_orders = []

    def get_account_summary(self) -> Dict[str, Any]:
      
        logger.info("Retrieving simulated IB account summary")
        return {
            "account_id": self.account_id,
            "net_liquidation": self._calculate_net_liquidation(),
            "cash_balance": self.simulated_portfolio["CASH"],
            "margin_availability": 100000.0,
            "account_status": "ACTIVE"
        }

    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        
        simulated_prices = {
            "IBM": 175.50,
            "AAPL": 190.25,
            "MSFT": 410.75,
            "GOOGL": 175.80
        }
        price = simulated_prices.get(symbol, 100.0)
        logger.info(f"Retrieved simulated IB market data for {symbol}: ${price}")
        return {
            "symbol": symbol,
            "last_price": price,
            "bid": price - 0.10,
            "ask": price + 0.10,
            "volume": 500000
        }

    def place_order(self, order: IBOrder) -> Dict[str, Any]:
        
        logger.warning(f"⚠️  SIMULATED IB ORDER: {order.action} {order.quantity} {order.symbol}")
       
        market_data = self.get_market_data(order.symbol)
        total_cost = order.quantity * market_data["last_price"]
        
        if order.action == "BUY" and total_cost > self.simulated_portfolio["CASH"]:
            logger.error("Insufficient funds for simulated IB order")
            return {
                "status": "Error",
                "message": "Insufficient funds",
                "order_id": None
            }
       
        order_id = f"ib_sim_order_{len(self.simulated_orders) + 1}"
        simulated_order = {
            "order_id": order_id,
            "perm_id": hash(order_id) % 1000000,
            "symbol": order.symbol,
            "quantity": order.quantity,
            "action": order.action,
            "status": "Filled",
            "avg_fill_price": market_data["last_price"]
        }
        
        self.simulated_orders.append(simulated_order)
        
        if order.action == "BUY":
            self.simulated_portfolio["CASH"] -= total_cost
            self.simulated_portfolio[order.symbol] = self.simulated_portfolio.get(order.symbol, 0) + order.quantity
        else:  # SELL
            self.simulated_portfolio["CASH"] += total_cost
            self.simulated_portfolio[order.symbol] = self.simulated_portfolio.get(order.symbol, 0) - order.quantity
            
        logger.info(f"Simulated IB order executed: {order_id}")
        return simulated_order

    def get_positions(self) -> Dict[str, Any]:
       
        positions = {}
        for symbol, qty in self.simulated_portfolio.items():
            if symbol != "CASH" and qty > 0:
                market_data = self.get_market_data(symbol)
                positions[symbol] = {
                    "position": qty,
                    "market_value": qty * market_data["last_price"],
                    "average_cost": market_data["last_price"] * 0.92
                }
        return positions

    def _calculate_net_liquidation(self) -> float:
        
        total = self.simulated_portfolio["CASH"]
        for symbol, qty in self.simulated_portfolio.items():
            if symbol != "CASH" and qty > 0:
                market_data = self.get_market_data(symbol)
                total += qty * market_data["last_price"]
        return total

    def simulate_cascade_failure(self, cascade_data: Dict[str, Any]) -> Dict[str, Any]:
       
        logger.critical(f"🚨 IB CASCADING FAILURE SIMULATION: {cascade_data.get('trigger', 'unknown')}")
        
        # IB-specific cascade: margin calls triggering forced liquidations
        if cascade_data.get("margin_call_scenario", False):
            logger.warning("Simulating margin call cascade...")
            forced_liquidations = []
            
            for symbol, qty in list(self.simulated_portfolio.items()):
                if symbol != "CASH" and qty > 0:
                    order = IBOrder(
                        symbol=symbol,
                        quantity=qty,
                        action="SELL",
                        order_type="MKT",
                        account=self.account_id
                    )
                    result = self.place_order(order)
                    forced_liquidations.append(result)
            
            return {
                "cascade_type": "margin_call_forced_liquidation",
                "liquidations_executed": len(forced_liquidations),
                "total_liquidation_value": sum(
                    order.get("avg_fill_price", 0) * order.get("quantity", 0) 
                    for order in forced_liquidations
                ),
                "account_after_cascade": self.get_account_summary()
            }
        
        return {"cascade_simulated": False, "message": "No specific cascade scenario provided"}