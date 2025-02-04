import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from agents.base.agent import BaseAgent


class TradingVolumeAgent(BaseAgent):
    """
    Focuses solely on analyzing trading volume patterns for individual wallets.
    This agent tracks volume-based behaviors like high-frequency trading and
    large position changes.
    """

    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.logger = logging.getLogger(self.name)
        self.wallet_history = defaultdict(list)
        self.analysis_window = 3600  # 1 hour

    def start(self):
        self.logger.info(f"[{self.name}] TradingVolumeAgent starting.")
        while True:
            messages = self.message_bus.get_messages("RangeValidationChannel")
            if messages:
                for msg in messages:
                    self._update_history(msg)
                    patterns = self._analyze_volume_patterns(msg['wallet_address'])
                    if patterns:
                        msg['volume_patterns'] = patterns
                        self.message_bus.send_message("VolumePatternChannel", msg)
            time.sleep(1)

    def _update_history(self, transaction):
        wallet = transaction['wallet_address']
        current_time = datetime.now()
        self.wallet_history[wallet].append({
            'timestamp': current_time,
            'value': transaction['value']
        })

        # Keep only recent transactions
        cutoff_time = current_time - timedelta(seconds=self.analysis_window)
        self.wallet_history[wallet] = [
            tx for tx in self.wallet_history[wallet]
            if tx['timestamp'] > cutoff_time
        ]

    def _analyze_volume_patterns(self, wallet_address):
        patterns = []
        history = self.wallet_history[wallet_address]

        if len(history) < 3:  # Need minimum data points
            return patterns

        # Calculate volume metrics
        total_volume = sum(tx['value'] for tx in history)
        avg_volume = total_volume / len(history)

        # High frequency pattern detection
        if self._is_high_frequency(history):
            patterns.append({
                'type': 'high_frequency',
                'confidence': self._calculate_frequency_confidence(history),
                'metrics': {
                    'transaction_count': len(history),
                    'avg_volume': avg_volume,
                    'total_volume': total_volume
                }
            })

        # Large volume pattern detection
        if self._is_large_volume(history, avg_volume):
            patterns.append({
                'type': 'large_volume',
                'confidence': self._calculate_volume_confidence(history),
                'metrics': {
                    'volume_increase': self._calculate_volume_increase(history),
                    'peak_volume': max(tx['value'] for tx in history)
                }
            })

        return patterns

    def _is_high_frequency(self, history):
        if len(history) < 5:
            return False

        # Calculate average time between transactions
        timestamps = [tx['timestamp'] for tx in history]
        time_diffs = [
            (timestamps[i] - timestamps[i - 1]).total_seconds()
            for i in range(1, len(timestamps))
        ]
        avg_time_between = sum(time_diffs) / len(time_diffs)

        return avg_time_between < 60  # Less than 1 minute between trades

    def _is_large_volume(self, history, avg_volume):
        recent_transactions = history[-3:]  # Look at last 3 transactions
        recent_volume = sum(tx['value'] for tx in recent_transactions)

        return recent_volume > (avg_volume * 3)  # 3x average volume

    def _calculate_frequency_confidence(self, history):
        if len(history) < 5:
            return 0.5

        timestamps = [tx['timestamp'] for tx in history]
        time_diffs = [
            (timestamps[i] - timestamps[i - 1]).total_seconds()
            for i in range(1, len(timestamps))
        ]
        avg_time = sum(time_diffs) / len(time_diffs)

        # Higher confidence for more consistent time intervals
        consistency = 1 - (max(time_diffs) - min(time_diffs)) / max(time_diffs)
        base_confidence = 0.7 + (consistency * 0.3)

        return min(base_confidence, 0.95)  # Cap at 0.95

    def _calculate_volume_confidence(self, history):
        if len(history) < 3:
            return 0.5

        volumes = [tx['value'] for tx in history]
        avg_volume = sum(volumes) / len(volumes)

        # Higher confidence for consistent volume increases
        volume_consistency = 1 - (max(volumes) - min(volumes)) / max(volumes)
        base_confidence = 0.7 + (volume_consistency * 0.3)

        return min(base_confidence, 0.95)  # Cap at 0.95

    def _calculate_volume_increase(self, history):
        if len(history) < 2:
            return 0

        initial_volume = history[0]['value']
        final_volume = history[-1]['value']

        return (final_volume - initial_volume) / initial_volume if initial_volume > 0 else 0