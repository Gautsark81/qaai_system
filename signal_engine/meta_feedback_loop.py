# signal_engine/meta_feedback_loop.py

from typing import Dict, Any
import pandas as pd


class MetaFeedbackLoop:
    """
    Meta-learning feedback loop that evaluates trades,
    updates signal quality scores, and adjusts strategy parameters in real time.
    """

    def __init__(self, signal_engine=None, quality_control=None):
        self.signal_engine = signal_engine
        self.quality_control = quality_control

    def register_trade_result(self, trade_info: Dict[str, Any]):
        """
        Accepts executed trade info and updates feedback systems.

        Parameters
        ----------
        trade_info : dict
            Must contain 'symbol', 'pnl', and 'signal' keys at minimum.
        """
        if self.quality_control:
            try:
                self.quality_control.update_metrics(trade_info)
            except AttributeError:
                pass  # quality_control may be a simple function or None

    def evaluate_signals(self, trade_log: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluates the quality of recent signals and returns scored DataFrame.

        Parameters
        ----------
        trade_log : pd.DataFrame
            Must contain 'symbol', 'pnl', and 'signal'.

        Returns
        -------
        pd.DataFrame
            Contains quality scores and any strategy adjustment recommendations.
        """
        if self.quality_control and hasattr(
            self.quality_control, "evaluate_signal_quality"
        ):
            return self.quality_control.evaluate_signal_quality(trade_log)
        return trade_log

    def auto_tune(self, trade_log: pd.DataFrame) -> Dict[str, Any]:
        """
        Uses quality metrics to auto-tune buy/sell thresholds.

        Returns
        -------
        dict
            Example: {'buy_threshold': 0.6, 'sell_threshold': 0.4}
        """
        if self.quality_control and hasattr(
            self.quality_control, "auto_tune_thresholds"
        ):
            try:
                return self.quality_control.auto_tune_thresholds(
                    trade_log, current_buy=0.5, current_sell=0.5
                )
            except TypeError:
                # If function doesn't match expected args
                return {}
        return {}
