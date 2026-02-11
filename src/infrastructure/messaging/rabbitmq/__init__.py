# PATH: src/infrastructure/messaging/rabbitmq/__init__.py
# DESC: RabbitMQ messaging package.
"""RabbitMQ messaging adapters."""

from src.infrastructure.messaging.rabbitmq.ai_feedback_publisher import (
    AIFeedbackPublisher,
)

__all__: list[str] = [
    "AIFeedbackPublisher",
]
