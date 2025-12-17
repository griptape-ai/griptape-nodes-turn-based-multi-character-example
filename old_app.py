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
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"http://localhost:{port}/run",
            json={"flow_input": flow_input},
        )
        response.raise_for_status()
        result = response.json()
        return result.get("output", {})


async def execute_poem_workflow_async(
    topic: str,
) -> dict:
    """Execute the Griptape Nodes workflow via HTTP.

    Returns:
        dict: Contains workflow output including audio artifacts, text outputs, and retrospective.
    """
    flow_input = {
        "Start Flow": {
            "topic": topic,
        }
    }

    manager = get_server_manager()
    port = manager.get_port("poem_flow")

    if port is None:
        return {
            "was_successful": False,
            "result_details": "Workflow server not configured",
        }

    try:
        output = await call_workflow_server(port, flow_input)

        # Check for error in output
        if "error" in output:
            return {
                "was_successful": False,
                "result_details": f"Workflow error: {output['error']}",
            }

        # Parse the End Flow data from the raw output
        end_flow_data = output.get("End Flow", {})

        return {
            "was_successful": end_flow_data.get("was_successful", False),
            "result_details": end_flow_data.get("result_details", ""),
            "output": end_flow_data.get("output", ""),
        }
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


async def execute_image_workflow_async(
    subject: str,
) -> dict:
    """Execute the Griptape Nodes workflow via HTTP.

    Returns:
        dict: Contains workflow output including audio artifacts, text outputs, and retrospective.
    """
    flow_input = {
        "Start Flow": {
            "subject": subject,
        }
    }

    manager = get_server_manager()
    port = manager.get_port("image_flow")

    if port is None:
        return {
            "was_successful": False,
            "result_details": "Workflow server not configured",
        }

    try:
        output = await call_workflow_server(port, flow_input)

        # Check for error in output
        if "error" in output:
            return {
                "was_successful": False,
                "result_details": f"Workflow error: {output['error']}",
            }

        # Parse the End Flow data from the raw output
        end_flow_data = output.get("End Flow", {})

        return {
            "was_successful": end_flow_data.get("was_successful", False),
            "result_details": end_flow_data.get("result_details", ""),
            "image_url": end_flow_data.get("image_url", {}),
        }
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


def _initialize_poem_flow_state() -> None:
    """Initialize session state variables for the poem workflow."""
    if "topic" not in st.session_state:
        st.session_state.topic = "A serene landscape with mountains and a river"
    if "poem_workflow_running" not in st.session_state:
        st.session_state.poem_workflow_running = False
    if "poem_flow_output" not in st.session_state:
        st.session_state.poem_flow_output = None


def _initialize_image_flow_state() -> None:
    """Initialize session state variables for the image workflow."""
    if "subject" not in st.session_state:
        st.session_state.subject = "A futuristic cityscape at sunset"
    if "image_workflow_running" not in st.session_state:
        st.session_state.image_workflow_running = False
    if "image_flow_output" not in st.session_state:
        st.session_state.image_flow_output = None


def _initialize_session_state() -> None:
    """Initialize all session state variables with default values."""
    _initialize_poem_flow_state()
    _initialize_image_flow_state()


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
    st.markdown("Generate content with AI-powered workflows")

    st.session_state.topic = st.text_area(
        "Define a topic for a poem:",
        value=st.session_state.topic,
        height=400,
        key="topic_input",
    )

    if st.button(
        "Re-run poem workflow",
        type="primary",
        width='stretch',
        disabled=st.session_state.poem_workflow_running,
        key="rerun_poem_button",
    ):
        st.session_state.poem_workflow_running = True
        try:
            with st.spinner("Regenerating poem..."):
                result = asyncio.run(
                    execute_poem_workflow_async(
                        topic=st.session_state.topic or "",
                    )
                )
                st.session_state.poem_flow_output = result
                st.success("✓ Poem regenerated successfully!")
        except Exception as e:
            st.error(f"✗ Poem regeneration failed: {e}")
        finally:
            st.session_state.poem_workflow_running = False
            st.rerun()

    st.session_state.subject = st.text_area(
        "Define a subject for an image:",
        value=st.session_state.subject,
        height=400,
        key="subject_input",
    )

    if st.button(
        "Re-run image workflow",
        type="primary",
        width='stretch',
        disabled=st.session_state.image_workflow_running,
        key="rerun_image_button",
    ):
        st.session_state.image_workflow_running = True
        try:
            with st.spinner("Regenerating image..."):
                result = asyncio.run(
                    execute_image_workflow_async(
                        subject=st.session_state.subject or "",
                    )
                )
                st.session_state.image_flow_output = result
                st.success("✓ Image regenerated successfully!")
        except Exception as e:
            st.error(f"✗ Image regeneration failed: {e}")
        finally:
            st.session_state.image_workflow_running = False
            st.rerun()

    # Display outputs if available
    st.subheader("Poem Output")
    if st.session_state.poem_flow_output is not None:
        poem_result = st.session_state.poem_flow_output
        if poem_result.get("result_details"):
            st.info(poem_result["result_details"])
        poem_output = poem_result.get("output", "")
        if poem_output:
            st.text(poem_output)

    st.subheader("Image Output")
    if st.session_state.image_flow_output is not None:
        image_result = st.session_state.image_flow_output
        if image_result.get("result_details"):
            st.info(image_result["result_details"])
        image_artifact = image_result.get("image_url")
        if image_artifact:
            image_url = get_image_artifact_value(image_artifact)
            if image_url:
                st.image(image_url, caption="Generated Image", width='stretch')
            else:
                st.warning("No image URL found in the workflow output.")


if __name__ == "__main__":
    main()
