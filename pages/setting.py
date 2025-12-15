"""Setting page for configuring the scenario setting."""

import streamlit as st


# Pre-fab options for Context
CONTEXT_PREFABS = {
    "Medieval Fantasy": "This is a typical fantasy world, D&D style. We are not using dice rolls or heavy statistics, but rather emphasizing storytelling.",
    "Sci-Fi Colony": "A remote space colony on the edge of known space, where technology and survival go hand in hand.",
    "Modern Urban": "A contemporary city setting with modern technology and real-world constraints.",
    "Post-Apocalyptic": "A world ravaged by disaster, where survivors must adapt to harsh new realities.",
    "Create My Own": "",
}

# Pre-fab options for Tone & Direction
TONE_PREFABS = {
    "Serious & Deadly": "This is presented as a serious and deadly experience. The good guys should be on their toes, and they might lose some friends along the way...",
    "Lighthearted Adventure": "A fun and adventurous tone where challenges are overcome with wit and teamwork.",
    "Dark & Gritty": "A grim world where moral ambiguity reigns and difficult choices must be made.",
    "Epic Fantasy": "A grand adventure with high stakes and heroic deeds.",
    "Create My Own": "",
}


def _initialize_setting_state() -> None:
    """Initialize setting state with default pre-fab selections."""
    if "context_prefab" not in st.session_state:
        st.session_state.context_prefab = "Medieval Fantasy"
    if "context_text_area" not in st.session_state:
        st.session_state.context_text_area = CONTEXT_PREFABS["Medieval Fantasy"]
    if "tone_prefab" not in st.session_state:
        st.session_state.tone_prefab = "Serious & Deadly"
    if "tone_text_area" not in st.session_state:
        st.session_state.tone_text_area = TONE_PREFABS["Serious & Deadly"]
    if "setting_dirty" not in st.session_state:
        st.session_state.setting_dirty = False
    if "prev_context_text" not in st.session_state:
        st.session_state.prev_context_text = st.session_state.context_text_area
    if "prev_tone_text" not in st.session_state:
        st.session_state.prev_tone_text = st.session_state.tone_text_area


def _mark_dirty() -> None:
    """Mark the setting as dirty (changed)."""
    st.session_state.setting_dirty = True


def render() -> None:
    """Render the Setting page."""
    _initialize_setting_state()
    
    st.header("Setting")
    st.markdown("Define world context and narrative tone for character/location generation.")
    
    # Context Dropdown
    context_options = list(CONTEXT_PREFABS.keys())
    selected_context = st.selectbox(
        "Context",
        options=context_options,
        index=context_options.index(st.session_state.context_prefab),
        key="context_dropdown",
    )
    
    # Handle context dropdown change
    if selected_context != st.session_state.context_prefab:
        st.session_state.context_prefab = selected_context
        if selected_context == "Create My Own":
            st.session_state.context_text_area = ""
        else:
            st.session_state.context_text_area = CONTEXT_PREFABS[selected_context]
        st.session_state.prev_context_text = st.session_state.context_text_area
        _mark_dirty()
        st.rerun()
    
    # Context Text Area
    st.text_area(
        "Context",
        height=150,
        key="context_text_area",
        label_visibility="collapsed",
    )
    
    # Track context text changes
    if st.session_state.context_text_area != st.session_state.prev_context_text:
        st.session_state.prev_context_text = st.session_state.context_text_area
        _mark_dirty()
    
    st.divider()
    
    # Tone & Direction Dropdown
    tone_options = list(TONE_PREFABS.keys())
    selected_tone = st.selectbox(
        "Tone & Direction",
        options=tone_options,
        index=tone_options.index(st.session_state.tone_prefab),
        key="tone_dropdown",
    )
    
    # Handle tone dropdown change
    if selected_tone != st.session_state.tone_prefab:
        st.session_state.tone_prefab = selected_tone
        if selected_tone == "Create My Own":
            st.session_state.tone_text_area = ""
        else:
            st.session_state.tone_text_area = TONE_PREFABS[selected_tone]
        st.session_state.prev_tone_text = st.session_state.tone_text_area
        _mark_dirty()
        st.rerun()
    
    # Tone & Direction Text Area
    st.text_area(
        "Tone & Direction",
        height=150,
        key="tone_text_area",
        label_visibility="collapsed",
    )
    
    # Track tone text changes
    if st.session_state.tone_text_area != st.session_state.prev_tone_text:
        st.session_state.prev_tone_text = st.session_state.tone_text_area
        _mark_dirty()
