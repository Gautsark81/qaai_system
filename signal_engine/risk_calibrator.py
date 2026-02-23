# signal_engine/risk_calibrator.py

from typing import Dict, Any
import pandas as pd


class RiskCalibrator:
    """
    Adaptive risk calibration system that tunes position sizing,
    stop-loss/take-profit levels, and exposure based on feedback.
    """

    def __init__(self, base_position_size: float = 1.0):
        self.base_position_size = base_position_size

    def calibrate(self, trade_log: pd.DataFrame) -> Dict[str, Any]:
        """
        Adjusts risk parameters based on trade performance.

        Parameters
        ----------
        trade_log : pd.DataFrame
            Must contain at least 'pnl'.

        Returns
        -------
        dict
            Example: {'position_size': 1.2, 'stop_loss_factor': 0.95, 'take_profit_factor': 1.05}
        """
        if trade_log is None or trade_log.empty:
            return {
                "position_size": self.base_position_size,
                "stop_loss_factor": 1.0,
                "take_profit_factor": 1.0,
            }

        avg_pnl = trade_log["pnl"].mean() if "pnl" in trade_log.columns else 0

        # Simple rule: scale position size based on profitability
        adjustment_factor = 1.0 + (avg_pnl / 1000.0)
        adjustment_factor = max(0.5, min(2.0, adjustment_factor))

        return {
            "position_size": self.base_position_size * adjustment_factor,
            "stop_loss_factor": 1.0 if avg_pnl >= 0 else 0.95,
            "take_profit_factor": 1.0 if avg_pnl >= 0 else 1.05,
        }
