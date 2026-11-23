"""
FireBox Main CLI Interface.
Command dispatcher, interactive TUI REPL, and task runner.
"""

import sys
import os
import json
import click
from pathlib import Path
from typing import Optional

from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED

from firebox.version import VERSION, CODENAME
from firebox import __tagline__
from firebox.ui.theme import (
    get_console,
    COLOR_ORANGE,
    COLOR_BLUE,
    COLOR_BORDER,
    COLOR_GRAY,
    COLOR_GRAY_LIGHT,
    COLOR_FIRE_FLAME,
    COLOR_FIRE_GOLD,
    COLOR_FIRE_YELLOW,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WARNING,
    COLOR_INFO,
    COLOR_WHITE,
    COLOR_ASH,
)
from firebox.ui.animations import render_logo, display_startup_card
from firebox.ui.tui import FireBoxTUI, SLASH_COMMANDS
from firebox.ui.formatters import render_markdown, render_plan
from firebox.ui.diff_viewer import render_diff
from firebox.config.manager import get_config
from firebox.config.schemas import SafetyLevel, AnimationMode
from firebox.providers.registry import get_provider_registry
from firebox.tools.registry import get_tool_registry
from firebox.safety.permissions import PermissionManager
from firebox.safety.rollback import get_rollback_manager
from firebox.agent.modes import AgentMode, MODE_DESCRIPTIONS
from firebox.agent.engine import AgentEngine
from firebox.agent.session import get_session_manager
from firebox.extensions.plugins import get_plugin_manager
from firebox.installer.doctor import run_diagnostics


def run_interactive_repl(workspace_root: Path, session_id: Optional[str] = None):
    """Launch the cinematic interactive FireBox TUI REPL."""
    console = get_console()
    config_mgr = get_config()
    provider_reg = get_provider_registry()
    tool_reg = get_tool_registry(workspace_root)
    session_mgr = get_session_manager()

    # Startup sequence
    anim_mode = config_mgr.app_config.animation_mode.value
    provider = provider_reg.get_provider()
    model_name = config_mgr.app_config.active_model
    tools = tool_reg.list_tools()

    active_session_id = session_id or f"firebox_{os.getpid()}"
    engine = AgentEngine(
        workspace_root=workspace_root,
        session_id=active_session_id,
        mode=AgentMode.AUTONOMOUS,
    )

    display_startup_card(
        provider_name=provider.name,
        model_name=model_name,
        cwd=str(workspace_root),
        session_id=active_session_id,
        tools_count=len(tools),
        mode=anim_mode,
        safety_level=config_mgr.permissions.safety_level.value,
        console=console,
    )

    tui = FireBoxTUI()

    while True:
        try:
            user_input = tui.prompt(mode=engine.mode.value, model_name=config_mgr.app_config.active_model)
            if not user_input:
                continue

            # Handle slash commands
            if user_input.startswith("/"):
                cmd_parts = user_input.split()
                cmd = cmd_parts[0].lower()
                arg = " ".join(cmd_parts[1:]) if len(cmd_parts) > 1 else ""

                if cmd in ("/exit", "/quit"):
                    console.print(f"[bold {COLOR_FIRE_GOLD}]Extinguishing FireBox. Keep coding! 🔥[/]")
                    break

                elif cmd in ("/help", "/?"):
                    _show_help_table(console)

                elif cmd == "/clear":
                    console.clear()
                    display_startup_card(
                        provider_name=provider.name,
                        model_name=model_name,
                        cwd=str(workspace_root),
                        session_id=active_session_id,
                        tools_count=len(tools),
                        mode="minimal",
                        safety_level=config_mgr.permissions.safety_level.value,
                        console=console,
                    )

                elif cmd == "/status":
                    _show_status(console, engine, config_mgr)

                elif cmd == "/doctor":
                    run_diagnostics(workspace_root, console=console)

                elif cmd == "/new":
                    import uuid
                    active_session_id = f"firebox_{uuid.uuid4().hex[:8]}"
                    engine = AgentEngine(workspace_root=workspace_root, session_id=active_session_id)
                    console.print(f"[bold {COLOR_SUCCESS}]✔ Started fresh session: {active_session_id}[/]")

                elif cmd == "/sessions":
                    _list_sessions(console, session_mgr)

                elif cmd == "/resume":
                    if arg:
                        engine = AgentEngine(workspace_root=workspace_root, session_id=arg)
                        active_session_id = arg
                        console.print(f"[bold {COLOR_SUCCESS}]✔ Resumed session: {arg}[/]")
                    else:
                        console.print("[yellow]Usage: /resume <session_id>[/]")

                elif cmd == "/compact":
                    engine.messages = engine.context_mgr.compact_context(engine.messages)
                    console.print(f"[bold {COLOR_SUCCESS}]✔ Context compacted successfully.[/]")

                elif cmd == "/context":
                    tokens = engine.context_mgr.count_conversation_tokens(engine.messages)
                    limit = engine.context_mgr.max_token_limit
                    console.print(f"[bold {COLOR_FIRE_GOLD}]Context usage:[/] {tokens:,} / {limit:,} tokens estimated")

                elif cmd == "/models":
                    _list_models(console, provider_reg)

                elif cmd == "/model":
                    if arg:
                        provider_reg.set_active_model(arg)
                        console.print(f"[bold {COLOR_SUCCESS}]✔ Active model set to:[/] [bold cyan]{arg}[/]")
                    else:
                        console.print("[yellow]Usage: /model <model_name> (e.g. /model gpt-4o, /model claude-3-7-sonnet)[/]")

                elif cmd == "/providers":
                    _list_providers(console, provider_reg)

                elif cmd == "/provider":
                    if arg:
                        resolved = provider_reg.resolve_provider_choice(arg)
                        if resolved:
                            try:
                                provider_reg.set_active_provider(resolved)
                                prov = provider_reg.get_provider(resolved)
                                catalog = provider_reg.get_catalog()
                                meta = next((c for c in catalog if c["id"] == resolved), None)
                                idx_str = f"#{meta['index']} · " if meta else ""
                                console.print(f"[bold {COLOR_SUCCESS}]✔ Active provider set to:[/] [bold white]{prov.name}[/] [dim]({idx_str}{resolved})[/] [bold {COLOR_FIRE_GOLD}](Model: {prov.default_model})[/]")
                            except Exception as e:
                                console.print(f"[bold {COLOR_ERROR}]✖ {e}[/]")
                        else:
                            console.print(f"[bold {COLOR_ERROR}]✖ Unknown provider '{arg}'. Type [bold cyan]/providers[/] to view the numbered catalog (1-{len(provider_reg.get_catalog())}).[/]")
                    else:
                        _list_providers(console, provider_reg)
                        console.print(f"[dim]Tip: Switch instantly with [bold cyan]/provider <number>[/] (e.g. [bold]/provider 1[/] for OpenAI, [bold]/provider 2[/] for Anthropic, [bold]/provider 7[/] for Perplexity)[/]")

                elif cmd in ("/setup", "/key"):
                    _list_providers(console, provider_reg)
                    catalog = provider_reg.get_catalog()
                    choice = click.prompt(
                        f"Select AI Provider by Number (1-{len(catalog)}) or name",
                        default="1",
                    )
                    resolved = provider_reg.resolve_provider_choice(choice)
                    if resolved:
                        meta = next((c for c in catalog if c["id"] == resolved), None)
                        p_name = meta["name"] if meta else resolved.capitalize()
                        p_idx = meta["index"] if meta else None
                        d_model = meta.get("default_model", "default") if meta else "default"
                        req_key = meta.get("requires_key", True) if meta else True

                        if req_key:
                            console.print(f"[dim {COLOR_GRAY_LIGHT}]Paste or enter your API key below. It will visibly show on screen where you enter it.[/]")
                            in_key = click.prompt(f"Enter API Key for {p_name}", default="", hide_input=False)
                            if in_key:
                                config_mgr.credentials.set_key(resolved, in_key)
                                _display_key_confirmation_card(console, p_name, resolved, p_idx, in_key, d_model)
                            else:
                                console.print("[yellow]No key entered.[/]")
                        else:
                            console.print(f"[bold {COLOR_SUCCESS}]✔ {p_name} is ready (offline/local, no API key required).[/]")

                        provider_reg.set_active_provider(resolved)
                        console.print(f"[bold {COLOR_SUCCESS}]✔ Switched active provider to:[/] [bold white]{p_name}[/] [dim]({resolved})[/]")
                    else:
                        console.print(f"[bold {COLOR_ERROR}]✖ Unknown provider selection: {choice}[/]")

                elif cmd == "/tools":
                    _list_tools(console, tool_reg)

                elif cmd == "/plugins":
                    _list_plugins(console)

                elif cmd == "/permissions":
                    _show_permissions(console, config_mgr)

                elif cmd == "/diff":
                    res = tool_reg.execute_tool("git_diff", {})
                    console.print(res.output)

                elif cmd == "/files":
                    res = tool_reg.execute_tool("list_dir", {"path": "."})
                    console.print(res.output)

                elif cmd == "/undo":
                    rb = get_rollback_manager()
                    restored = rb.undo_last()
                    if restored:
                        console.print(f"[bold {COLOR_SUCCESS}]✔ Successfully rolled back:[/] {restored}")
                    else:
                        console.print("[yellow]No recent file backup found to undo.[/]")

                elif cmd == "/plan":
                    if arg:
                        engine.set_mode(AgentMode.PLAN)
                        engine.run_turn(f"Create a comprehensive step-by-step plan for: {arg}")
                    else:
                        console.print("[yellow]Usage: /plan <goal or feature description>[/]")

                elif cmd == "/review":
                    engine.set_mode(AgentMode.REVIEW)
                    engine.run_turn(arg or "Perform a deep code review of the modified code and current workspace files.")

                elif cmd == "/test":
                    res = tool_reg.execute_tool("run_tests", {})
                    console.print(res.output)

                elif cmd == "/fix":
                    engine.set_mode(AgentMode.AUTONOMOUS)
                    engine.run_turn(f"Diagnose and fix the following issue: {arg or 'Check recent test failures and fix them'}")

                elif cmd == "/terminal":
                    if arg:
                        res = tool_reg.execute_tool("shell_exec", {"command": arg})
                        console.print(res.output)
                    else:
                        console.print("[yellow]Usage: /terminal <shell command>[/]")

                else:
                    console.print(f"[yellow]Unknown command '{cmd}'. Type [bold cyan]/help[/] for list of commands.[/]")
                continue

            # Normal prompt to agent engine
            engine.run_turn(user_input)

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Operation cancelled by user (Ctrl+C).[/]")
        except EOFError:
            break


def _show_help_table(console):
    table = Table(box=ROUNDED, border_style=COLOR_FIRE_FLAME, expand=True)
    table.add_column("Command", style=f"bold {COLOR_FIRE_GOLD}", width=16)
    table.add_column("Category", style="cyan", width=12)
    table.add_column("Description", style=COLOR_WHITE)

    for cmd, (cat, desc) in sorted(SLASH_COMMANDS.items(), key=lambda x: (x[1][0], x[0])):
        table.add_row(cmd, cat, desc)

    console.print(Panel(table, title=f"[bold {COLOR_FIRE_GOLD}]🔥 FIREBOX COMMAND REFERENCE 🔥[/]", border_style=COLOR_FIRE_FLAME))


def _show_status(console, engine, config_mgr):
    table = Table(box=ROUNDED, border_style=COLOR_FIRE_FLAME)
    table.add_column("Property", style=f"bold {COLOR_FIRE_GOLD}")
    table.add_column("Value", style=COLOR_WHITE)
    table.add_row("Active Mode", f"[bold cyan]{engine.mode.value.upper()}[/]")
    table.add_row("Session ID", engine.session_id)
    table.add_row("Active Provider", config_mgr.app_config.active_provider)
    table.add_row("Active Model", config_mgr.app_config.active_model)
    table.add_row("Safety Level", config_mgr.permissions.safety_level.value)
    table.add_row("Workspace", str(engine.workspace_root))
    console.print(Panel(table, title="System Status", border_style=COLOR_FIRE_FLAME))


def _list_sessions(console, session_mgr):
    sessions = session_mgr.list_sessions()
    table = Table(box=ROUNDED, border_style=COLOR_FIRE_FLAME, expand=True)
    table.add_column("Session ID", style=f"bold {COLOR_FIRE_GOLD}")
    table.add_column("Model", style="cyan")
    table.add_column("Mode", style="white")
    table.add_column("Messages", justify="right")
    table.add_column("Workspace", style="dim")

    for s in sessions:
        table.add_row(s["session_id"], s["model"], s["mode"], str(s["message_count"]), s["workspace"])
    console.print(Panel(table, title="Saved Sessions", border_style=COLOR_FIRE_FLAME))


def _list_models(console, provider_reg):
    prov = provider_reg.get_provider()
    models = prov.list_models()
    table = Table(box=ROUNDED, border_style=COLOR_FIRE_FLAME)
    table.add_column("Available Models", style=f"bold {COLOR_FIRE_GOLD}")
    for m in models:
        table.add_row(m)
    console.print(Panel(table, title=f"Models for {prov.name}", border_style=COLOR_FIRE_FLAME))


def _display_key_confirmation_card(
    console,
    provider_name: str,
    provider_id: str,
    index_num: Optional[int],
    key: str,
    default_model: str,
):
    """Render a dedicated, visible API key confirmation card confirming key was added."""
    idx_str = f"#{index_num} · " if index_num else ""
    table = Table.grid(padding=(0, 2))
    table.add_column("Property", style=f"bold {COLOR_GRAY_LIGHT}", width=16)
    table.add_column("Value", style="bold white")
    table.add_row("Provider:", f"[bold {COLOR_ORANGE}]{provider_name}[/] [dim]({idx_str}{provider_id})[/]")
    table.add_row("Entered API Key:", f"[bold {COLOR_BLUE}]{key}[/]")
    table.add_row("Default Model:", f"[cyan]{default_model}[/]")
    table.add_row("Storage Target:", f"[dim]Secure Storage (~/.firebox/credentials.dat)[/]")
    table.add_row("Status:", f"[bold {COLOR_SUCCESS}]✔ REGISTERED & ACTIVE[/]")

    console.print(Panel(
        table,
        title=f"[bold {COLOR_BLUE}]🔑 API Credential Registered[/]",
        subtitle=f"[dim]Input verified & saved securely[/]",
        border_style=COLOR_BLUE,
        expand=False,
    ))


def _list_providers(console, provider_reg):
    catalog = provider_reg.get_catalog()
    all_provs = {p["id"]: p for p in provider_reg.list_all_providers()}

    table = Table(box=ROUNDED, border_style=COLOR_BORDER)
    table.add_column("#", style=f"bold {COLOR_ORANGE}", justify="center", width=5)
    table.add_column("Provider Name", style="bold white", width=18)
    table.add_column("ID", style=f"dim {COLOR_GRAY_LIGHT}", width=11)
    table.add_column("Default Model", style="cyan", width=22)
    table.add_column("Status", justify="center", width=11)

    for cat in catalog:
        idx = cat["index"]
        p_id = cat["id"]
        p_info = all_provs.get(p_id, {})
        is_configured = p_info.get("configured", False)
        is_active = p_info.get("is_active", False)

        if not cat.get("requires_key", True):
            key_status = f"[dim]OFFLINE[/]"
        elif is_configured:
            key_status = f"[bold {COLOR_SUCCESS}]CONFIGURED[/]"
        else:
            key_status = f"[dim {COLOR_ASH}]NOT SET[/]"

        num_str = f"★{idx:02d}" if is_active else f"[{idx:02d}]"
        table.add_row(num_str, cat["name"], p_id, cat["default_model"][:22], key_status)

    console.print(Panel(
        table,
        title=f"[bold {COLOR_ORANGE}]🔥 Registered AI Providers (1-{len(catalog)})[/]",
        subtitle=f"[dim]Choose by number: firebox setup, firebox provider add <#>, or /provider <#>[/]",
        border_style=COLOR_BORDER,
    ))


def _list_tools(console, tool_reg):
    tools = tool_reg.list_tools()
    table = Table(box=ROUNDED, border_style=COLOR_FIRE_FLAME, expand=True)
    table.add_column("Tool Name", style=f"bold {COLOR_FIRE_GOLD}", width=22)
    table.add_column("Category", style="cyan", width=12)
    table.add_column("Status", width=10, justify="center")
    table.add_column("Description", style=COLOR_WHITE)

    for t in tools:
        st = f"[bold {COLOR_SUCCESS}]ENABLED[/]" if t["enabled"] else f"[dim]DISABLED[/]"
        table.add_row(t["name"], t["category"], st, t["description"])
    console.print(Panel(table, title="FireBox Tool Registry", border_style=COLOR_FIRE_FLAME))


def _list_plugins(console):
    pm = get_plugin_manager()
    plugins = pm.list_plugins()
    table = Table(box=ROUNDED, border_style=COLOR_FIRE_FLAME, expand=True)
    table.add_column("Plugin ID", style=f"bold {COLOR_FIRE_GOLD}")
    table.add_column("Version", style="cyan")
    table.add_column("Tools", style="white")

    for p in plugins:
        tools_str = ", ".join(p.get("tools", [])) or "(none)"
        table.add_row(p["id"], p.get("version", "1.0.0"), tools_str)
    console.print(Panel(table, title="Installed Plugins", border_style=COLOR_FIRE_FLAME))


def _show_permissions(console, config_mgr):
    p = config_mgr.permissions
    table = Table(box=ROUNDED, border_style=COLOR_FIRE_FLAME)
    table.add_column("Permission Setting", style=f"bold {COLOR_FIRE_GOLD}")
    table.add_column("Value", style=COLOR_WHITE)
    table.add_row("Safety Level", p.safety_level.value)
    table.add_row("Workspace Isolation", str(p.workspace_only))
    table.add_row("Allow Shell Exec", str(p.allow_shell_commands))
    table.add_row("Allow Deletions", str(p.allow_file_deletions))
    console.print(Panel(table, title="Security & Permission Configuration", border_style=COLOR_FIRE_FLAME))


# ==========================================
# Click CLI Command Tree
# ==========================================

class FireBoxGroup(click.Group):
    """Custom Click Group that transparently maps positional workspace directories."""

    def parse_args(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            candidate = Path(args[0])
            if candidate.exists() and candidate.is_dir():
                args = ["--dir", args[0]] + args[1:]
        return super().parse_args(ctx, args)


@click.group(cls=FireBoxGroup, invoke_without_command=True)
@click.option("--dir", "-d", "workspace_dir", default=".", help="Workspace directory (defaults to current working directory).")
@click.option("--prompt", "-p", help="One-off prompt to run autonomously without entering interactive REPL.")
@click.option("--mode", "-m", type=click.Choice(["ask", "plan", "build", "autonomous", "review"]), default=None)
@click.option("--session", "-s", help="Session ID to create or resume.")
@click.option("--version", "-v", is_flag=True, help="Show FireBox version.")
@click.pass_context
def main(ctx, workspace_dir, prompt, mode, session, version):
    """FireBox — The Next-Generation AI Coding Agent.
    Ignite Your Code. Burn Through Tasks.
    """
    console = get_console()

    if version:
        console.print(f"[bold {COLOR_FIRE_FLAME}]FireBox[/] [bold {COLOR_FIRE_GOLD}]v{VERSION}[/] ({CODENAME})")
        console.print(f"[dim]{__tagline__}[/]")
        return

    # If a subcommand was already resolved by Click
    if ctx.invoked_subcommand is not None:
        return

    # Determine workspace directory
    ws_path = Path(workspace_dir).resolve()
    if not ws_path.exists() or not ws_path.is_dir():
        console.print(f"[bold {COLOR_ERROR}]Error: Workspace directory does not exist: {workspace_dir}[/]")
        sys.exit(1)

    agent_mode = AgentMode(mode) if mode else AgentMode.AUTONOMOUS

    # One-off prompt execution
    if prompt:
        engine = AgentEngine(workspace_root=ws_path, session_id=session, mode=agent_mode)
        engine.run_turn(prompt)
        return

    # Interactive TUI mode
    run_interactive_repl(workspace_root=ws_path, session_id=session)


@main.command("init")
@click.argument("path", default=".")
def cmd_init(path):
    """Initialize FIREBOX.md project instruction file and workspace settings."""
    console = get_console()
    ws = Path(path).resolve()
    firebox_md = ws / "FIREBOX.md"

    if firebox_md.exists():
        console.print(f"[yellow]FIREBOX.md already exists at {firebox_md}[/]")
        return

    template = (
        "# FIREBOX PROJECT INSTRUCTIONS\n\n"
        "Welcome to FireBox! This file instructs the FireBox AI agent on the guidelines,\n"
        "coding standards, and commands specific to this repository.\n\n"
        "## Build & Test Commands\n"
        "- Test: `python -m pytest` or `npm test`\n"
        "- Build: `npm run build` or `cargo build`\n\n"
        "## Architecture & Conventions\n"
        "- Clean code with typed annotations.\n"
        "- Verify changes with automated tests before committing.\n"
    )
    firebox_md.write_text(template, encoding="utf-8")
    console.print(f"[bold {COLOR_SUCCESS}]✔ Created FIREBOX.md at {firebox_md}[/]")


@main.command("doctor")
@click.argument("path", default=".")
def cmd_doctor(path):
    """Run diagnostics on environment, providers, runtimes, and permissions."""
    ws = Path(path).resolve()
    run_diagnostics(ws)


@main.command("version")
def cmd_version():
    """Display FireBox version and brand information."""
    console = get_console()
    render_logo(console, mode="minimal")
    console.print(f"[bold {COLOR_FIRE_FLAME}]FireBox AI Engine[/] [bold {COLOR_FIRE_GOLD}]v{VERSION}[/] ({CODENAME})")
    console.print(f"[dim]{__tagline__}[/]")


@main.command("setup")
@click.option("--provider", "-p", "provider_arg", default=None, help="AI provider number (1-19) or name.")
@click.option("--key", "-k", "key_arg", default=None, help="API key for the selected provider.")
def cmd_setup(provider_arg, key_arg):
    """Interactive wizard to configure AI providers by number and plug in API keys."""
    console = get_console()
    config_mgr = get_config()
    reg = get_provider_registry()
    catalog = reg.get_catalog()

    console.print(Panel(
        f"[bold {COLOR_ORANGE}]🔥 FireBox AI Provider & API Key Setup Wizard 🔥[/]\n"
        f"[dim {COLOR_GRAY_LIGHT}]Select your preferred provider by Number (1-{len(catalog)}) and plug in your API key with visible confirmation.[/]",
        border_style=COLOR_BORDER,
    ))

    # Display numbered table if user didn't pass provider argument
    if not provider_arg:
        _list_providers(console, reg)
        choice = click.prompt(
            f"Select AI Provider by Number (1-{len(catalog)}) or name",
            default="1",
        )
    else:
        choice = provider_arg

    # Resolve selection by number or name
    resolved_id = reg.resolve_provider_choice(str(choice))
    if not resolved_id:
        console.print(f"[bold {COLOR_ERROR}]✖ Unknown provider selection '{choice}'. Defaulting to OpenAI (#1).[/]")
        resolved_id = "openai"

    prov_meta = next((c for c in catalog if c["id"] == resolved_id), None)
    prov_name = prov_meta["name"] if prov_meta else resolved_id.capitalize()
    prov_index = prov_meta["index"] if prov_meta else None
    requires_key = prov_meta.get("requires_key", True) if prov_meta else True
    default_model = prov_meta.get("default_model", "default") if prov_meta else "default"

    console.print(f"\n[bold {COLOR_SUCCESS}]✔ Selected Provider:[/] [bold white]{prov_name}[/] [dim]({resolved_id})[/] — Provider #{prov_index}\n")

    # API Key handling with visible entry (hide_input=False)
    key = key_arg
    if key is None and requires_key:
        console.print(f"[dim {COLOR_GRAY_LIGHT}]Paste or enter your API key below. The key will be visibly shown where you enter it:[/]")
        key = click.prompt(
            f"Enter API Key for {prov_name} (press Enter to skip)",
            default="",
            hide_input=False,
        )

    if key:
        config_mgr.credentials.set_key(resolved_id, key)
        _display_key_confirmation_card(
            console=console,
            provider_name=prov_name,
            provider_id=resolved_id,
            index_num=prov_index,
            key=key,
            default_model=default_model,
        )
    elif not requires_key:
        console.print(f"[bold {COLOR_SUCCESS}]✔ Provider {prov_name} is ready (offline/local, no API key required).[/]")
    else:
        console.print(f"[yellow]No API key entered. You can add one anytime with: [bold cyan]firebox provider add {prov_index}[/][/]")

    # Update active configuration
    config_mgr.app_config.active_provider = resolved_id
    try:
        prov = reg.get_provider(resolved_id)
        config_mgr.app_config.active_model = prov.default_model
    except Exception:
        config_mgr.app_config.active_model = default_model

    config_mgr.save_app_config()
    console.print(f"[bold {COLOR_SUCCESS}]✔ FireBox configured with [bold white]{prov_name}[/] [dim](Model: {config_mgr.app_config.active_model})[/]![/]\n")


# ==========================================
# Project Subcommands (plan, build, fix, test, review, refactor, analyze)
# ==========================================

@main.command("plan")
@click.argument("goal")
@click.option("--path", "-d", default=".")
def cmd_plan(goal, path):
    """Analyze the project and output a step-by-step milestone plan."""
    engine = AgentEngine(workspace_root=Path(path).resolve(), mode=AgentMode.PLAN)
    engine.run_turn(f"Create a comprehensive step-by-step milestone plan to achieve: {goal}")


@main.command("build")
@click.argument("task")
@click.option("--path", "-d", default=".")
def cmd_build(task, path):
    """Implement a feature or code task directly with validation."""
    engine = AgentEngine(workspace_root=Path(path).resolve(), mode=AgentMode.BUILD)
    engine.run_turn(f"Implement and verify: {task}")


@main.command("fix")
@click.argument("issue", default="Diagnose and fix all failing tests or syntax errors.")
@click.option("--path", "-d", default=".")
def cmd_fix(issue, path):
    """Diagnose errors and automatically implement fixes."""
    engine = AgentEngine(workspace_root=Path(path).resolve(), mode=AgentMode.AUTONOMOUS)
    engine.run_turn(f"Diagnose and fix the following issue: {issue}")


@main.command("test")
@click.option("--path", "-d", default=".")
def cmd_test(path):
    """Detect and execute project test suites."""
    tool_reg = get_tool_registry(Path(path).resolve())
    res = tool_reg.execute_tool("run_tests", {})
    get_console().print(res.output)


@main.command("review")
@click.option("--path", "-d", default=".")
def cmd_review(path):
    """Perform a deep code review on the project workspace."""
    engine = AgentEngine(workspace_root=Path(path).resolve(), mode=AgentMode.REVIEW)
    engine.run_turn("Review current project files and git diff for bugs, security vulnerabilities, and code quality.")


@main.command("analyze")
@click.option("--path", "-d", default=".")
def cmd_analyze(path):
    """Scan and summarize languages, frameworks, and architecture of the workspace."""
    tool_reg = get_tool_registry(Path(path).resolve())
    res = tool_reg.execute_tool("detect_project", {})
    get_console().print(res.output)


@main.command("refactor")
@click.argument("target")
@click.option("--path", "-d", default=".")
def cmd_refactor(target, path):
    """Refactor targeted code for better modularity and performance."""
    engine = AgentEngine(workspace_root=Path(path).resolve(), mode=AgentMode.AUTONOMOUS)
    engine.run_turn(f"Refactor the following target for clarity, performance, and maintainability: {target}")


# ==========================================
# Providers & Models Command Groups
# ==========================================

@main.group("providers")
def grp_providers():
    """List and manage AI providers."""
    pass

@grp_providers.command("list")
def cmd_providers_list():
    """List all supported and configured AI providers."""
    _list_providers(get_console(), get_provider_registry())

# Alias `firebox providers` directly
@main.command("providers")
def cmd_providers_shortcut():
    """List all AI providers."""
    _list_providers(get_console(), get_provider_registry())


@main.group("provider")
def grp_provider():
    """Add, remove, or test AI providers."""
    pass

@grp_provider.command("add")
@click.argument("name", required=False)
@click.argument("key", required=False)
def cmd_provider_add(name, key):
    """Configure API key for an AI provider by Number (1-19) or name."""
    console = get_console()
    config_mgr = get_config()
    reg = get_provider_registry()
    catalog = reg.get_catalog()

    if not name:
        _list_providers(console, reg)
        name = click.prompt(
            f"Select Provider by Number (1-{len(catalog)}) or name",
            default="1",
        )

    resolved_id = reg.resolve_provider_choice(str(name))
    if not resolved_id:
        console.print(f"[bold {COLOR_ERROR}]✖ Unknown provider '{name}'.[/]")
        return

    prov_meta = next((c for c in catalog if c["id"] == resolved_id), None)
    prov_name = prov_meta["name"] if prov_meta else resolved_id.capitalize()
    prov_index = prov_meta["index"] if prov_meta else None
    default_model = prov_meta.get("default_model", "default") if prov_meta else "default"

    if not key:
        console.print(f"[dim {COLOR_GRAY_LIGHT}]Paste or enter your API key below. The key will be visibly shown where you enter it:[/]")
        key = click.prompt(f"Enter API Key for {prov_name}", hide_input=False)

    if key:
        config_mgr.credentials.set_key(resolved_id, key)
        _display_key_confirmation_card(
            console=console,
            provider_name=prov_name,
            provider_id=resolved_id,
            index_num=prov_index,
            key=key,
            default_model=default_model,
        )
        console.print(f"[bold {COLOR_SUCCESS}]✔ Successfully saved API credentials for {prov_name} (#{prov_index})![/]")

@grp_provider.command("test")
@click.argument("name")
def cmd_provider_test(name):
    """Test connectivity and credentials for a provider."""
    console = get_console()
    reg = get_provider_registry()
    prov = reg.get_provider(name)
    ok = prov.test_connection()
    if ok:
        console.print(f"[bold {COLOR_SUCCESS}]✔ Connectivity test for {prov.name} PASSED[/]")
    else:
        console.print(f"[bold {COLOR_ERROR}]✖ Connectivity test for {prov.name} FAILED[/]")


@main.group("models")
def grp_models():
    """List, search, and set models."""
    pass

@grp_models.command("list")
def cmd_models_list():
    """List models for active provider."""
    _list_models(get_console(), get_provider_registry())

@grp_models.command("set")
@click.argument("model_name")
def cmd_models_set(model_name):
    """Set the active model."""
    console = get_console()
    reg = get_provider_registry()
    reg.set_active_model(model_name)
    console.print(f"[bold {COLOR_SUCCESS}]✔ Active model set to {model_name}[/]")

# Alias `firebox models` directly
@main.command("models")
def cmd_models_shortcut():
    """List models for active provider."""
    _list_models(get_console(), get_provider_registry())


# ==========================================
# Config, Sessions, Tools, Plugins, Reset
# ==========================================

@main.group("config")
def grp_config():
    """Manage FireBox configuration."""
    pass

@grp_config.command("show")
def cmd_config_show():
    """Display current configuration."""
    console = get_console()
    cfg = get_config()
    console.print_json(json.dumps(cfg.app_config.model_dump()))

@grp_config.command("reset")
def cmd_config_reset():
    """Reset configuration to initial defaults."""
    cfg = get_config()
    cfg.reset_to_defaults()
    get_console().print(f"[bold {COLOR_SUCCESS}]✔ Configuration reset to defaults.[/]")


@main.command("sessions")
def cmd_sessions():
    """List all saved agent sessions."""
    _list_sessions(get_console(), get_session_manager())


@main.command("tools")
def cmd_tools():
    """List all registered tools."""
    _list_tools(get_console(), get_tool_registry())


@main.command("plugins")
def cmd_plugins():
    """List installed plugins."""
    _list_plugins(get_console())


@main.command("permissions")
def cmd_permissions():
    """Display security and permissions configuration."""
    _show_permissions(get_console(), get_config())


@main.command("reset")
def cmd_reset():
    """Reset FireBox configuration and cache."""
    cfg = get_config()
    cfg.reset_to_defaults()
    get_console().print(f"[bold {COLOR_SUCCESS}]✔ FireBox has been reset to fresh defaults.[/]")


@main.command("update")
def cmd_update():
    """Check for FireBox updates."""
    get_console().print(f"[bold {COLOR_SUCCESS}]FireBox v{VERSION} is the latest Prometheus Ember release.[/]")


if __name__ == "__main__":
    main()
