"""Streamlit application for executing Griptape Nodes workflows via HTTP."""

import asyncio
import logging
from typing import Any

import httpx
import streamlit as st
from dotenv import load_dotenv
from griptape.artifacts.image_url_artifact import ImageUrlArtifact

from workflow_server_manager import WorkflowServerManager

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Griptape Nodes Turn-Based Multi-Character Example",
    page_icon="🎵",
    layout="wide",
)


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
    
async def execute_character_generation_async(
    character: str,
    description: str,
    society: str,
) -> dict:
    """Execute the character generation workflow via HTTP.

    Returns:
        dict: Contains workflow output including character data.
    """
    logger.info("=== CHARACTER GENERATION WORKFLOW ===")
    logger.info(f"Input - character: {character}")
    logger.info(f"Input - description: {description}")
    logger.info(f"Input - society: {society}")

    flow_input = {
        "Start Flow": {
            "character": character,
            "description": description,
            "society": society,
        }
    }

    manager = get_server_manager()
    port = manager.get_port("character_generation_flow")

    if port is None:
        return {
            "was_successful": False,
            "result_details": "Character generation workflow server not configured",
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

        # Try different possible keys for character data
        character_data = end_flow_data.get("character") or end_flow_data.get("description") or {}
        logger.info(f"Extracted character_data: {character_data}")

        result = {
            "was_successful": end_flow_data.get("was_successful", False),
            "result_details": end_flow_data.get("result_details", ""),
            "character_data": character_data,
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


async def execute_image_and_story_async(
    character_data: dict,
    scenario: str,
) -> dict:
    """Execute image generation and story generation workflows concurrently.

    Returns:
        dict: Contains both image and story outputs.
    """
    logger.info("=== IMAGE AND STORY WORKFLOW ===")
    logger.info(f"Input - character_data: {character_data}")
    logger.info(f"Input - scenario: {scenario}")

    # Run both workflows in parallel using asyncio.gather
    image_task = asyncio.create_task(
        execute_character_image_async(character_data)
    )
    story_task = asyncio.create_task(
        execute_story_generation_async(character_data, scenario)
    )

    image_result, story_result = await asyncio.gather(image_task, story_task)

    logger.info(f"Image result: {image_result}")
    logger.info(f"Story result: {story_result}")

    return {
        "image": image_result,
        "story": story_result,
    }


async def execute_character_image_async(character_data: dict) -> dict:
    """Execute the character image generation workflow via HTTP.

    Returns:
        dict: Contains workflow output including image artifact.
    """
    logger.info("--- Character Image Workflow ---")
    logger.info(f"Input character_data: {character_data}")

    flow_input = {
        "Start Flow": {
            "character_dictionary": character_data,
        }
    }

    manager = get_server_manager()
    port = manager.get_port("character_image_flow")

    if port is None:
        return {
            "was_successful": False,
            "result_details": "Character image workflow server not configured",
        }

    try:
        output = await call_workflow_server(port, flow_input)

        # Check for error in output
        if "error" in output:
            logger.error(f"Image workflow error: {output['error']}")
            return {
                "was_successful": False,
                "result_details": f"Workflow error: {output['error']}",
            }

        # Parse the End Flow data from the raw output
        end_flow_data = output.get("End Flow", {})
        logger.info(f"Image workflow End Flow data: {end_flow_data}")

        result = {
            "was_successful": end_flow_data.get("was_successful", False),
            "result_details": end_flow_data.get("result_details", ""),
            "image": end_flow_data.get("image", {}),
        }
        logger.info(f"Image workflow returning: {result}")
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


async def execute_story_generation_async(
    character_data: dict,
    scenario: str,
) -> dict:
    """Execute the story generation workflow via HTTP.

    Returns:
        dict: Contains workflow output including story text.
    """
    logger.info("--- Story Generation Workflow ---")
    logger.info(f"Input character_data: {character_data}")
    logger.info(f"Input scenario: {scenario}")

    flow_input = {
        "Start Flow": {
            "character": character_data,
            "situation": scenario,
        }
    }

    manager = get_server_manager()
    port = manager.get_port("story_from_character")

    if port is None:
        return {
            "was_successful": False,
            "result_details": "Story generation workflow server not configured",
        }

    try:
        output = await call_workflow_server(port, flow_input)

        # Check for error in output
        if "error" in output:
            logger.error(f"Story workflow error: {output['error']}")
            return {
                "was_successful": False,
                "result_details": f"Workflow error: {output['error']}",
            }

        # Parse the End Flow data from the raw output
        end_flow_data = output.get("End Flow", {})
        logger.info(f"Story workflow End Flow data: {end_flow_data}")

        result = {
            "was_successful": end_flow_data.get("was_successful", False),
            "result_details": end_flow_data.get("result_details", ""),
            "story": end_flow_data.get("story", ""),
        }
        logger.info(f"Story workflow returning: {result}")
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



def _initialize_session_state() -> None:
    """Initialize all session state variables with default values."""
    # Character generation inputs
    if "character_name" not in st.session_state:
        st.session_state.character_name = "Elena"
    if "character_description" not in st.session_state:
        st.session_state.character_description = "A brave warrior with a mysterious past"
    if "society" not in st.session_state:
        st.session_state.society = "A medieval kingdom filled with magic and dragons"

    # Story generation input
    if "scenario" not in st.session_state:
        st.session_state.scenario = "The character discovers an ancient artifact"

    # Workflow running states
    if "character_workflow_running" not in st.session_state:
        st.session_state.character_workflow_running = False
    if "story_workflow_running" not in st.session_state:
        st.session_state.story_workflow_running = False

    # Output storage
    if "character_output" not in st.session_state:
        st.session_state.character_output = None
    if "story_and_image_output" not in st.session_state:
        st.session_state.story_and_image_output = None


def get_image_artifact_value(artifact: Any) -> str | None:
    """Extract the URL/path from an ImageUrlArtifact or dict artifact."""
    if artifact is None:
        return None
    if isinstance(artifact, ImageUrlArtifact) and hasattr(artifact, "value"):
        return artifact.value
    if isinstance(artifact, dict) and "value" in artifact:
        return artifact["value"]
    return None


def main() -> None:  # noqa: C901, PLR0912, PLR0915
    """Main Streamlit application."""
    _initialize_session_state()

    # Ensure workflow servers are started
    get_server_manager()

    st.title("Griptape Nodes Turn-Based Multi-Character Example")
    st.markdown("Generate characters and stories with AI-powered workflows")

    # Create two columns for the two workflows
    col1, col2 = st.columns(2)

    with col1:
        st.header("1. Generate Character")
        st.session_state.character_name = st.text_input(
            "Character Name:",
            value=st.session_state.character_name,
            key="character_name_input",
        )
        st.session_state.character_description = st.text_area(
            "Character Description:",
            value=st.session_state.character_description,
            height=150,
            key="character_description_input",
        )
        st.session_state.society = st.text_area(
            "Society:",
            value=st.session_state.society,
            height=150,
            key="society_input",
        )

        if st.button(
            "Generate Character",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.character_workflow_running,
            key="generate_character_button",
        ):
            st.session_state.character_workflow_running = True
            try:
                with st.spinner("Generating character..."):
                    result = asyncio.run(
                        execute_character_generation_async(
                            character=st.session_state.character_name or "",
                            description=st.session_state.character_description or "",
                            society=st.session_state.society or "",
                        )
                    )
                    st.session_state.character_output = result
                    if result.get("was_successful"):
                        st.success("✓ Character generated successfully!")
                    else:
                        st.error(f"✗ Character generation failed: {result.get('result_details')}")
            except Exception as e:
                st.error(f"✗ Character generation failed: {e}")
            finally:
                st.session_state.character_workflow_running = False
                st.rerun()

    with col2:
        st.header("2. Generate Image & Story")
        st.session_state.scenario = st.text_area(
            "Scenario:",
            value=st.session_state.scenario,
            height=150,
            key="scenario_input",
        )

        # Check if character has been generated
        character_available = (
            st.session_state.character_output is not None
            and st.session_state.character_output.get("was_successful")
        )

        if not character_available:
            st.warning("⚠️ Please generate a character first before running this workflow.")

        if st.button(
            "Generate Image & Story",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.story_workflow_running or not character_available,
            key="generate_story_button",
        ):
            st.session_state.story_workflow_running = True
            try:
                with st.spinner("Generating image and story..."):
                    character_data = st.session_state.character_output.get("character_data", {})
                    result = asyncio.run(
                        execute_image_and_story_async(
                            character_data=character_data,
                            scenario=st.session_state.scenario or "",
                        )
                    )
                    st.session_state.story_and_image_output = result
                    st.success("✓ Image and story generated successfully!")
            except Exception as e:
                st.error(f"✗ Image and story generation failed: {e}")
            finally:
                st.session_state.story_workflow_running = False
                st.rerun()

    # Display outputs
    st.divider()

    # Character Output
    st.subheader("Character Output")
    if st.session_state.character_output is not None:
        character_result = st.session_state.character_output
        if character_result.get("result_details"):
            st.info(character_result["result_details"])
        character_data = character_result.get("character_data")
        if character_data:
            st.json(character_data)
        elif not character_result.get("was_successful"):
            st.warning("No character data available.")

    # Story and Image Output
    st.subheader("Story Output")
    if st.session_state.story_and_image_output is not None:
        story_result = st.session_state.story_and_image_output.get("story", {})
        if story_result.get("result_details"):
            st.info(story_result["result_details"])
        story_text = story_result.get("story", "")
        if story_text:
            st.text(story_text)
        elif not story_result.get("was_successful"):
            st.warning("No story available.")

    st.subheader("Character Image")
    if st.session_state.story_and_image_output is not None:
        image_result = st.session_state.story_and_image_output.get("image", {})
        if image_result.get("result_details"):
            st.info(image_result["result_details"])
        image_artifact = image_result.get("image")
        if image_artifact:
            image_url = get_image_artifact_value(image_artifact)
            if image_url:
                st.image(image_url, caption="Generated Character Image", use_container_width=True)
            else:
                st.warning("No image URL found in the workflow output.")
        elif not image_result.get("was_successful"):
            st.warning("No image available.")


if __name__ == "__main__":
    main()
