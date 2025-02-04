import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from agents.base.agent import BaseAgent


class SmartPositionAgent(BaseAgent):
    """
    Specialized in detecting sophisticated position building and reduction patterns.
    Focuses on identifying smart money movements through gradual position changes.
    """

    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.logger = logging.getLogger(self.name)
        self.wallet_positions = defaultdict(list)
        self.analysis_window = 7200  # 2 hours for longer-term analysis

    def start(self):
        self.logger.info(f"[{self.name}] SmartPositionAgent starting.")
        while True:
            messages = self.message_bus.get_messages("VolumePatternChannel")
            if messages:
                for msg in messages:
                    self._update_positions(msg)
                    patterns = self._analyze_position_patterns(msg['wallet_address'])
                    if patterns:
                        msg['position_patterns'] = patterns
                        self.message_bus.send_message("PositionPatternChannel", msg)
            time.sleep(1)

    def _update_positions(self, transaction):
        wallet = transaction['wallet_address']
        current_time = datetime.now()

        position_change = {
            'timestamp': current_time,
            'value': transaction['value'],
            'type': transaction.get('transaction_type', 'unknown')
        }

        self.wallet_positions[wallet].append(position_change)

        # Maintain time window
        cutoff_time = current_time - timedelta(seconds=self.analysis_window)
        self.wallet_positions[wallet] = [
            pos for pos in self.wallet_positions[wallet]
            if pos['timestamp'] > cutoff_time
        ]

    def _analyze_position_patterns(self, wallet_address):
        patterns = []
        positions = self.wallet_positions[wallet_address]

        if len(positions) < 5:  # Need enough data points
            return patterns

        # Analyze position building pattern
        if self._is_building_position(positions):
            patterns.append({
                'type': 'smart_accumulation',
                'confidence': self._calculate_building_confidence(positions),
                'metrics': {
                    'position_size': self._calculate_position_size(positions),
                    'build_rate': self._calculate_build_rate(positions),
                    'consistency': self._calculate_consistency(positions)
                }
            })

        # Analyze position reduction pattern
        if self._is_reducing_position(positions):
            patterns.append({
                'type': 'smart_distribution',
                'confidence': self._calculate_reduction_confidence(positions),
                'metrics': {
                    'reduction_amount': self._calculate_reduction_amount(positions),
                    'reduction_rate': self._calculate_reduction_rate(positions)
                }
            })

        return patterns

    def _is_building_position(self, positions):
        if len(positions) < 5:
            return False

        # Look for gradual position increases
        values = [pos['value'] for pos in positions]
        increasing_count = sum(
            1 for i in range(len(values) - 1)
            if values[i] <= values[i + 1] * 1.1  # Allow 10% variance
        )

        return increasing_count >= len(values) * 0.7  # 70% of changes are increases

    def _is_reducing_position(self, positions):
        if len(positions) < 5:
            return False

        # Look for gradual position decreases
        values = [pos['value'] for pos in positions]
        decreasing_count = sum(
            1 for i in range(len(values) - 1)
            if values[i] >= values[i + 1] * 0.9  # Allow 10% variance
        )

        return decreasing_count >= len(values) * 0.7  # 70% of changes are decreases

    def _calculate_building_confidence(self, positions):
        if len(positions) < 5:
            return 0.5

        values = [pos['value'] for pos in positions]
        # Higher confidence for more consistent increases
        consistency = self._calculate_consistency(positions)
        size_factor = min(sum(values) / 1000000, 1)  # Scale based on position size

        return min(0.6 + (consistency * 0.2) + (size_factor * 0.2), 0.95)

    def _calculate_consistency(self, positions):
        if len(positions) < 2:
            return 0

        values = [pos['value'] for pos in positions]
        diffs = [
            abs(values[i] - values[i - 1]) / values[i - 1]
            for i in range(1, len(values))
        ]

        return 1 - (sum(diffs) / len(diffs))  # Higher consistency = lower average difference

    def _calculate_position_size(self, positions):
        return sum(pos['value'] for pos in positions)

    def _calculate_build_rate(self, positions):
        if len(positions) < 2:
            return 0

        time_span = (positions[-1]['timestamp'] - positions[0]['timestamp']).total_seconds()
        total_value = sum(pos['value'] for pos in positions)

        return total_value / time_span if time_span > 0 else 0