"""Run Scenario page for executing turn-based multi-character role-playing scenarios."""

import asyncio
import json
import logging
from typing import Any

import streamlit as st
from griptape.artifacts.image_url_artifact import ImageUrlArtifact

from utils import call_workflow_server, get_server_manager

logger = logging.getLogger(__name__)

# Silhouette placeholder (same as characters.py)
SILHOUETTE_PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect width='100' height='100' fill='%23ddd'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='%23999'%3E?%3C/text%3E%3C/svg%3E"

# Pre-fab options for Scenario
SCENARIO_PREFABS = {
    "Retrieve the Orb of Wonder": "Your mission: Retrieve the Orb of Wonder before the Witch King can use it to complete his dark ritual. Time is of the essence—you estimate you have mere minutes before the ritual reaches completion. If he succeeds, the entire kingdom will fall under his shadow curse. You tracked him here after weeks of pursuit across the wilderness, and this is your only chance to stop him. The Orb is said to corrupt those who touch it, but you have no choice—it must be taken from his grasp.",
    "Defend the Village": "A band of marauders approaches the peaceful village. You must rally the villagers and defend against the attack. The stakes are high—failure means the village will be razed and its people enslaved.",
    "Escape the Dungeon": "You've been captured and thrown into a dark dungeon. Your goal is to escape before your captors return to execute you. Time is critical, and you must work with your fellow prisoners to break free.",
    "Create My Own": "",
}

# Pre-fab options for Scene
SCENE_PREFABS = {
    "Throne Room Confrontation": "The protagonists stand at the main entrance of the throne room, weapons drawn. At the far end of the hall, the Witch King sits upon his obsidian throne, the glowing Orb of Wonder clutched in his skeletal hand. Guards flank the throne, ready to defend their lord. The adventurers have come to retrieve the Orb before the Witch King can complete his dark ritual.",
    "Village Gate": "You stand at the village gate as dust clouds signal the approaching marauders. Villagers huddle behind you, their faces filled with fear. The gate is sturdy but won't hold forever.",
    "Dungeon Cell": "You wake in a cold, damp cell. Iron bars separate you from the corridor. You can hear the footsteps of guards patrolling nearby. Your fellow prisoners whisper plans of escape.",
    "Create My Own": "",
}


def get_image_artifact_value(artifact: Any) -> str | None:
    """Extract the URL/path from an ImageUrlArtifact or dict artifact."""
    if artifact is None:
        return None
    if isinstance(artifact, ImageUrlArtifact) and hasattr(artifact, "value"):
        return artifact.value
    if isinstance(artifact, dict) and "value" in artifact:
        return artifact["value"]
    return None


def _initialize_run_scenario_state() -> None:
    """Initialize Run Scenario state."""
    if "scenario_prefab" not in st.session_state:
        st.session_state.scenario_prefab = "Retrieve the Orb of Wonder"
    if "scenario_text" not in st.session_state:
        st.session_state.scenario_text = SCENARIO_PREFABS["Retrieve the Orb of Wonder"]
    if "scene_prefab" not in st.session_state:
        st.session_state.scene_prefab = "Throne Room Confrontation"
    if "scene_text" not in st.session_state:
        st.session_state.scene_text = SCENE_PREFABS["Throne Room Confrontation"]
    if "facts_json" not in st.session_state:
        st.session_state.facts_json = ""
    if "facts_generated" not in st.session_state:
        st.session_state.facts_generated = False
    if "generating_facts" not in st.session_state:
        st.session_state.generating_facts = False
    if "scenario_running" not in st.session_state:
        st.session_state.scenario_running = False
    if "scenario_turns" not in st.session_state:
        st.session_state.scenario_turns = []
    if "current_turn" not in st.session_state:
        st.session_state.current_turn = 0
    if "processing_turn" not in st.session_state:
        st.session_state.processing_turn = False
    # Initialize expander states (default to expanded)
    if "expander_setting" not in st.session_state:
        st.session_state.expander_setting = True
    if "expander_location" not in st.session_state:
        st.session_state.expander_location = True
    if "expander_scenario" not in st.session_state:
        st.session_state.expander_scenario = True
    if "expander_scene" not in st.session_state:
        st.session_state.expander_scene = True
    if "expander_characters" not in st.session_state:
        st.session_state.expander_characters = True
    if "expander_facts_editor" not in st.session_state:
        st.session_state.expander_facts_editor = True


def _check_dirty_state() -> bool:
    """Check if any upstream data is dirty (requires Generate Facts to be re-run)."""
    # Check if setting is dirty
    if st.session_state.get("setting_dirty", False):
        return True
    # Check if location is dirty
    if st.session_state.get("location_dirty", False):
        return True
    # Check if any character is dirty (but NOT portrait dirty - that's OK)
    characters = st.session_state.get("characters", [])
    for char in characters:
        if char.get("_dirty", False):
            return True
    # Check if scenario or scene changed
    if "prev_scenario_text" not in st.session_state:
        st.session_state.prev_scenario_text = st.session_state.get("scenario_text", "")
    if "prev_scene_text" not in st.session_state:
        st.session_state.prev_scene_text = st.session_state.get("scene_text", "")
    
    if st.session_state.get("scenario_text", "") != st.session_state.prev_scenario_text:
        return True
    if st.session_state.get("scene_text", "") != st.session_state.prev_scene_text:
        return True
    
    return False


def _validate_json(json_str: str) -> tuple[bool, str | None]:
    """Validate JSON string. Returns (is_valid, error_message)."""
    if not json_str or json_str.strip() == "":
        return False, "JSON is empty"
    try:
        json.loads(json_str)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)


async def _generate_facts_async() -> dict:
    """Generate facts using the fact_generation workflow."""
    context = st.session_state.get("context_text_area", "")
    tone = st.session_state.get("tone_text_area", "")
    location = st.session_state.get("location_text", "")
    scenario = st.session_state.get("scenario_text", "")
    scene = st.session_state.get("scene_text", "")
    
    # Get selected characters
    characters = st.session_state.get("characters", [])
    character_data = []
    for char in characters:
        # Filter out metadata fields
        char_display = {k: v for k, v in char.items() if not k.startswith("_")}
        character_data.append(char_display)

    # Convert characters to JSON string as workflow expects
    participants_json = json.dumps(character_data)

    flow_input = {
        "Start Flow": {
            "setting_context": context,
            "tone_and_direction": tone,
            "location": location,
            "scenario_description": scenario,
            "scene_description": scene,
            "participants": participants_json,
        }
    }
    
    manager = get_server_manager()
    port = manager.get_port("fact_generation")
    
    if port is None:
        return {
            "was_successful": False,
            "result_details": "Workflow server not configured",
            "facts": None,
        }
    
    try:
        output = await call_workflow_server(port, flow_input)

        if "error" in output:
            return {
                "was_successful": False,
                "result_details": f"Workflow error: {output['error']}",
                "facts": None,
            }

        # Extract facts from workflow output
        # The workflow returns was_successful, result_details, and facts
        return {
            "was_successful": output.get("was_successful", True),
            "result_details": output.get("result_details", "Facts generated successfully"),
            "facts": output.get("facts"),
        }
    except Exception as e:
        logger.exception("Failed to generate facts")
        return {
            "was_successful": False,
            "result_details": f"Failed to generate facts: {e}",
            "facts": None,
        }


async def _execute_turn_async(turn_number: int) -> dict:
    """Execute a single turn of the scenario."""
    facts_json = st.session_state.get("facts_json", "")
    
    if not facts_json:
        return {
            "was_successful": False,
            "result_details": "No facts available",
            "turn_data": None,
        }
    
    try:
        facts = json.loads(facts_json)
    except json.JSONDecodeError:
        return {
            "was_successful": False,
            "result_details": "Invalid facts JSON",
            "turn_data": None,
        }
    
    # TODO: Call actual turn execution workflow
    # For now, return placeholder data
    await asyncio.sleep(1)  # Simulate processing
    
    # Placeholder turn data structure
    turn_data = {
        "turn_number": turn_number,
        "character_actions": [],
        "adjudication": {
            "dm_decisions": [],
            "fact_changes": {},
            "narrative_summary": f"Turn {turn_number} placeholder narrative.",
        },
    }
    
    return {
        "was_successful": True,
        "result_details": f"Turn {turn_number} completed",
        "turn_data": turn_data,
    }


def _render_character_list_readonly() -> None:
    """Render read-only character list."""
    characters = st.session_state.get("characters", [])
    
    if not characters:
        st.info("No characters available. Go to the Characters tab to add characters.")
        return
    
    for char in characters:
        char_id = char.get("_id", "")
        char_name = char.get("name", "NO NAME PROVIDED")
        is_dirty = char.get("_dirty", False)
        portrait_url = char.get("_portrait_url")
        is_expanded = char.get("_expanded_readonly", False)
        
        # Determine portrait to show
        if portrait_url:
            portrait_display = portrait_url
        else:
            portrait_display = SILHOUETTE_PLACEHOLDER
        
        # Character name with asterisk if dirty
        name_display = f"{char_name}{' *' if is_dirty else ''}"
        
        # Use expander instead of button - expander icon automatically on the right
        with st.expander(f"**{name_display}**", expanded=is_expanded):
            # Add slight indentation
            _, content_col, _ = st.columns([0.02, 0.96, 0.02])
            
            with content_col:
                # Portrait thumbnail
                st.image(portrait_display, width=60)
                
                st.divider()
                
                # Display character JSON (read-only)
                display_data = {k: v for k, v in char.items() if not k.startswith("_")}
                st.json(display_data)


def _render_turn_log(turn: dict) -> None:
    """Render a single turn in the scenario log."""
    turn_num = turn.get("turn_number", 0)
    
    # Turn header
    st.markdown("---")
    st.markdown(f"### TURN {turn_num}")
    st.markdown("---")
    
    # Character actions (placeholder for now)
    character_actions = turn.get("character_actions", [])
    if character_actions:
        for action in character_actions:
            char_name = action.get("character_name", "Unknown")
            action_text = action.get("action", "")
            
            # Character row (collapsed by default)
            is_expanded = action.get("_expanded", False)
            
            col1, col2, col3 = st.columns([0.12, 0.75, 0.13])
            
            with col1:
                # Get character portrait
                characters = st.session_state.get("characters", [])
                char_data = next((c for c in characters if c.get("name") == char_name), None)
                portrait_url = char_data.get("_portrait_url") if char_data else None
                portrait_display = portrait_url if portrait_url else SILHOUETTE_PLACEHOLDER
                st.image(portrait_display, width=60)
            
            with col2:
                st.markdown(f"**{char_name}**: {action_text}")
            
            with col3:
                expand_icon = "▼" if is_expanded else "▶"
                if st.button(expand_icon, key=f"expand_action_{turn_num}_{char_name}", width='stretch'):
                    action["_expanded"] = not is_expanded
                    st.rerun()
            
            # Expanded view
            if is_expanded:
                st.json(action)
                st.divider()
    
    # Adjudication row
    adjudication = turn.get("adjudication", {})
    if adjudication:
        is_adj_expanded = adjudication.get("_expanded", False)
        
        col1, col2 = st.columns([0.9, 0.1])
        
        with col1:
            st.markdown("**ADJUDICATION**: Turn results and fact changes")
        
        with col2:
            expand_icon = "▼" if is_adj_expanded else "▶"
            if st.button(expand_icon, key=f"expand_adj_{turn_num}", width='stretch'):
                adjudication["_expanded"] = not is_adj_expanded
                st.rerun()
        
        if is_adj_expanded:
            st.json(adjudication)
            st.divider()
    
    # Next Turn button (only for the last turn)
    if turn_num == st.session_state.current_turn:
        if st.button("Next Turn", key=f"next_turn_{turn_num}", width='stretch'):
            st.session_state.processing_turn = True
            st.rerun()


def render() -> None:
    """Render the Run Scenario page."""
    _initialize_run_scenario_state()
    
    st.header("Run Scenario")
    st.markdown("Configure and execute turn-based multi-character role-playing scenarios.")
    
    # Three-panel layout
    left_col, right_col = st.columns([0.55, 0.45])
    
    with left_col:
        # Top-left panel
        with st.container():
            st.subheader("Configuration")
            
            # Setting Display (Read-Only) - Collapsible
            with st.expander("**Setting**", expanded=st.session_state.expander_setting):
                context = st.session_state.get("context_text_area", "")
                tone = st.session_state.get("tone_text_area", "")
                
                if context:
                    st.text_area("Context:", value=context, height=80, disabled=True, key="context_display_readonly")
                else:
                    st.info("No context configured.")
                
                if tone:
                    st.text_area("Tone & Direction:", value=tone, height=80, disabled=True, key="tone_display_readonly")
                else:
                    st.info("No tone configured.")
            
            # Location Display (Read-Only) - Collapsible
            with st.expander("**Location**", expanded=st.session_state.expander_location):
                location = st.session_state.get("location_text", "")
                if location:
                    st.text_area("Location:", value=location, height=100, disabled=True, key="location_display_readonly")
                else:
                    st.info("No location configured.")
            
            # Scenario Configuration - Collapsible
            with st.expander("**Scenario**", expanded=st.session_state.expander_scenario):
                scenario_options = list(SCENARIO_PREFABS.keys())
                selected_scenario = st.selectbox(
                    "Scenario",
                    options=scenario_options,
                    index=scenario_options.index(st.session_state.scenario_prefab),
                    key="scenario_dropdown",
                    disabled=st.session_state.scenario_running,
                )
                
                # Handle scenario dropdown change
                if selected_scenario != st.session_state.scenario_prefab:
                    st.session_state.scenario_prefab = selected_scenario
                    if selected_scenario == "Create My Own":
                        st.session_state.scenario_text = ""
                    else:
                        st.session_state.scenario_text = SCENARIO_PREFABS[selected_scenario]
                    # Clear facts if scenario changed
                    if st.session_state.facts_generated:
                        st.session_state.facts_json = ""
                        st.session_state.facts_generated = False
                    st.rerun()
                
                scenario_text = st.text_area(
                    "Scenario",
                    value=st.session_state.scenario_text,
                    height=150,
                    key="scenario_text_area",
                    label_visibility="collapsed",
                    disabled=st.session_state.scenario_running,
                )
                
                # Track scenario text changes
                if scenario_text != st.session_state.get("prev_scenario_text", ""):
                    st.session_state.scenario_text = scenario_text
                    st.session_state.prev_scenario_text = scenario_text
                    # Clear facts if scenario changed
                    if st.session_state.facts_generated:
                        st.session_state.facts_json = ""
                        st.session_state.facts_generated = False
            
            # Scene Configuration - Collapsible
            with st.expander("**Scene**", expanded=st.session_state.expander_scene):
                scene_options = list(SCENE_PREFABS.keys())
                selected_scene = st.selectbox(
                    "Scene",
                    options=scene_options,
                    index=scene_options.index(st.session_state.scene_prefab),
                    key="scene_dropdown",
                    disabled=st.session_state.scenario_running,
                )
                
                # Handle scene dropdown change
                if selected_scene != st.session_state.scene_prefab:
                    st.session_state.scene_prefab = selected_scene
                    if selected_scene == "Create My Own":
                        st.session_state.scene_text = ""
                    else:
                        st.session_state.scene_text = SCENE_PREFABS[selected_scene]
                    # Clear facts if scene changed
                    if st.session_state.facts_generated:
                        st.session_state.facts_json = ""
                        st.session_state.facts_generated = False
                    st.rerun()
                
                scene_text = st.text_area(
                    "Scene",
                    value=st.session_state.scene_text,
                    height=150,
                    key="scene_text_area",
                    label_visibility="collapsed",
                    disabled=st.session_state.scenario_running,
                )
                
                # Track scene text changes
                if scene_text != st.session_state.get("prev_scene_text", ""):
                    st.session_state.scene_text = scene_text
                    st.session_state.prev_scene_text = scene_text
                    # Clear facts if scene changed
                    if st.session_state.facts_generated:
                        st.session_state.facts_json = ""
                        st.session_state.facts_generated = False
            
            # Character List (Read-Only) - Collapsible
            with st.expander("**Character List**", expanded=st.session_state.expander_characters):
                _render_character_list_readonly()
            
            # Generate Facts Button
            any_processing = st.session_state.generating_facts or st.session_state.processing_turn
            generate_label = "Generating Facts..." if st.session_state.generating_facts else "Generate Facts"
            
            if st.button(
                generate_label,
                key="generate_facts",
                disabled=any_processing or st.session_state.scenario_running,
                width='stretch',
                type="primary",
            ):
                st.session_state.generating_facts = True
                st.rerun()
            
            # Message Display
            if not st.session_state.facts_generated:
                st.info("Click Generate Facts to populate")
            elif _check_dirty_state():
                st.warning("⚠ Regenerate Facts - upstream data has changed")
            
            # Run Scenario Button
            facts_valid = False
            if st.session_state.facts_json:
                is_valid, _ = _validate_json(st.session_state.facts_json)
                facts_valid = is_valid
            
            can_run = (
                st.session_state.facts_generated
                and not _check_dirty_state()
                and facts_valid
                and not st.session_state.scenario_running
            )
            
            run_label = "Stop Scenario" if st.session_state.scenario_running else "Run Scenario"
            
            if st.button(
                run_label,
                key="run_scenario",
                disabled=not can_run and not st.session_state.scenario_running,
                width='stretch',
                type="primary" if not st.session_state.scenario_running else "secondary",
            ):
                if st.session_state.scenario_running:
                    # Stop scenario
                    st.session_state.scenario_running = False
                    st.session_state.processing_turn = False
                    st.rerun()
                else:
                    # Start scenario
                    st.session_state.scenario_running = True
                    st.session_state.current_turn = 0
                    st.session_state.scenario_turns = []
                    st.rerun()
        
        # Bottom-left panel: Facts JSON Editor - Collapsible
        with st.expander("**Facts JSON Editor**", expanded=st.session_state.expander_facts_editor):
            facts_placeholder = "Click Generate Facts to populate"
            facts_value = st.session_state.facts_json if st.session_state.facts_json else facts_placeholder
            
            facts_disabled = (
                not st.session_state.facts_generated
                or st.session_state.generating_facts
                or st.session_state.processing_turn
            )
            
            facts_text = st.text_area(
                "Facts JSON",
                value=facts_value if st.session_state.facts_generated else facts_placeholder,
                height=400,
                key="facts_json_editor",
                label_visibility="collapsed",
                disabled=facts_disabled,
            )
            
            # Validate and update facts JSON
            if st.session_state.facts_generated and facts_text != facts_placeholder:
                is_valid, error_msg = _validate_json(facts_text)
                if not is_valid:
                    st.error(f"Invalid JSON: {error_msg}")
                else:
                    st.session_state.facts_json = facts_text
    
    with right_col:
        # Right panel: Scenario Log
        st.subheader("Scenario Log")
        
        if not st.session_state.scenario_running and not st.session_state.scenario_turns:
            st.info("Scenario log will appear here")
        else:
            # Display all turns
            for turn in st.session_state.scenario_turns:
                _render_turn_log(turn)
            
            # Show processing indicator if processing
            if st.session_state.processing_turn:
                with st.spinner(f"Processing Turn {st.session_state.current_turn + 1}..."):
                    pass
    
    # Handle Generate Facts workflow
    if st.session_state.generating_facts:
        try:
            result = asyncio.run(_generate_facts_async())
            if result.get("was_successful"):
                facts = result.get("facts", {})
                st.session_state.facts_json = json.dumps(facts, indent=2)
                st.session_state.facts_generated = True
                st.session_state.prev_scenario_text = st.session_state.scenario_text
                st.session_state.prev_scene_text = st.session_state.scene_text
                st.success("✓ Facts generated successfully!")
            else:
                st.error(f"✗ Failed to generate facts: {result.get('result_details', 'Unknown error')}")
        except Exception as e:
            st.error(f"✗ Facts generation failed: {e}")
        finally:
            st.session_state.generating_facts = False
            st.rerun()
    
    # Handle turn processing
    if st.session_state.processing_turn and st.session_state.scenario_running:
        try:
            turn_num = st.session_state.current_turn + 1
            result = asyncio.run(_execute_turn_async(turn_num))
            logger.info(f"Turn {turn_num} response: {json.dumps(result, indent=2)}")
            if result.get("was_successful"):
                turn_data = result.get("turn_data", {})
                st.session_state.scenario_turns.append(turn_data)
                st.session_state.current_turn = turn_num
                # Update facts JSON with changes from turn
                # TODO: Apply fact changes from adjudication
            else:
                st.error(f"✗ Turn {turn_num} failed: {result.get('result_details', 'Unknown error')}")
        except Exception as e:
            logger.exception(f"Turn execution failed: {e}")
            st.error(f"✗ Turn execution failed: {e}")
        finally:
            st.session_state.processing_turn = False
            st.rerun()
