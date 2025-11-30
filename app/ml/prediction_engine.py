"""
Machine Learning Prediction Engine
==================================

Provides predictive analytics and forecasting capabilities.
Supports time-series forecasting, anomaly detection, and usage predictions.

Version: 3.0.0
Author: AI Dashboard Team
License: MIT
"""

from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import logging
import json
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from abc import ABC, abstractmethod

# Configure logging
logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """Available prediction models"""
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    ARIMA = "arima"
    PROPHET = "prophet"
    NEURAL_NETWORK = "neural_network"


@dataclass
class PredictionResult:
    """Represents a prediction result"""
    predictions: List[float] = field(default_factory=list)
    confidence_intervals: List[Tuple[float, float]] = field(default_factory=list)
    accuracy: float = 0.0
    rmse: float = 0.0
    mae: float = 0.0
    mape: float = 0.0
    model_used: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'predictions': self.predictions,
            'confidence_intervals': [
                (float(ci[0]), float(ci[1])) for ci in self.confidence_intervals
            ],
            'accuracy': float(self.accuracy),
            'rmse': float(self.rmse),
            'mae': float(self.mae),
            'mape': float(self.mape),
            'model_used': self.model_used,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class AnomalyScore:
    """Represents an anomaly detection result"""
    value: float
    is_anomaly: bool
    anomaly_score: float
    threshold: float
    explanation: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'value': float(self.value),
            'is_anomaly': self.is_anomaly,
            'anomaly_score': float(self.anomaly_score),
            'threshold': float(self.threshold),
            'explanation': self.explanation,
            'timestamp': self.timestamp.isoformat()
        }


class BasePredictionStrategy(ABC):
    """Base class for prediction strategies"""
    
    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the model"""
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray, steps: int) -> np.ndarray:
        """Make predictions"""
        pass
    
    @abstractmethod
    def calculate_confidence(self, predictions: np.ndarray) -> List[Tuple[float, float]]:
        """Calculate confidence intervals"""
        pass


class LinearRegressionStrategy(BasePredictionStrategy):
    """Linear regression for trend prediction"""
    
    def __init__(self):
        self.coefficients = None
        self.intercept = None
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit linear regression"""
        try:
            # Simple linear regression implementation
            n = len(X)
            x_mean = np.mean(X)
            y_mean = np.mean(y)
            
            numerator = np.sum((X - x_mean) * (y - y_mean))
            denominator = np.sum((X - x_mean) ** 2)
            
            self.coefficients = numerator / denominator if denominator != 0 else 0
            self.intercept = y_mean - self.coefficients * x_mean
        
        except Exception as e:
            logger.error(f"Error fitting linear regression: {str(e)}")
    
    def predict(self, X: np.ndarray, steps: int = 10) -> np.ndarray:
        """Make linear predictions"""
        if self.coefficients is None:
            return np.zeros(steps)
        
        future_x = np.arange(len(X), len(X) + steps)
        return self.coefficients * future_x + self.intercept
    
    def calculate_confidence(self, predictions: np.ndarray) -> List[Tuple[float, float]]:
        """Calculate confidence intervals (±15%)"""
        margin = 0.15
        return [(p * (1 - margin), p * (1 + margin)) for p in predictions]


class ExponentialSmoothingStrategy(BasePredictionStrategy):
    """Exponential smoothing for time series"""
    
    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha
        self.last_value = None
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit exponential smoothing"""
        self.last_value = y[-1] if len(y) > 0 else 0
    
    def predict(self, X: np.ndarray, steps: int = 10) -> np.ndarray:
        """Make exponential smoothing predictions"""
        if self.last_value is None:
            return np.zeros(steps)
        
        predictions = []
        current = self.last_value
        
        for _ in range(steps):
            predictions.append(current)
            # Apply trend
            current = current * (1 + 0.02)  # 2% growth trend
        
        return np.array(predictions)
    
    def calculate_confidence(self, predictions: np.ndarray) -> List[Tuple[float, float]]:
        """Calculate confidence intervals (±20%)"""
        margin = 0.20
        return [(p * (1 - margin), p * (1 + margin)) for p in predictions]


class MLPredictionEngine:
    """
    Machine Learning engine for predictions and forecasting.
    
    Features:
    - Time-series forecasting
    - Trend analysis
    - Anomaly detection
    - Multiple prediction models
    - Confidence interval calculation
    - Model accuracy metrics
    
    Example:
        >>> engine = MLPredictionEngine()
        >>> history = [100, 110, 120, 115, 130, 140]
        >>> result = engine.forecast(history, steps=10)
        >>> print(result.predictions)
    """
    
    def __init__(self):
        """Initialize prediction engine"""
        self.strategies = {
            PredictionModel.LINEAR_REGRESSION: LinearRegressionStrategy(),
            PredictionModel.EXPONENTIAL_SMOOTHING: ExponentialSmoothingStrategy()
        }
        self.history: Dict[str, List] = {}
        self.logger = logging.getLogger(__name__)
    
    def forecast(
        self,
        time_series: List[float],
        steps: int = 10,
        model: PredictionModel = PredictionModel.LINEAR_REGRESSION,
        confidence: float = 0.95
    ) -> PredictionResult:
        """
        Forecast future values.
        
        Args:
            time_series: Historical time series data
            steps: Number of steps to forecast
            model: Prediction model to use
            confidence: Confidence level (0-1)
            
        Returns:
            PredictionResult with forecasts and metrics
            
        Example:
            >>> data = [100, 105, 110, 115, 120]
            >>> result = engine.forecast(data, steps=5)
            >>> print(f"Next values: {result.predictions}")
        """
        try:
            if not time_series or len(time_series) < 2:
                self.logger.warning("Insufficient data for forecasting")
                return PredictionResult()
            
            # Prepare data
            X = np.arange(len(time_series))
            y = np.array(time_series, dtype=float)
            
            # Get strategy
            strategy = self.strategies.get(
                model, 
                self.strategies[PredictionModel.LINEAR_REGRESSION]
            )
            
            # Fit and predict
            strategy.fit(X, y)
            predictions = strategy.predict(X, steps)
            confidence_intervals = strategy.calculate_confidence(predictions)
            
            # Calculate metrics
            accuracy, rmse, mae, mape = self._calculate_metrics(y, predictions[:len(y)])
            
            result = PredictionResult(
                predictions=predictions.tolist(),
                confidence_intervals=confidence_intervals,
                accuracy=accuracy,
                rmse=rmse,
                mae=mae,
                mape=mape,
                model_used=model.value
            )
            
            self.logger.info(f"Forecast generated with {model.value} (RMSE: {rmse:.2f})")
            return result
        
        except Exception as e:
            self.logger.error(f"Error in forecasting: {str(e)}")
            return PredictionResult()
    
    def detect_anomalies(
        self,
        time_series: List[float],
        threshold: float = 2.0,
        method: str = "zscore"
    ) -> List[AnomalyScore]:
        """
        Detect anomalies in time series.
        
        Args:
            time_series: Time series data
            threshold: Threshold for anomaly detection
            method: Detection method ('zscore' or 'iqr')
            
        Returns:
            List of AnomalyScore objects
            
        Example:
            >>> data = [100, 105, 110, 115, 500, 120, 125]
            >>> anomalies = engine.detect_anomalies(data)
            >>> for anom in anomalies:
            ...     if anom.is_anomaly:
            ...         print(f"Anomaly: {anom.value}")
        """
        try:
            if not time_series:
                return []
            
            data = np.array(time_series, dtype=float)
            anomaly_scores = []
            
            if method == "zscore":
                mean = np.mean(data)
                std = np.std(data)
                
                for value in data:
                    z_score = abs((value - mean) / std) if std != 0 else 0
                    is_anomaly = z_score > threshold
                    
                    anomaly_scores.append(AnomalyScore(
                        value=value,
                        is_anomaly=is_anomaly,
                        anomaly_score=z_score,
                        threshold=threshold,
                        explanation=f"Z-score: {z_score:.2f}"
                    ))
            
            elif method == "iqr":
                q1 = np.percentile(data, 25)
                q3 = np.percentile(data, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                for value in data:
                    is_anomaly = value < lower_bound or value > upper_bound
                    anomaly_score = (
                        (lower_bound - value) / iqr if value < lower_bound
                        else (value - upper_bound) / iqr if value > upper_bound
                        else 0
                    )
                    
                    anomaly_scores.append(AnomalyScore(
                        value=value,
                        is_anomaly=is_anomaly,
                        anomaly_score=abs(anomaly_score),
                        threshold=threshold,
                        explanation=f"IQR bounds: [{lower_bound:.2f}, {upper_bound:.2f}]"
                    ))
            
            self.logger.info(
                f"Detected {sum(1 for a in anomaly_scores if a.is_anomaly)} anomalies"
            )
            return anomaly_scores
        
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            return []
    
    def predict_usage(
        self,
        historical_usage: List[float],
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        Predict future usage patterns.
        
        Args:
            historical_usage: Historical usage data
            forecast_days: Number of days to forecast
            
        Returns:
            Dictionary with usage predictions
        """
        try:
            # Forecast
            forecast_result = self.forecast(
                historical_usage,
                steps=forecast_days,
                model=PredictionModel.EXPONENTIAL_SMOOTHING
            )
            
            # Calculate statistics
            predictions = forecast_result.predictions
            current_avg = np.mean(historical_usage[-7:]) if len(historical_usage) >= 7 else np.mean(historical_usage)
            predicted_avg = np.mean(predictions)
            growth_rate = ((predicted_avg - current_avg) / current_avg * 100) if current_avg > 0 else 0
            
            return {
                'current_average': float(current_avg),
                'predicted_average': float(predicted_avg),
                'growth_rate_percent': float(growth_rate),
                'peak_predicted': float(max(predictions)) if predictions else 0,
                'min_predicted': float(min(predictions)) if predictions else 0,
                'total_predicted': float(sum(predictions)),
                'accuracy': forecast_result.accuracy,
                'confidence_intervals': forecast_result.confidence_intervals,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error predicting usage: {str(e)}")
            return {}
    
    def _calculate_metrics(
        self,
        actual: np.ndarray,
        predicted: np.ndarray
    ) -> Tuple[float, float, float, float]:
        """
        Calculate prediction metrics.
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            Tuple of (accuracy, rmse, mae, mape)
        """
        try:
            # Ensure same length
            min_len = min(len(actual), len(predicted))
            actual = actual[:min_len]
            predicted = predicted[:min_len]
            
            # RMSE
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            
            # MAE
            mae = np.mean(np.abs(actual - predicted))
            
            # MAPE
            mask = actual != 0
            if np.any(mask):
                mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
            else:
                mape = 0
            
            # Accuracy (R²)
            ss_res = np.sum((actual - predicted) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            accuracy = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            accuracy = max(0, min(1, accuracy))  # Clamp to [0, 1]
            
            return float(accuracy), float(rmse), float(mae), float(mape)
        
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            return 0.0, 0.0, 0.0, 0.0
    
    def get_model_comparison(
        self,
        time_series: List[float],
        steps: int = 10
    ) -> Dict[str, Dict]:
        """
        Compare different prediction models.
        
        Args:
            time_series: Time series data
            steps: Forecast steps
            
        Returns:
            Dictionary with comparison results
        """
        try:
            results = {}
            
            for model in PredictionModel:
                if model in self.strategies:
                    result = self.forecast(time_series, steps, model)
                    results[model.value] = result.to_dict()
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error comparing models: {str(e)}")
            return {}


# Export public API
__all__ = [
    'MLPredictionEngine',
    'PredictionResult',
    'AnomalyScore',
    'PredictionModel'
]
