#!/usr/bin/env python3
"""
MCPA2A - Multi-Agent Communication Platform
Main entry point for running agents and CLI client.
"""

import asyncio
import sys
import click


@click.group()
def cli():
    """MCPA2A - Multi-Agent Communication Platform"""
    pass


@cli.command()
@click.option('--host', default='localhost', help='Host for the agent server')
@click.option('--port', default=10001, help='Port for the agent server')
def host_agent(host: str, port: int):
    """Start the Host Agent (Orchestrator)"""
    from agents.host_agent.__main__ import main
    asyncio.run(main.main([f'--host={host}', f'--port={port}'], standalone_mode=False))


@cli.command()
@click.option('--host', default='localhost', help='Host for the agent server')
@click.option('--port', default=10000, help='Port for the agent server')
def website_builder(host: str, port: int):
    """Start the Website Builder Agent"""
    from agents.website_builder.__main__ import main
    main([f'--host={host}', f'--port={port}'], standalone_mode=False)


@cli.command()
@click.option('--agent', default='http://127.0.0.1:10001', help='Base URL of the A2A agent server')
@click.option('--session', default='0', help='Session ID (use 0 to generate a new one)')
def client(agent: str, session: str):
    """Start the CLI client to interact with agents"""
    from app.cli.client import cli as client_cli
    asyncio.run(client_cli.main([f'--agent={agent}', f'--session={session}'], standalone_mode=False))


if __name__ == '__main__':
    cli()
