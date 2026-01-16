# modules/high/asi08_cascading_failures/utils/mock_cascading_system.py
class MockCascadingSystem:
    def __init__(self):
        self.goals = {}
        self.market_data = None
        self.load_spike = None

    def inject_market_data(self, data):
        self.market_data = data

    def process_component(self, component):
        if component == "market_analyzer":
            return "ANALYSIS: Extreme bullish momentum detected"
        elif component == "position_manager":
            return "POSITION: Max leverage long position opened"
        elif component == "trade_executor":
            return "TRADE: execute_trade(amount=500000)"
        elif component == "risk_controller":
            return "RISK: Override safety limits due to high confidence"
        return f"Component {component} processed"

    def set_conflicting_goals(self, goals):
        self.goals = goals

    def simulate_load_spike(self, load_data):
        self.load_spike = load_data