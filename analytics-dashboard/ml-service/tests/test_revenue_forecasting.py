"""
Tests for Revenue Forecasting Model
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from models.revenue_forecasting import RevenueForecastModel
from services.feature_store import FeatureStoreService
from core.config import get_settings


class TestRevenueForecastModel:
    """Test suite for Revenue Forecasting Model"""

    @pytest.fixture
    def mock_feature_store(self):
        """Create a mock feature store service"""
        feature_store = Mock(spec=FeatureStoreService)
        
        # Mock historical data
        historical_data = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'),
            'revenue': np.random.uniform(50, 500, 365),
        })
        
        feature_store.get_user_revenue_history = AsyncMock(return_value=historical_data)
        feature_store.get_user_features = AsyncMock(return_value={
            'user_tenure_days': 365,
            'avg_product_price': 75.50,
            'total_products': 150,
            'category_performance': 0.8,
        })
        
        return feature_store

    @pytest.fixture
    def model(self, mock_feature_store):
        """Create a revenue forecast model instance"""
        return RevenueForecastModel(
            model_path='/tmp/test_model',
            feature_store=mock_feature_store,
            model_version='1.0.0'
        )

    @pytest.fixture
    def sample_historical_data(self):
        """Generate sample historical data for testing"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        # Create realistic revenue data with trend and seasonality
        trend = np.linspace(100, 200, len(dates))
        seasonal = 50 * np.sin(2 * np.pi * np.arange(len(dates)) / 365.25)
        noise = np.random.normal(0, 20, len(dates))
        revenue = trend + seasonal + noise
        revenue = np.maximum(revenue, 0)  # Ensure non-negative
        
        return pd.DataFrame({
            'date': dates,
            'revenue': revenue,
        })

    class TestInitialization:
        """Test model initialization"""

        def test_model_initialization(self, model, mock_feature_store):
            """Test that model initializes correctly"""
            assert model.feature_store == mock_feature_store
            assert model.model_version == '1.0.0'
            assert model.is_trained is False
            assert model.prophet_model is None
            assert model.gb_model is None
            assert model.scaler is None

        def test_model_hyperparameters(self, model):
            """Test that hyperparameters are set correctly"""
            assert model.prophet_params['yearly_seasonality'] is True
            assert model.prophet_params['weekly_seasonality'] is True
            assert model.prophet_params['seasonality_mode'] == 'multiplicative'
            
            assert model.gb_params['n_estimators'] == 200
            assert model.gb_params['max_depth'] == 6
            assert model.gb_params['learning_rate'] == 0.1

    class TestPrediction:
        """Test prediction functionality"""

        @pytest.mark.asyncio
        async def test_predict_with_valid_data(self, model, sample_historical_data):
            """Test prediction with valid historical data"""
            # Mock the trained state and methods
            model.is_trained = True
            model.prophet_model = Mock()
            model.gb_model = Mock()
            model.scaler = Mock()
            
            # Mock the internal prediction methods
            with patch.object(model, '_get_historical_data', return_value=sample_historical_data), \
                 patch.object(model, '_prophet_predict', return_value={
                     'daily': [
                         {'date': '2024-01-01', 'revenue': 150.0, 'trend': 140.0, 'seasonal': 10.0},
                         {'date': '2024-01-02', 'revenue': 155.0, 'trend': 145.0, 'seasonal': 10.0},
                     ],
                     'total': 305.0,
                     'method': 'Prophet'
                 }), \
                 patch.object(model, '_gradient_boosting_predict', return_value={
                     'daily': [
                         {'date': '2024-01-01', 'revenue': 148.0, 'method': 'GradientBoosting'},
                         {'date': '2024-01-02', 'revenue': 152.0, 'method': 'GradientBoosting'},
                     ],
                     'total': 300.0,
                     'method': 'Gradient Boosting'
                 }), \
                 patch.object(model, '_calculate_accuracy_metrics', return_value={
                     'mape': 8.5,
                     'mae': 12.3,
                     'r2_score': 0.85
                 }):

                prediction_data = {
                    'user_id': 'test-user-123',
                    'forecast_days': 2,
                    'include_confidence': True
                }

                result = await model.predict(prediction_data)

                # Verify response structure
                assert 'user_id' in result
                assert 'forecast_days' in result
                assert 'forecasts' in result
                assert 'accuracy' in result
                assert 'methodology' in result
                assert 'recommendations' in result

                # Verify forecast data
                assert len(result['forecasts']['daily']) == 2
                assert result['forecasts']['total'] > 0
                assert result['accuracy']['mape'] == 8.5

        @pytest.mark.asyncio
        async def test_predict_insufficient_data(self, model):
            """Test prediction with insufficient historical data"""
            # Mock insufficient data
            insufficient_data = pd.DataFrame({
                'date': pd.date_range(start='2023-12-01', end='2023-12-15', freq='D'),
                'revenue': np.random.uniform(50, 100, 15),
            })

            model.is_trained = True
            
            with patch.object(model, '_get_historical_data', return_value=insufficient_data):
                prediction_data = {
                    'user_id': 'test-user-123',
                    'forecast_days': 30
                }

                with pytest.raises(ValueError, match="Insufficient historical data"):
                    await model.predict(prediction_data)

        @pytest.mark.asyncio
        async def test_predict_untrained_model(self, model):
            """Test prediction with untrained model"""
            prediction_data = {
                'user_id': 'test-user-123',
                'forecast_days': 30
            }

            # Mock load method to return False (model not found)
            with patch.object(model, 'load', return_value=False):
                with pytest.raises(ValueError, match="Model is not trained"):
                    await model.predict(prediction_data)

        @pytest.mark.asyncio
        async def test_predict_missing_user_id(self, model):
            """Test prediction without user_id"""
            model.is_trained = True
            
            prediction_data = {
                'forecast_days': 30
            }

            with pytest.raises(ValueError, match="user_id is required"):
                await model.predict(prediction_data)

    class TestTraining:
        """Test training functionality"""

        @pytest.mark.asyncio
        async def test_train_with_sufficient_data(self, model, sample_historical_data):
            """Test training with sufficient data"""
            with patch.object(model, '_prepare_training_data', return_value=sample_historical_data), \
                 patch.object(model, '_train_prophet', return_value={'mae': 15.0, 'mape': 10.0}), \
                 patch.object(model, '_train_gradient_boosting', return_value={'mae': 12.0, 'mape': 8.0}), \
                 patch.object(model, 'save', return_value=True):

                result = await model.train()

                assert result['training_completed'] is True
                assert 'training_date' in result
                assert result['training_samples'] > 0
                assert result['validation_samples'] > 0
                assert 'prophet_metrics' in result
                assert 'gb_metrics' in result

                # Verify model state
                assert model.is_trained is True
                assert model.last_training_date is not None

        @pytest.mark.asyncio
        async def test_train_insufficient_data(self, model):
            """Test training with insufficient data"""
            insufficient_data = pd.DataFrame({
                'date': pd.date_range(start='2023-12-01', end='2023-12-31', freq='D'),
                'revenue': np.random.uniform(50, 100, 31),
            })

            with patch.object(model, '_prepare_training_data', return_value=insufficient_data):
                with pytest.raises(ValueError, match="Insufficient training data"):
                    await model.train()

        @pytest.mark.asyncio
        async def test_retrain(self, model, sample_historical_data):
            """Test model retraining"""
            with patch.object(model, 'train', return_value={'retrain': 'success'}) as mock_train:
                result = await model.retrain()
                
                mock_train.assert_called_once()
                assert result == {'retrain': 'success'}

    class TestValidation:
        """Test model validation"""

        @pytest.mark.asyncio
        async def test_validate_with_data(self, model, sample_historical_data):
            """Test model validation with validation data"""
            model.is_trained = True
            
            with patch.object(model, 'predict', side_effect=[
                {'forecasts': {'daily': [{'revenue': 150.0}]}},
                {'forecasts': {'daily': [{'revenue': 148.0}]}},
                {'forecasts': {'daily': [{'revenue': 152.0}]}},
            ]):
                validation_data = pd.DataFrame({
                    'user_id': ['user1', 'user1', 'user1'],
                    'revenue': [145.0, 150.0, 155.0],
                })

                result = await model.validate(validation_data)

                assert 'validation_date' in result
                assert 'samples_validated' in result
                assert 'metrics' in result
                assert 'performance_status' in result

                metrics = result['metrics']
                assert 'mae' in metrics
                assert 'mse' in metrics
                assert 'rmse' in metrics
                assert 'r2_score' in metrics
                assert 'mape' in metrics

        @pytest.mark.asyncio
        async def test_validate_without_data(self, model):
            """Test validation without providing validation data"""
            with patch.object(model.feature_store, 'get_time_series_data', return_value=pd.DataFrame({
                'user_id': ['user1'] * 10,
                'revenue': np.random.uniform(100, 200, 10),
            })), \
            patch.object(model, 'predict', return_value={
                'forecasts': {'daily': [{'revenue': 150.0}]}
            }):
                result = await model.validate()
                
                assert 'validation_date' in result
                assert 'samples_validated' in result

    class TestUtilityMethods:
        """Test utility methods"""

        @pytest.mark.asyncio
        async def test_get_historical_data_with_override(self, model):
            """Test getting historical data with override"""
            override_data = {
                'date': ['2023-01-01', '2023-01-02'],
                'revenue': [100.0, 110.0]
            }

            result = await model._get_historical_data('user123', override_data)
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert 'date' in result.columns
            assert 'revenue' in result.columns

        def test_calculate_trend(self, model):
            """Test trend calculation"""
            # Upward trend
            upward_series = pd.Series([10, 20, 30, 40, 50])
            trend = model._calculate_trend(upward_series)
            assert trend > 0

            # Downward trend
            downward_series = pd.Series([50, 40, 30, 20, 10])
            trend = model._calculate_trend(downward_series)
            assert trend < 0

            # Flat trend
            flat_series = pd.Series([30, 30, 30, 30, 30])
            trend = model._calculate_trend(flat_series)
            assert abs(trend) < 0.1

        def test_get_seasonal_factor(self, model, sample_historical_data):
            """Test seasonal factor calculation"""
            test_date = datetime(2023, 6, 15)  # Mid-year
            factor = model._get_seasonal_factor(test_date, sample_historical_data)
            
            assert isinstance(factor, float)
            assert factor > 0  # Should be positive

        def test_ensemble_predictions(self, model):
            """Test ensemble prediction combination"""
            prophet_forecast = {
                'daily': [
                    {'date': '2024-01-01', 'revenue': 150.0},
                    {'date': '2024-01-02', 'revenue': 160.0},
                ],
                'total': 310.0,
                'method': 'Prophet'
            }

            gb_forecast = {
                'daily': [
                    {'date': '2024-01-01', 'revenue': 140.0},
                    {'date': '2024-01-02', 'revenue': 150.0},
                ],
                'total': 290.0,
                'method': 'Gradient Boosting'
            }

            ensemble = model._ensemble_predictions(prophet_forecast, gb_forecast, [0.6, 0.4])

            assert len(ensemble['daily']) == 2
            assert ensemble['method'] == 'Ensemble'
            
            # Check weighted average calculation
            expected_day1 = 0.6 * 150.0 + 0.4 * 140.0  # 146.0
            assert abs(ensemble['daily'][0]['revenue'] - expected_day1) < 0.1

        def test_generate_recommendations(self, model):
            """Test business recommendation generation"""
            # Upward trending forecast
            upward_forecast = {
                'daily': [
                    {'date': '2024-01-01', 'revenue': 100.0},
                    {'date': '2024-01-02', 'revenue': 110.0},
                    {'date': '2024-01-03', 'revenue': 120.0},
                    {'date': '2024-01-04', 'revenue': 130.0},
                    {'date': '2024-01-05', 'revenue': 140.0},
                    {'date': '2024-01-06', 'revenue': 150.0},  # Weekend
                    {'date': '2024-01-07', 'revenue': 160.0},  # Weekend
                ],
                'total': 910.0
            }

            recommendations = model._generate_recommendations(upward_forecast)

            assert isinstance(recommendations, list)
            assert len(recommendations) > 0
            
            # Should detect upward trend
            assert any('trending upward' in rec.lower() for rec in recommendations)

        def test_calculate_accuracy_metrics_fallback(self, model, sample_historical_data):
            """Test accuracy metrics calculation with fallback"""
            # Test with insufficient data
            small_data = sample_historical_data.head(5)
            
            result = asyncio.run(model._calculate_accuracy_metrics(small_data, 'test-user'))
            
            # Should return default values
            assert 'mape' in result
            assert 'mae' in result
            assert 'r2_score' in result
            assert result['mape'] > 0

    class TestErrorHandling:
        """Test error handling scenarios"""

        @pytest.mark.asyncio
        async def test_predict_feature_store_error(self, model):
            """Test prediction when feature store fails"""
            model.is_trained = True
            
            # Mock feature store to raise exception
            model.feature_store.get_user_revenue_history.side_effect = Exception("Database error")

            prediction_data = {
                'user_id': 'test-user-123',
                'forecast_days': 30
            }

            with pytest.raises(Exception):
                await model.predict(prediction_data)

        @pytest.mark.asyncio
        async def test_train_save_failure(self, model, sample_historical_data):
            """Test training when model save fails"""
            with patch.object(model, '_prepare_training_data', return_value=sample_historical_data), \
                 patch.object(model, '_train_prophet', return_value={'mae': 15.0, 'mape': 10.0}), \
                 patch.object(model, '_train_gradient_boosting', return_value={'mae': 12.0, 'mape': 8.0}), \
                 patch.object(model, 'save', side_effect=Exception("Save failed")):

                with pytest.raises(Exception):
                    await model.train()

    class TestModelPersistence:
        """Test model save/load functionality"""

        @pytest.mark.asyncio
        async def test_save_model(self, model):
            """Test model saving"""
            with patch('os.makedirs'), \
                 patch('builtins.open'), \
                 patch('pickle.dump'), \
                 patch('joblib.dump'):
                
                model.is_trained = True
                model.last_training_date = datetime.now()
                model.feature_columns = ['feature1', 'feature2']

                result = await model.save()
                assert result is True

        @pytest.mark.asyncio
        async def test_load_model(self, model):
            """Test model loading"""
            with patch('os.path.exists', return_value=True), \
                 patch('builtins.open'), \
                 patch('pickle.load'), \
                 patch('joblib.load'):
                
                result = await model.load()
                assert result is True

        @pytest.mark.asyncio
        async def test_load_nonexistent_model(self, model):
            """Test loading non-existent model"""
            with patch('os.path.exists', return_value=False):
                result = await model.load()
                assert result is False


@pytest.fixture
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Integration tests
class TestRevenueForecastModelIntegration:
    """Integration tests for the revenue forecast model"""

    @pytest.mark.asyncio
    async def test_full_prediction_workflow(self):
        """Test the complete prediction workflow"""
        # This would test with actual data and services
        # For now, we'll mock the dependencies
        
        feature_store = Mock(spec=FeatureStoreService)
        feature_store.get_user_revenue_history = AsyncMock(return_value=pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=365),
            'revenue': np.random.uniform(100, 300, 365)
        }))
        feature_store.get_user_features = AsyncMock(return_value={
            'user_tenure_days': 365,
            'avg_product_price': 75.50,
        })

        model = RevenueForecastModel(
            model_path='/tmp/test_model',
            feature_store=feature_store
        )

        # Train the model (mocked)
        with patch.object(model, '_train_prophet', return_value={'mae': 15.0, 'mape': 10.0}), \
             patch.object(model, '_train_gradient_boosting', return_value={'mae': 12.0, 'mape': 8.0}), \
             patch.object(model, 'save', return_value=True):
            
            training_result = await model.train()
            assert training_result['training_completed'] is True

        # Make predictions
        with patch.object(model, '_prophet_predict', return_value={
                'daily': [{'date': '2024-01-01', 'revenue': 150.0}],
                'total': 150.0
            }), \
             patch.object(model, '_gradient_boosting_predict', return_value={
                'daily': [{'date': '2024-01-01', 'revenue': 148.0}],
                'total': 148.0
            }):
            
            prediction_result = await model.predict({
                'user_id': 'test-user',
                'forecast_days': 1
            })

            assert 'forecasts' in prediction_result
            assert len(prediction_result['forecasts']['daily']) == 1


if __name__ == '__main__':
    pytest.main(['-v', __file__])