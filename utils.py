"""Shared utilities for the Streamlit application."""

import httpx
import streamlit as st
from workflow_server_manager import WorkflowServerManager


@st.cache_resource
def get_server_manager() -> WorkflowServerManager:
    """Get or create the workflow server manager."""
    return WorkflowServerManager.get_instance()


async def call_workflow_server(port: int, flow_input: dict) -> dict:
    """Call a workflow server's /run endpoint.

    Args:
        port: The port the workflow server is running on
        flow_input: The complete flow input dict (including "Start Flow" key)

    Returns:
        The workflow output dict from the server response
    """
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"http://localhost:{port}/run",
            json={"flow_input": flow_input},
        )
        response.raise_for_status()
        result = response.json()
        return result.get("output", {})
