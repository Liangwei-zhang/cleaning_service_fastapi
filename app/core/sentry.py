import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import os


def init_sentry():
    """Initialize Sentry for error tracking"""
    dsn = os.getenv("SENTRY_DSN")
    
    if not dsn:
        print("Sentry DSN not configured, skipping...")
        return
    
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring
        traces_sample_rate=0.1,
        # Enable logging
        send_default_pii=True,
        # Environment
        environment=os.getenv("ENVIRONMENT", "development"),
        # Release tracking
        release="smartclean@1.0.0",
    )
    
    print(f"Sentry initialized: {dsn[:20]}...")


def capture_exception(exception, context=None):
    """Capture an exception with optional context"""
    if context:
        sentry_sdk.set_context("custom", context)
    sentry_sdk.capture_exception(exception)


def capture_message(message, level="info"):
    """Capture a message"""
    sentry_sdk.capture_message(message, level=level)
