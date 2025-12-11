"""Location page for managing locations."""

import streamlit as st


# Pre-fab options for Location
LOCATION_PREFABS = {
    "Ancient Throne Room": "An ancient throne room with stone walls, approximately 60 feet in length. Flickering torches are mounted on the walls providing dim illumination. At the far end sits an ornate obsidian throne, its dark surface reflecting the firelight. Tattered banners hang from the high ceiling, their colors faded with age. The air is still and heavy, carrying the scent of old stone and dust.",
    "Medieval Tavern": "A cozy medieval tavern with wooden beams overhead and a large fireplace crackling in the corner. Rough-hewn tables and benches fill the main room, while a bar runs along one wall stocked with barrels and bottles. The atmosphere is warm and inviting, though the floor is sticky with spilled ale. Patrons' voices create a low hum of conversation.",
    "Forest Clearing": "A peaceful forest clearing surrounded by ancient oak trees. Sunlight filters through the canopy, creating dappled patterns on the moss-covered ground. A small stream trickles nearby, its gentle sound providing a backdrop to the natural serenity. Wildflowers dot the edges of the clearing, and birds can be heard chirping in the distance.",
    "Abandoned Warehouse": "A large, abandoned warehouse with high ceilings and broken windows. Dust motes dance in the shafts of light that pierce through the grimy panes. Crates and barrels are scattered haphazardly, some overturned and spilling their contents. The air smells of rust, decay, and something metallic. Echoes seem to carry far in the empty space.",
    "Mystical Library": "An expansive library filled with towering bookshelves that reach toward a vaulted ceiling. Magical orbs float overhead, providing soft illumination. Ladders on rails allow access to the highest shelves. The scent of old parchment and leather bindings fills the air. Ancient tomes glow faintly with protective enchantments.",
    "Create My Own": "",
}


def _initialize_location_state() -> None:
    """Initialize location state with default pre-fab selection."""
    if "location_prefab" not in st.session_state:
        st.session_state.location_prefab = "Ancient Throne Room"
    if "location_text" not in st.session_state:
        st.session_state.location_text = LOCATION_PREFABS["Ancient Throne Room"]
    if "location_dirty" not in st.session_state:
        st.session_state.location_dirty = False
    if "prev_location_text" not in st.session_state:
        st.session_state.prev_location_text = st.session_state.location_text


def _mark_location_dirty() -> None:
    """Mark location as dirty (triggers dirty state on Run Scenario tab)."""
    st.session_state.location_dirty = True


def render() -> None:
    """Render the Location page."""
    _initialize_location_state()
    
    st.header("Location")
    st.markdown("Define the physical location/environment where scenarios take place.")
    
    # Location Pre-fab Dropdown
    location_options = list(LOCATION_PREFABS.keys())
    selected_location = st.selectbox(
        "Location Pre-fab",
        options=location_options,
        index=location_options.index(st.session_state.location_prefab),
        key="location_dropdown",
    )
    
    # Handle location dropdown change
    if selected_location != st.session_state.location_prefab:
        st.session_state.location_prefab = selected_location
        if selected_location == "Create My Own":
            st.session_state.location_text = ""
        else:
            st.session_state.location_text = LOCATION_PREFABS[selected_location]
        st.session_state.prev_location_text = st.session_state.location_text
        _mark_location_dirty()
        st.rerun()
    
    # Location Description Text Area
    location_text = st.text_area(
        "Location Description",
        value=st.session_state.location_text,
        height=300,
        key="location_text_area",
        label_visibility="collapsed",
        placeholder="Describe the location, environment, or scene for your scenario...",
    )
    
    # Track location text changes
    if location_text != st.session_state.prev_location_text:
        st.session_state.location_text = location_text
        st.session_state.prev_location_text = location_text
        _mark_location_dirty()
