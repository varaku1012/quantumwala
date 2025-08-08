"""
ML Service Main Application
FastAPI application for machine learning model inference and predictions.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis
import structlog

# Local imports
from api.routes import predictions, models, features, health
from core.config import get_settings
from core.logging import setup_logging
from core.database import get_database
from core.cache import get_redis_client
from services.model_manager import ModelManager
from services.feature_store import FeatureStoreService
from models.revenue_forecasting import RevenueForecastModel
from models.demand_prediction import DemandPredictionModel
from models.price_optimization import PriceOptimizationModel

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('ml_service_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('ml_service_request_duration_seconds', 'Request latency')
ACTIVE_MODELS = Gauge('ml_service_active_models', 'Number of active models')
PREDICTION_COUNT = Counter('ml_service_predictions_total', 'Total predictions', ['model_type'])

settings = get_settings()

# Global services
model_manager: ModelManager = None
feature_store: FeatureStoreService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup and shutdown."""
    logger.info("Starting ML Service...")
    
    global model_manager, feature_store
    
    try:
        # Initialize database
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Initialize Redis
        redis_client = redis.Redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        logger.info("Redis connection established")
        
        # Initialize Feature Store
        feature_store = FeatureStoreService(
            database_url=settings.FEATURE_STORE_URL,
            redis_client=redis_client
        )
        await feature_store.initialize()
        logger.info("Feature Store initialized")
        
        # Initialize Model Manager
        model_manager = ModelManager(
            model_storage_path=settings.MODEL_STORAGE_PATH,
            redis_client=redis_client,
            feature_store=feature_store
        )
        
        # Load ML models
        await load_models()
        
        logger.info("ML Service started successfully")
        
        yield  # Application runs here
        
    except Exception as e:
        logger.error(f"Failed to start ML Service: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down ML Service...")
        if model_manager:
            await model_manager.cleanup()
        if feature_store:
            await feature_store.cleanup()
        logger.info("ML Service shutdown complete")


async def load_models():
    """Load and initialize ML models."""
    try:
        # Revenue Forecasting Model
        revenue_model = RevenueForecastModel(
            model_path=os.path.join(settings.MODEL_STORAGE_PATH, 'revenue_forecast'),
            feature_store=feature_store
        )
        await model_manager.register_model('revenue_forecast', revenue_model)
        logger.info("Revenue forecasting model loaded")
        
        # Demand Prediction Model
        demand_model = DemandPredictionModel(
            model_path=os.path.join(settings.MODEL_STORAGE_PATH, 'demand_prediction'),
            feature_store=feature_store
        )
        await model_manager.register_model('demand_prediction', demand_model)
        logger.info("Demand prediction model loaded")
        
        # Price Optimization Model
        price_model = PriceOptimizationModel(
            model_path=os.path.join(settings.MODEL_STORAGE_PATH, 'price_optimization'),
            feature_store=feature_store
        )
        await model_manager.register_model('price_optimization', price_model)
        logger.info("Price optimization model loaded")
        
        ACTIVE_MODELS.set(model_manager.get_model_count())
        
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise


# Create FastAPI app
app = FastAPI(
    title="EtsyPro AI ML Service",
    description="Machine Learning inference service for predictive analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Backend
        "http://localhost:3001",  # Frontend
        settings.BACKEND_URL,
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add request processing time and metrics."""
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Update Prometheus metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.observe(process_time)
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.warning(
        "HTTP exception occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "type": "http_error"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception occurred",
        exception=str(exc),
        path=request.url.path,
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )


# Dependency providers
async def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    if model_manager is None:
        raise HTTPException(status_code=503, detail="Model manager not initialized")
    return model_manager


async def get_feature_store_service() -> FeatureStoreService:
    """Get the global feature store service instance."""
    if feature_store is None:
        raise HTTPException(status_code=503, detail="Feature store not initialized")
    return feature_store


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "EtsyPro AI ML Service",
        "version": "1.0.0",
        "status": "healthy",
        "models_loaded": model_manager.get_model_count() if model_manager else 0,
        "docs": "/docs",
        "metrics": "/metrics",
        "health": "/health"
    }


# Include API routes
app.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

app.include_router(
    predictions.router,
    prefix="/api/v1/ml/predict",
    tags=["Predictions"],
    dependencies=[Depends(get_model_manager)]
)

app.include_router(
    models.router,
    prefix="/api/v1/ml/models",
    tags=["Model Management"],
    dependencies=[Depends(get_model_manager)]
)

app.include_router(
    features.router,
    prefix="/api/v1/ml/features",
    tags=["Feature Engineering"],
    dependencies=[Depends(get_feature_store_service)]
)


# Batch processing endpoints
@app.post("/api/v1/ml/batch/predict")
async def batch_predict(
    requests: list[Dict[str, Any]],
    background_tasks: BackgroundTasks,
    model_mgr: ModelManager = Depends(get_model_manager)
):
    """Process batch predictions asynchronously."""
    batch_id = f"batch_{int(time.time())}"
    
    background_tasks.add_task(
        process_batch_predictions,
        batch_id,
        requests,
        model_mgr
    )
    
    return {
        "batch_id": batch_id,
        "status": "processing",
        "total_requests": len(requests),
        "message": "Batch processing started"
    }


async def process_batch_predictions(
    batch_id: str,
    requests: list[Dict[str, Any]],
    model_manager: ModelManager
):
    """Process batch predictions in the background."""
    logger.info(f"Processing batch {batch_id} with {len(requests)} requests")
    
    results = []
    for i, request in enumerate(requests):
        try:
            # Process individual prediction
            model_type = request.get('model_type')
            model = await model_manager.get_model(model_type)
            
            prediction = await model.predict(request.get('data', {}))
            results.append({
                "request_id": request.get('id', i),
                "prediction": prediction,
                "status": "success"
            })
            
        except Exception as e:
            logger.error(f"Error processing request {i} in batch {batch_id}: {e}")
            results.append({
                "request_id": request.get('id', i),
                "error": str(e),
                "status": "error"
            })
    
    # Store results (in production, this would go to a database or cache)
    logger.info(f"Batch {batch_id} processing complete: {len(results)} results")


# Model retraining endpoint
@app.post("/api/v1/ml/retrain/{model_type}")
async def retrain_model(
    model_type: str,
    background_tasks: BackgroundTasks,
    model_mgr: ModelManager = Depends(get_model_manager)
):
    """Retrain a specific model with latest data."""
    if not await model_mgr.model_exists(model_type):
        raise HTTPException(status_code=404, detail=f"Model {model_type} not found")
    
    job_id = f"retrain_{model_type}_{int(time.time())}"
    
    background_tasks.add_task(
        retrain_model_background,
        job_id,
        model_type,
        model_mgr
    )
    
    return {
        "job_id": job_id,
        "model_type": model_type,
        "status": "started",
        "message": "Model retraining started"
    }


async def retrain_model_background(
    job_id: str,
    model_type: str,
    model_manager: ModelManager
):
    """Retrain model in the background."""
    logger.info(f"Starting model retraining job {job_id} for {model_type}")
    
    try:
        model = await model_manager.get_model(model_type)
        await model.retrain()
        logger.info(f"Model retraining job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Model retraining job {job_id} failed: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True,
        loop="asyncio"
    )