"""Characters page for managing characters."""

import json
from pathlib import Path
from typing import Any

import streamlit as st

from utils import execute_portrait_generation


# Silhouette placeholder image (using a data URI for a simple placeholder)
SILHOUETTE_PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect width='100' height='100' fill='%23ddd'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='%23999'%3E?%3C/text%3E%3C/svg%3E"


def load_character_prefabs() -> list[dict]:
    """Load all character JSON files from the characters directory as pre-fabs."""
    characters_dir = Path("characters")
    prefabs = []
    
    if characters_dir.exists():
        for char_file in sorted(characters_dir.glob("*.json")):
            try:
                with open(char_file, "r", encoding="utf-8") as f:
                    char_data = json.load(f)
                    char_data["_prefab_filename"] = char_file.name
                    prefabs.append(char_data)
            except Exception as e:
                st.warning(f"Failed to load {char_file.name}: {e}")
    
    return prefabs


def _initialize_characters_state() -> None:
    """Initialize characters state with default pre-selected characters."""
    if "characters" not in st.session_state:
        # Load 5-6 pre-selected characters
        prefabs = load_character_prefabs()
        initial_characters = []
        
        # Select first 5-6 characters as initial
        for i, prefab in enumerate(prefabs[:6]):
            char_data = json.loads(json.dumps(prefab))  # Deep copy
            char_data["_id"] = f"char_{i}"
            char_data["_prefab_name"] = prefab.get("name", "Unknown")
            char_data["_expanded"] = False
            char_data["_dirty"] = True  # Characters are dirty on load and need portraits generated
            char_data["_portrait_generated"] = False
            char_data["_portrait_url"] = None
            initial_characters.append(char_data)
        
        st.session_state.characters = initial_characters
        st.session_state.next_character_id = len(initial_characters)
        st.session_state.next_new_character_num = 1
    
    if "portrait_generating" not in st.session_state:
        st.session_state.portrait_generating = False
    if "portrait_generating_char_id" not in st.session_state:
        st.session_state.portrait_generating_char_id = None
    if "batch_portrait_generating" not in st.session_state:
        st.session_state.batch_portrait_generating = False


def _get_character_name(char_data: dict) -> str:
    """Get character name from JSON, or return default."""
    return char_data.get("name", "NO NAME PROVIDED")


def _mark_character_dirty(char_id: str) -> None:
    """Mark a specific character as dirty."""
    for char in st.session_state.characters:
        if char.get("_id") == char_id:
            char["_dirty"] = True
            break


def _mark_all_characters_dirty() -> None:
    """Mark all characters as dirty (e.g., when setting changes)."""
    for char in st.session_state.characters:
        char["_dirty"] = True


def _check_setting_changed() -> None:
    """Check if setting changed and mark characters dirty if needed."""
    setting_dirty = st.session_state.get("setting_dirty", False)
    if setting_dirty:
        # Check if we've already marked characters dirty for this setting change
        last_setting_dirty = st.session_state.get("_last_setting_dirty_state", False)
        if setting_dirty != last_setting_dirty:
            # Update state tracking BEFORE marking dirty to prevent rerun during tab navigation
            st.session_state._last_setting_dirty_state = setting_dirty
            _mark_all_characters_dirty()


def _validate_json(json_str: str) -> tuple[bool, str | None]:
    """Validate JSON string. Returns (is_valid, error_message)."""
    try:
        json.loads(json_str)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)


def _get_character_json_string(char_data: dict) -> str:
    """Get the character data as a JSON string."""
    # Filter out metadata fields (those starting with _)
    display_data = {k: v for k, v in char_data.items() if not k.startswith("_")}
    return json.dumps(display_data)


def _generate_portrait(char_id: str, context: str, tone: str, char_data: dict) -> str | None:
    """Generate portrait for a character. Returns portrait URL or None."""
    try:
        # Get character data as JSON string
        char_json_string = _get_character_json_string(char_data)
        char_name = char_data.get("name", "unknown")

        # Create character name to JSON string mapping
        character_name_to_json = {char_name: char_json_string}

        # Call the portrait generation workflow
        result = execute_portrait_generation(
            context=context,
            tone=tone,
            character_name_to_json=character_name_to_json,
        )

        if result.get("was_successful"):
            # Extract portrait URL for this character
            portraits = result.get("portraits", {})
            portrait_url = portraits.get(char_name)
            return portrait_url
        else:
            st.error(f"Portrait generation failed: {result.get('result_details')}")
            return None
    except Exception as e:
        st.error(f"Portrait generation error: {e}")
        return None


def _get_prefab_options() -> list[str]:
    """Get list of pre-fab option names."""
    prefabs = load_character_prefabs()
    options = [prefab.get("name", "Unknown") for prefab in prefabs]
    options.append("Create My Own")
    return options


def _get_prefab_by_name(name: str) -> dict | None:
    """Get pre-fab data by name."""
    if name == "Create My Own":
        return None
    prefabs = load_character_prefabs()
    for prefab in prefabs:
        if prefab.get("name") == name:
            return prefab
    return None


def _create_new_character_json(num: int) -> dict:
    """Create a new character JSON with default structure."""
    return {"name": f"NEW CHARACTER {num}"}


def render_character_row(char_data: dict, index: int) -> None:
    """Render a single character row (collapsed or expanded)."""
    char_id = char_data["_id"]
    is_expanded = char_data.get("_expanded", False)
    is_dirty = char_data.get("_dirty", False)
    char_name = _get_character_name(char_data)
    portrait_url = char_data.get("_portrait_url")
    is_generating = (
        st.session_state.portrait_generating
        and st.session_state.portrait_generating_char_id == char_id
    )
    any_generating = st.session_state.portrait_generating or st.session_state.batch_portrait_generating
    
    # Determine portrait to show
    if is_generating:
        portrait_display = SILHOUETTE_PLACEHOLDER  # Will show spinner overlay
    elif portrait_url:
        portrait_display = portrait_url
    else:
        portrait_display = SILHOUETTE_PLACEHOLDER
    
    # Row header (clickable to expand/collapse)
    col1, col2, col3 = st.columns([0.12, 0.75, 0.13])
    
    with col1:
        # Portrait thumbnail
        if is_generating:
            with st.spinner(""):
                st.image(portrait_display, width=80, use_container_width=False)
        else:
            st.image(portrait_display, width=80, use_container_width=False)
    
    with col2:
        # Character name with asterisk if dirty
        name_display = f"{char_name}{' *' if is_dirty else ''}"
        st.markdown(f"**{name_display}**")
    
    with col3:
        # Expand/collapse button
        expand_icon = "▼" if is_expanded else "▶"
        expand_label = "Collapse" if is_expanded else "Expand"
        if st.button(
            expand_icon,
            key=f"expand_{char_id}",
            help=expand_label,
            use_container_width=True,
        ):
            char_data["_expanded"] = not is_expanded
            st.rerun()
    
    # Expanded content (outside column layout)
    if is_expanded:
            st.divider()
            
            # Pre-fab dropdown
            prefab_options = _get_prefab_options()
            current_prefab_name = char_data.get("_prefab_name", "Create My Own")
            
            # Find current selection index
            try:
                current_index = prefab_options.index(current_prefab_name)
            except ValueError:
                current_index = len(prefab_options) - 1  # "Create My Own"
            
            selected_prefab = st.selectbox(
                "Pre-fab",
                options=prefab_options,
                index=current_index,
                key=f"prefab_{char_id}",
                disabled=any_generating,
            )
            
            # Handle pre-fab change
            if selected_prefab != current_prefab_name:
                char_data["_prefab_name"] = selected_prefab
                prefab_data = _get_prefab_by_name(selected_prefab)
                
                if prefab_data:
                    # Load pre-fab data
                    char_data.update(json.loads(json.dumps(prefab_data)))  # Deep copy
                    char_data["_portrait_url"] = None  # Clear portrait
                    char_data["_portrait_generated"] = False
                else:
                    # Create My Own
                    next_num = st.session_state.next_new_character_num
                    char_data.clear()
                    char_data.update(_create_new_character_json(next_num))
                    char_data["_id"] = char_id
                    char_data["_prefab_name"] = "Create My Own"
                    char_data["_expanded"] = True
                    char_data["_dirty"] = False
                    char_data["_portrait_generated"] = False
                    char_data["_portrait_url"] = None
                    st.session_state.next_new_character_num += 1
                
                _mark_character_dirty(char_id)
                st.rerun()
            
            # JSON Editor
            # Filter out metadata fields for display
            display_data = {k: v for k, v in char_data.items() if not k.startswith("_")}
            current_json_str = json.dumps(display_data, indent=2)
            
            json_editor_key = f"json_editor_{char_id}"
            json_text = st.text_area(
                "Character JSON",
                value=current_json_str,
                height=300,
                key=json_editor_key,
                disabled=any_generating,
                label_visibility="collapsed",
            )
            
            # Validate and update JSON
            is_valid, error_msg = _validate_json(json_text)
            
            if not is_valid and json_text != current_json_str:
                st.error(f"Invalid JSON: {error_msg}")
            
            # Update character data if JSON changed
            if json_text != current_json_str:
                try:
                    new_data = json.loads(json_text)
                    # Preserve metadata
                    metadata = {
                        "_id": char_data["_id"],
                        "_prefab_name": char_data.get("_prefab_name", "Create My Own"),
                        "_expanded": char_data.get("_expanded", True),
                        "_dirty": char_data.get("_dirty", False),
                        "_portrait_generated": char_data.get("_portrait_generated", False),
                        "_portrait_url": char_data.get("_portrait_url"),
                    }
                    char_data.clear()
                    char_data.update(new_data)
                    char_data.update(metadata)
                    _mark_character_dirty(char_id)
                except json.JSONDecodeError:
                    pass  # Error already shown above
            
            # Buttons row
            col_btn1, col_btn2 = st.columns([1, 1])
            
            with col_btn1:
                button_label = "Generating..." if is_generating else "Regenerate Portrait"
                if st.button(
                    button_label,
                    key=f"regenerate_{char_id}",
                    disabled=any_generating,
                    use_container_width=True,
                ):
                    st.session_state.portrait_generating = True
                    st.session_state.portrait_generating_char_id = char_id
                    st.rerun()
            
            with col_btn2:
                if st.button(
                    "Delete",
                    key=f"delete_{char_id}",
                    disabled=any_generating,
                    use_container_width=True,
                ):
                    st.session_state.characters = [
                        c for c in st.session_state.characters if c.get("_id") != char_id
                    ]
                    st.rerun()
        
            st.divider()


def render() -> None:
    """Render the Characters page."""
    _initialize_characters_state()
    _check_setting_changed()

    # Show indicator if setting changed and characters need regeneration
    setting_dirty = st.session_state.get("setting_dirty", False)
    header_text = "Characters*" if setting_dirty else "Characters"

    st.header(header_text)
    st.markdown("Define characters with facts, generate AI portraits based on Setting + character facts.")
    
    # Top button: Regenerate Updated Characters
    any_generating = st.session_state.portrait_generating or st.session_state.batch_portrait_generating
    button_label = "Generating..." if st.session_state.batch_portrait_generating else "Regenerate Updated Characters"
    
    if st.button(
        button_label,
        key="regenerate_all",
        disabled=any_generating,
        use_container_width=True,
        type="primary",
    ):
        st.session_state.batch_portrait_generating = True
        st.rerun()
    
    # Character rows
    characters = st.session_state.get("characters", [])
    
    if not characters:
        st.info("No characters. Click '+ Add Character' to add one.")
    else:
        for index, char_data in enumerate(characters):
            render_character_row(char_data, index)
    
    # Add Character button
    if st.button(
        "+ Add Character",
        key="add_character",
        disabled=any_generating,
        use_container_width=True,
    ):
        new_char = _create_new_character_json(st.session_state.next_new_character_num)
        new_char["_id"] = f"char_{st.session_state.next_character_id}"
        new_char["_prefab_name"] = "Create My Own"
        new_char["_expanded"] = True
        new_char["_dirty"] = False
        new_char["_portrait_generated"] = False
        new_char["_portrait_url"] = None
        
        st.session_state.characters.append(new_char)
        st.session_state.next_character_id += 1
        st.session_state.next_new_character_num += 1
        st.rerun()
    
    # Handle portrait generation
    if st.session_state.portrait_generating and st.session_state.portrait_generating_char_id:
        # Get context and tone from session state
        context = st.session_state.get("context_text_area", "")
        tone = st.session_state.get("tone_text_area", "")

        char_id = st.session_state.portrait_generating_char_id
        for char in st.session_state.characters:
            if char.get("_id") == char_id:
                # Call actual portrait generation
                portrait_url = _generate_portrait(char_id, context, tone, char)
                char["_portrait_url"] = portrait_url
                char["_portrait_generated"] = True
                char["_dirty"] = False  # Clear dirty state
                break
        st.session_state.portrait_generating = False
        st.session_state.portrait_generating_char_id = None
        st.rerun()

    if st.session_state.batch_portrait_generating:
        # Get context and tone from session state
        context = st.session_state.get("context_text_area", "")
        tone = st.session_state.get("tone_text_area", "")

        # Build character name to JSON string mapping for all dirty characters
        character_name_to_json = {}
        dirty_chars = []

        for char in st.session_state.characters:
            if char.get("_dirty", False):
                dirty_chars.append(char)
                char_json_string = _get_character_json_string(char)
                char_name = char.get("name", "unknown")
                character_name_to_json[char_name] = char_json_string

        if character_name_to_json:
            # Call portrait generation for all dirty characters at once
            try:
                result = execute_portrait_generation(
                    context=context,
                    tone=tone,
                    character_name_to_json=character_name_to_json,
                )

                if result.get("was_successful"):
                    portraits = result.get("portraits", {})
                    # Update each character with their portrait
                    for char in dirty_chars:
                        char_name = char.get("name", "unknown")
                        portrait_url = portraits.get(char_name)
                        char["_portrait_url"] = portrait_url
                        char["_portrait_generated"] = True
                        char["_dirty"] = False
                else:
                    st.error(f"Batch portrait generation failed: {result.get('result_details')}")
            except Exception as e:
                st.error(f"Batch portrait generation error: {e}")

        st.session_state.batch_portrait_generating = False
        st.rerun()
