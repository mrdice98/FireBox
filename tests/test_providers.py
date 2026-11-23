"""
Tests for AI Providers, Registry, and Mock Simulation.
"""

import pytest
from firebox.providers.base import ChatMessage, ChatResponse, ToolCall
from firebox.providers.mock_provider import MockProvider
from firebox.providers.registry import get_provider_registry


def test_mock_provider_basic():
    provider = MockProvider()
    assert provider.test_connection() is True
    assert "firebox-sim-1.0" in provider.list_models()

    resp = provider.chat_complete([
        ChatMessage(role="user", content="Hello FireBox!")
    ])
    assert isinstance(resp, ChatResponse)
    assert "operational" in resp.content.lower()


def test_mock_provider_tool_generation():
    provider = MockProvider()
    resp = provider.chat_complete(
        messages=[ChatMessage(role="user", content="Please read file config.py")],
        tools=[{"type": "function", "function": {"name": "read_file"}}]
    )
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "read_file"
    assert resp.tool_calls[0].arguments["path"] == "config.py"


def test_mock_provider_streaming():
    provider = MockProvider()
    chunks = list(provider.stream_chat([ChatMessage(role="user", content="Ping")]))
    assert len(chunks) > 0
    assert any("token" in c for c in chunks)


def test_provider_registry():
    reg = get_provider_registry()
    providers = reg.list_all_providers()
    assert len(providers) >= 10
    
    # Check default active
    active_prov = reg.get_provider()
    assert active_prov is not None

    # Switch active provider
    reg.set_active_provider("mock", model="firebox-sim-1.0")
    assert reg.get_provider("mock").name == "Mock/Offline"
