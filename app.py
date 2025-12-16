"""Streamlit application for executing Griptape Nodes workflows via HTTP."""

import streamlit as st
from dotenv import load_dotenv

from pages import characters, location, run_scenario, setting
from utils import get_server_manager

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Griptape Nodes Turn-Based Multi-Character Example",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide the sidebar navigation
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="stSidebar"][aria-expanded="true"] {
            display: none;
        }
        [data-testid="stSidebar"][aria-expanded="false"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def main() -> None:
    """Main Streamlit application."""
    # Load character prefabs at app startup
    if "character_prefabs" not in st.session_state:
        st.session_state.character_prefabs = characters.load_character_prefabs()
    
    # Ensure workflow servers are started
    get_server_manager()

    # App header with title
    st.title("Griptape Nodes Turn-Based Multi-Character Example")
    
    # Check if setting is dirty to show asterisk on Characters tab
    setting_dirty = st.session_state.get("setting_dirty", False)
    characters_label = "Characters*" if setting_dirty else "Characters"
    
    # Check if location is dirty to show asterisk on Run Scenario tab
    location_dirty = st.session_state.get("location_dirty", False)
    run_scenario_label = "Run Scenario*" if location_dirty else "Run Scenario"
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Setting", characters_label, "Location", run_scenario_label])

    with tab1:
        setting.render()

    with tab2:
        characters.render()

    with tab3:
        location.render()

    with tab4:
        run_scenario.render()


if __name__ == "__main__":
    main()
