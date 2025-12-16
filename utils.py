"""Shared utilities for the Streamlit application."""

import asyncio
import logging

import httpx
import streamlit as st
from workflow_server_manager import WorkflowServerManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    logger.info(f"Calling workflow server on port {port}")
    logger.info(f"Flow input: {flow_input}")

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"http://localhost:{port}/run",
            json={"flow_input": flow_input},
        )
        response.raise_for_status()
        result = response.json()
        output = result.get("output", {})

        logger.info(f"Workflow response from port {port}: {output}")
        return output


async def execute_portrait_generation_async(
    context: str,
    tone: str,
    character_name_to_json: dict,
) -> dict:
    """Execute the portrait generation workflow via HTTP.

    Args:
        context: The world context from Setting
        tone: The tone from Setting
        character_name_to_json: Dictionary mapping character names to their JSON data as strings

    Returns:
        dict: Contains workflow output including portrait images
    """
    logger.info("=== PORTRAIT GENERATION WORKFLOW ===")
    logger.info(f"Input - context: {context}")
    logger.info(f"Input - tone: {tone}")
    logger.info(f"Input - character_name_to_json: {character_name_to_json}")

    flow_input = {
        "Start Flow": {
            "context": context,
            "tone": tone,
            "character_name_to_json": character_name_to_json,
        }
    }

    manager = get_server_manager()
    port = manager.get_port("generate_char_portrait")

    if port is None:
        logger.error("Portrait generation workflow server not configured")
        return {
            "was_successful": False,
            "result_details": "Portrait generation workflow server not configured",
        }

    try:
        output = await call_workflow_server(port, flow_input)

        # Check for error in output
        if "error" in output:
            logger.error(f"Workflow returned error: {output['error']}")
            return {
                "was_successful": False,
                "result_details": f"Workflow error: {output['error']}",
            }

        # Parse the End Flow data from the raw output
        end_flow_data = output.get("End Flow", {})
        logger.info(f"End Flow data: {end_flow_data}")

        # The workflow returns portraits as a list of dicts
        # where each dict has the character name as key and image URL as value
        # Example: [{"Brother Aldric": "http://..."}]
        portraits_list = end_flow_data.get("portraits", [])

        # Convert to dict mapping names to portrait URLs
        # The workflow returns portraits as a list of dicts where each dict
        # has the character name as the key and the image URL as the value
        portraits_dict = {}
        for portrait_item in portraits_list:
            if isinstance(portrait_item, dict):
                # Handle format: [{"Brother Aldric": "url"}]
                for name, image in portrait_item.items():
                    if name and image:
                        portraits_dict[name] = image

        logger.info(f"Converted portraits dict: {portraits_dict}")

        result = {
            "was_successful": end_flow_data.get("was_successful", False),
            "result_details": end_flow_data.get("result_details", ""),
            "portraits": portraits_dict,
        }
        logger.info(f"Returning result: {result}")
        return result
    except httpx.RequestError as e:
        logger.exception("Failed to call workflow server")
        return {
            "was_successful": False,
            "result_details": f"Failed to connect to workflow server: {e}",
        }
    except httpx.HTTPStatusError as e:
        logger.exception("Workflow server returned error")
        return {
            "was_successful": False,
            "result_details": f"Workflow server error: {e.response.status_code}",
        }


def execute_portrait_generation(
    context: str,
    tone: str,
    character_name_to_json: dict,
) -> dict:
    """Synchronous wrapper for portrait generation workflow.

    Args:
        context: The world context from Setting
        tone: The tone from Setting
        character_name_to_json: Dictionary mapping character names to their JSON data as strings

    Returns:
        dict: Contains workflow output including portrait images
    """
    return asyncio.run(
        execute_portrait_generation_async(
            context=context,
            tone=tone,
            character_name_to_json=character_name_to_json,
        )
    )
