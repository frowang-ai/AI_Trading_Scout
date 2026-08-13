"""Realtime market-data adapters and alerting utilities."""

from .eastmoney import EastmoneyClient, EastmoneyError

__all__ = ["EastmoneyClient", "EastmoneyError"]
