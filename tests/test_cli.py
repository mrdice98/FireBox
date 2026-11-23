"""
Tests for FireBox CLI commands and argument routing.
"""

import pytest
from click.testing import CliRunner
from firebox.cli import main
from firebox.version import VERSION


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "FireBox" in result.output
    assert VERSION in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "FireBox — The Next-Generation AI Coding Agent" in result.output
    assert "doctor" in result.output
    assert "providers" in result.output
    assert "models" in result.output


def test_cli_doctor(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["doctor", str(tmp_path)])
    assert result.exit_code == 0
    assert "FIREBOX SYSTEM DOCTOR" in result.output
    assert "Python Version" in result.output


def test_cli_providers():
    runner = CliRunner()
    result = runner.invoke(main, ["providers"])
    assert result.exit_code == 0
    assert "Registered AI Providers" in result.output
    assert "openai" in result.output
    assert "anthropic" in result.output
    assert "gemini" in result.output


def test_cli_models():
    runner = CliRunner()
    result = runner.invoke(main, ["models"])
    assert result.exit_code == 0
    assert "Models for" in result.output


def test_cli_tools():
    runner = CliRunner()
    result = runner.invoke(main, ["tools"])
    assert result.exit_code == 0
    assert "read_file" in result.output
    assert "write_file" in result.output
    assert "shell_exec" in result.output


def test_cli_permissions():
    runner = CliRunner()
    result = runner.invoke(main, ["permissions"])
    assert result.exit_code == 0
    assert "Security & Permission Configuration" in result.output


def test_cli_analyze(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--path", str(tmp_path)])
    assert result.exit_code == 0
    assert "Project Root:" in result.output


def test_cli_init(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, ["init", str(tmp_path)])
    assert result.exit_code == 0
    firebox_md = tmp_path / "FIREBOX.md"
    assert firebox_md.exists()
    assert "FIREBOX PROJECT INSTRUCTIONS" in firebox_md.read_text(encoding="utf-8")


def test_cli_setup_by_number():
    runner = CliRunner()
    # Test passing provider by number 7 (Perplexity) and visible key
    result = runner.invoke(main, ["setup", "-p", "7", "-k", "pplx-test-token-777"])
    assert result.exit_code == 0
    assert "Perplexity AI" in result.output
    assert "pplx-test-token-777" in result.output
    assert "API Credential Registered" in result.output


def test_cli_provider_add_by_number():
    runner = CliRunner()
    # Test adding key using provider number 9 (SambaNova)
    result = runner.invoke(main, ["provider", "add", "9", "samba-key-999"])
    assert result.exit_code == 0
    assert "SambaNova Systems" in result.output
    assert "samba-key-999" in result.output


def test_cli_new_providers_in_catalog():
    runner = CliRunner()
    result = runner.invoke(main, ["providers"])
    assert result.exit_code == 0
    assert "Perplexity" in result.output
    assert "Cohere" in result.output
    assert "SambaNova" in result.output
    assert "Qwen" in result.output
