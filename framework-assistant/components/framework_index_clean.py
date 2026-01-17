"""
Framework Index Components.

Quick search and framework browsing components for sidebar and main interface.
"""

from typing import List, Dict, Any, Optional, Tuple
import streamlit as st


def render_quick_search(
    all_frameworks: List[Dict[str, Any]],
    compact: bool = False
) -> Optional[int]:
    """
    Render quick framework search component.
    
    Args:
        all_frameworks: List of all framework dicts
        compact: If True, render in compact mode for sidebar
        
    Returns:
        Framework ID if user selected one, None otherwise
    """
    if compact:
        # Compact version for sidebar
        st.markdown("### Quick Find")
        search_query = st.text_input(
            "Framework name",
            placeholder="Type to search...",
            key="sidebar_quick_search",
            label_visibility="collapsed"
        )
    else:
        # Full version for main interface
        search_query = st.text_input(
            "Quick Framework Lookup",
            placeholder="Start typing framework name...",
            key="main_quick_search"
        )
    
    if search_query and len(search_query) >= 2:
        # Search for matches
        matches = fuzzy_search_frameworks(all_frameworks, search_query)
        
        if matches:
            # Show top 5 matches in dropdown
            top_matches = matches[:5]
            
            if compact:
                st.markdown("**Top Matches:**")
                for fw in top_matches:
                    if st.button(
                        f"{fw['name']}", 
                        key=f"quick_{fw['id']}_compact",
                        use_container_width=True
                    ):
                        return fw['id']
            else:
                # Full version with better formatting
                with st.container():
                    st.markdown("**Top Matches:**")
                    
                    for fw in top_matches:
                        if st.button(
                            f"{fw['name']}", 
                            key=f"quick_{fw['id']}",
                            use_container_width=True
                        ):
                            return fw['id']
            
            # "View all" link
            total_matches = len(matches)
            if total_matches > 5:
                if st.button(
                    f"View all {total_matches} matches in Library",
                    key="view_all_matches"
                ):
                    # Store search query and switch to library tab
                    st.session_state.library_search_query = search_query
                    st.session_state.switch_to_library = True
                    st.rerun()
        else:
            st.info("No frameworks found matching your search.")
    
    return None


def fuzzy_search_frameworks(
    frameworks: List[Dict[str, Any]], 
    query: str
) -> List[Dict[str, Any]]:
    """
    Fuzzy search frameworks by name.
    
    Args:
        frameworks: List of framework dicts
        query: Search query
        
    Returns:
        List of matching frameworks, sorted by relevance
    """
    query_lower = query.lower()
    matches = []
    
    for fw in frameworks:
        name = fw.get('name', '').lower()
        
        # Exact match (highest priority)
        if query_lower == name:
            matches.insert(0, (fw, 100))
        # Starts with query (high priority)
        elif name.startswith(query_lower):
            matches.append((fw, 90))
        # Contains query (medium priority)
        elif query_lower in name:
            matches.append((fw, 70))
        # Word boundary match (lower priority)
        elif any(word.startswith(query_lower) for word in name.split()):
            matches.append((fw, 50))
    
    # Sort by score and return frameworks only
    matches.sort(key=lambda x: x[1], reverse=True)
    return [fw for fw, score in matches]


def group_frameworks_alphabetically(
    frameworks: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group frameworks by first letter.
    
    Args:
        frameworks: List of framework dicts
        
    Returns:
        Dict mapping letter to list of frameworks
    """
    grouped = {}
    
    for fw in frameworks:
        name = fw.get('name', 'Unknown')
        first_letter = name[0].upper() if name else '#'
        
        # Handle non-alphabetic characters
        if not first_letter.isalpha():
            first_letter = '#'
        
        if first_letter not in grouped:
            grouped[first_letter] = []
        
        grouped[first_letter].append(fw)
    
    # Sort frameworks within each group
    for letter in grouped:
        grouped[letter].sort(key=lambda x: x.get('name', '').lower())
    
    # Return sorted by letter
    return dict(sorted(grouped.items()))


def render_framework_list_item(
    framework: Dict[str, Any],
    show_metadata: bool = True,
    key_prefix: str = ""
) -> bool:
    """
    Render a single framework list item.
    
    Args:
        framework: Framework dict
        show_metadata: Whether to show metadata badges
        key_prefix: Prefix for button key
        
    Returns:
        True if clicked, False otherwise
    """
    name = framework.get('name', 'Unknown')
    difficulty = framework.get('difficulty_level', 'intermediate')
    fw_type = framework.get('type', 'General')
    
    # Build display text
    if show_metadata:
        display = f"{name} [{difficulty}]"
    else:
        display = name
    
    return st.button(
        display,
        key=f"{key_prefix}fw_{framework.get('id')}",
        use_container_width=True
    )


def get_framework_navigation(
    current_id: int,
    all_frameworks: List[Dict[str, Any]]
) -> Tuple[Optional[int], Optional[int]]:
    """
    Get previous and next framework IDs for navigation.
    
    Args:
        current_id: Current framework ID
        all_frameworks: List of all frameworks (sorted)
        
    Returns:
        Tuple of (previous_id, next_id), None if at boundaries
    """
    # Find current index
    current_idx = None
    for i, fw in enumerate(all_frameworks):
        if fw.get('id') == current_id:
            current_idx = i
            break
    
    if current_idx is None:
        return None, None
    
    # Get previous and next
    prev_id = all_frameworks[current_idx - 1].get('id') if current_idx > 0 else None
    next_id = all_frameworks[current_idx + 1].get('id') if current_idx < len(all_frameworks) - 1 else None
    
    return prev_id, next_id


def render_navigation_buttons(
    prev_id: Optional[int],
    next_id: Optional[int],
    prev_name: Optional[str] = None,
    next_name: Optional[str] = None
) -> Optional[int]:
    """
    Render previous/next navigation buttons.
    
    Args:
        prev_id: Previous framework ID
        next_id: Next framework ID
        prev_name: Previous framework name (optional)
        next_name: Next framework name (optional)
        
    Returns:
        Framework ID if navigation clicked, None otherwise
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    
    clicked_id = None
    
    with col1:
        if prev_id:
            label = "Previous"
            if prev_name:
                label += f": {prev_name}"
            if st.button(label, key="nav_prev", use_container_width=True):
                clicked_id = prev_id
    
    with col3:
        if next_id:
            label = "Next"
            if next_name:
                label += f": {next_name}"
            if st.button(label, key="nav_next", use_container_width=True):
                clicked_id = next_id
    
    return clicked_id


def get_framework_name_by_id(
    framework_id: int,
    all_frameworks: List[Dict[str, Any]]
) -> str:
    """
    Get framework name by ID.
    
    Args:
        framework_id: Framework ID
        all_frameworks: List of all frameworks
        
    Returns:
        Framework name or "Unknown"
    """
    for fw in all_frameworks:
        if fw.get('id') == framework_id:
            return fw.get('name', 'Unknown')
    return 'Unknown'
