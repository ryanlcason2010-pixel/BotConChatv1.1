"""
Framework Library Handler.

Provides the Framework Library tab functionality including:
- Alphabetical framework browsing
- Framework detail pages
- Navigation between frameworks
- Related framework links
"""

import re
from typing import Dict, List, Any, Optional, Tuple

import streamlit as st

from components.framework_index import (
    group_frameworks_alphabetically,
    fuzzy_search_frameworks,
    render_alphabet_jump_links
)


def _clean_framework_name(name: str) -> str:
    """Clean framework name by stripping trailing numbers."""
    return re.sub(r'\s+\d+$', '', name or '')


def _format_display_name(framework: Dict[str, Any]) -> str:
    """Get display name for a framework."""
    return framework.get('_display_name', _clean_framework_name(framework.get('name', 'Unknown')))


def init_library_state():
    """Initialize library-related session state."""
    if 'library_view' not in st.session_state:
        st.session_state.library_view = 'index'  # 'index' or 'detail'
    if 'library_framework_id' not in st.session_state:
        st.session_state.library_framework_id = None
    if 'library_expanded_sections' not in st.session_state:
        st.session_state.library_expanded_sections = set(['A'])
    if 'library_search_query' not in st.session_state:
        st.session_state.library_search_query = ''
    if 'library_type_filter' not in st.session_state:
        st.session_state.library_type_filter = None
    if 'library_domain_filter' not in st.session_state:
        st.session_state.library_domain_filter = None


def navigate_to_framework(framework_id: int):
    """Navigate to a framework detail page."""
    st.session_state.library_view = 'detail'
    st.session_state.library_framework_id = framework_id


def navigate_to_index():
    """Navigate back to the library index."""
    st.session_state.library_view = 'index'
    st.session_state.library_framework_id = None


def get_unique_frameworks(frameworks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Get unique frameworks by cleaned name.

    Args:
        frameworks: List of all frameworks

    Returns:
        List of unique frameworks with display names
    """
    seen_names = set()
    unique = []

    for fw in frameworks:
        name = fw.get('name', '')
        cleaned_name = _clean_framework_name(name)

        if cleaned_name and cleaned_name not in seen_names:
            seen_names.add(cleaned_name)
            unique.append({
                **fw,
                '_display_name': cleaned_name
            })

    # Sort alphabetically
    unique.sort(key=lambda x: x.get('_display_name', '').upper())
    return unique


def get_framework_by_id(
    frameworks: List[Dict[str, Any]],
    framework_id: int
) -> Optional[Dict[str, Any]]:
    """
    Find a framework by ID.

    Args:
        frameworks: List of frameworks
        framework_id: ID to find

    Returns:
        Framework dict or None
    """
    for fw in frameworks:
        if fw.get('id') == framework_id:
            cleaned_name = _clean_framework_name(fw.get('name', ''))
            return {**fw, '_display_name': cleaned_name}
    return None


def get_prev_next_frameworks(
    unique_frameworks: List[Dict[str, Any]],
    current_id: int
) -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    Get previous and next frameworks for navigation.

    Args:
        unique_frameworks: Sorted list of unique frameworks
        current_id: Current framework ID

    Returns:
        Tuple of (previous_framework, next_framework)
    """
    current_idx = None
    for i, fw in enumerate(unique_frameworks):
        if fw.get('id') == current_id:
            current_idx = i
            break

    if current_idx is None:
        return None, None

    prev_fw = unique_frameworks[current_idx - 1] if current_idx > 0 else None
    next_fw = unique_frameworks[current_idx + 1] if current_idx < len(unique_frameworks) - 1 else None

    return prev_fw, next_fw


def render_framework_detail(
    framework: Dict[str, Any],
    unique_frameworks: List[Dict[str, Any]],
    all_frameworks: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Render the framework detail page.

    Args:
        framework: Framework to display
        unique_frameworks: List of unique frameworks for navigation
        all_frameworks: All frameworks for related lookups

    Returns:
        Action string if navigation requested ('back', 'chat', etc.)
    """
    action = None
    display_name = _format_display_name(framework)

    # Back button and navigation
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("Back to Library", key="lib_back_btn"):
            action = 'back'

    # Get prev/next for navigation
    prev_fw, next_fw = get_prev_next_frameworks(unique_frameworks, framework.get('id'))

    with col3:
        nav_cols = st.columns(2)
        with nav_cols[0]:
            if prev_fw:
                if st.button("Prev", key="lib_prev_btn"):
                    navigate_to_framework(prev_fw.get('id'))
                    st.rerun()
            else:
                st.button("Prev", key="lib_prev_btn_disabled", disabled=True)
        with nav_cols[1]:
            if next_fw:
                if st.button("Next", key="lib_next_btn"):
                    navigate_to_framework(next_fw.get('id'))
                    st.rerun()
            else:
                st.button("Next", key="lib_next_btn_disabled", disabled=True)

    st.markdown("---")

    # Framework header
    st.header(display_name)

    # Type and difficulty badges
    badge_cols = st.columns(3)
    with badge_cols[0]:
        fw_type = framework.get('type', 'General')
        st.markdown(f"**Type:** {fw_type}")
    with badge_cols[1]:
        difficulty = framework.get('difficulty_level', 'intermediate')
        st.markdown(f"**Difficulty:** {difficulty.title()}")
    with badge_cols[2]:
        priority = framework.get('priority_level', '')
        if priority:
            st.markdown(f"**Priority:** {priority}")

    st.markdown("---")

    # Business domains
    domains = framework.get('business_domains', '')
    if domains:
        st.markdown("**Business Domains:**")
        domain_list = [d.strip() for d in domains.split(',') if d.strip()]
        st.write(", ".join(domain_list))

    # Use case / Description
    use_case = framework.get('use_case', '')
    if use_case:
        st.markdown("**Use Case:**")
        st.write(use_case)

    # Diagnostic questions
    diag_questions = framework.get('diagnostic_questions', '')
    if diag_questions:
        st.markdown("**Diagnostic Questions:**")
        # Split by common delimiters
        questions = [q.strip() for q in re.split(r'[?]\s*', diag_questions) if q.strip()]
        for q in questions[:5]:  # Limit display
            st.markdown(f"- {q}?")
        if len(questions) > 5:
            st.caption(f"...and {len(questions) - 5} more questions")

    # Red flag indicators
    red_flags = framework.get('red_flag_indicators', '')
    if red_flags:
        st.markdown("**Red Flag Indicators:**")
        st.write(red_flags)

    # Levers
    levers = framework.get('levers', '')
    if levers:
        st.markdown("**Key Levers:**")
        st.write(levers)

    # Skills required
    skills = framework.get('skills_required', '')
    if skills:
        st.markdown("**Skills Required:**")
        st.write(skills)

    # Lifecycle stages
    lifecycle = framework.get('lifecycle_stages', '')
    if lifecycle:
        st.markdown("**Lifecycle Stages:**")
        st.write(lifecycle)

    # Related frameworks
    related = framework.get('related_canon', '') or framework.get('related_frameworks', '')
    if related:
        st.markdown("---")
        st.markdown("**Related Frameworks:**")

        # Try to parse related framework references
        related_items = [r.strip() for r in related.split(',') if r.strip()]
        if related_items:
            for item in related_items[:5]:
                st.markdown(f"- {item}")
        else:
            st.write(related)

    # Notes
    notes = framework.get('notes', '')
    if notes:
        st.markdown("---")
        st.markdown("**Notes:**")
        st.write(notes)

    st.markdown("---")

    # Action buttons
    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button("Ask about this framework in chat", key="lib_ask_chat", use_container_width=True):
            # Set up for chat query
            st.session_state.prefilled_query = f"Tell me about the {display_name}"
            action = 'chat'

    with action_cols[1]:
        st.button(
            "Start diagnostic flow",
            key="lib_diagnostic_btn",
            use_container_width=True,
            disabled=True,
            help="Coming soon - start a diagnostic session with this framework"
        )

    return action


def render_library_index(
    frameworks: List[Dict[str, Any]],
    unique_types: List[str],
    unique_domains: List[str]
) -> Optional[int]:
    """
    Render the library index view with alphabetical sections.

    Args:
        frameworks: All frameworks
        unique_types: List of unique framework types
        unique_domains: List of unique business domains

    Returns:
        Selected framework ID if one was clicked
    """
    selected_id = None

    # Filters row
    filter_cols = st.columns([2, 2, 2])

    with filter_cols[0]:
        type_options = ["All Types"] + unique_types
        selected_type = st.selectbox(
            "Type",
            type_options,
            key="lib_type_filter",
            label_visibility="collapsed"
        )
        if selected_type != "All Types":
            st.session_state.library_type_filter = selected_type
        else:
            st.session_state.library_type_filter = None

    with filter_cols[1]:
        # Get first domain from each comma-separated list
        domain_set = set()
        for d in unique_domains:
            first_domain = d.split(',')[0].strip() if d else ''
            if first_domain:
                domain_set.add(first_domain)
        domain_options = ["All Domains"] + sorted(domain_set)

        selected_domain = st.selectbox(
            "Domain",
            domain_options,
            key="lib_domain_filter",
            label_visibility="collapsed"
        )
        if selected_domain != "All Domains":
            st.session_state.library_domain_filter = selected_domain
        else:
            st.session_state.library_domain_filter = None

    with filter_cols[2]:
        search_query = st.text_input(
            "Search",
            placeholder="Filter by name...",
            key="lib_search_input",
            label_visibility="collapsed"
        )
        st.session_state.library_search_query = search_query

    # Get unique frameworks
    unique_frameworks = get_unique_frameworks(frameworks)

    # Apply filters
    filtered = unique_frameworks
    if st.session_state.library_type_filter:
        filtered = [f for f in filtered if f.get('type', '') == st.session_state.library_type_filter]
    if st.session_state.library_domain_filter:
        filtered = [f for f in filtered
                    if st.session_state.library_domain_filter.lower() in (f.get('business_domains', '') or '').lower()]
    if st.session_state.library_search_query:
        filtered = fuzzy_search_frameworks(filtered, st.session_state.library_search_query, max_results=50)

    # Display count
    st.caption(f"Showing {len(filtered)} of {len(unique_frameworks)} frameworks")

    # If searching or filtering, show flat list
    if st.session_state.library_search_query or st.session_state.library_type_filter or st.session_state.library_domain_filter:
        selected_id = _render_flat_list(filtered)
    else:
        # Show alphabetical sections
        selected_id = _render_alphabetical_sections(filtered)

    return selected_id


def _render_flat_list(frameworks: List[Dict[str, Any]]) -> Optional[int]:
    """Render a flat list of frameworks."""
    selected_id = None

    for i, fw in enumerate(frameworks[:50]):  # Limit to 50
        display_name = _format_display_name(fw)
        fw_type = fw.get('type', '')
        type_badge = f" | {fw_type}" if fw_type else ""

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**{display_name}**{type_badge}")
        with col2:
            if st.button("View", key=f"flat_view_{i}"):
                selected_id = fw.get('id')

    if len(frameworks) > 50:
        st.caption(f"...and {len(frameworks) - 50} more. Refine your search to see more results.")

    return selected_id


def _render_alphabetical_sections(frameworks: List[Dict[str, Any]]) -> Optional[int]:
    """Render frameworks in alphabetical sections."""
    selected_id = None

    # Group by letter
    grouped = group_frameworks_alphabetically(frameworks)

    # Jump links
    st.markdown("**Jump to:**")
    selected_letter = render_alphabet_jump_links(grouped, key_prefix="lib_jump")
    if selected_letter:
        # Expand the selected section
        st.session_state.library_expanded_sections.add(selected_letter)

    st.markdown("---")

    # Render sections
    for letter in sorted(grouped.keys()):
        letter_frameworks = grouped[letter]

        # Section header with expand/collapse
        is_expanded = letter in st.session_state.library_expanded_sections
        header_cols = st.columns([5, 1])

        with header_cols[0]:
            st.markdown(f"### {letter} ({len(letter_frameworks)} frameworks)")

        with header_cols[1]:
            if is_expanded:
                if st.button("Collapse", key=f"collapse_{letter}"):
                    st.session_state.library_expanded_sections.discard(letter)
                    st.rerun()
            else:
                if st.button("Expand", key=f"expand_{letter}"):
                    st.session_state.library_expanded_sections.add(letter)
                    st.rerun()

        # Show frameworks if expanded
        if is_expanded:
            visible_count = min(10, len(letter_frameworks))
            show_more_key = f"show_more_{letter}"

            # Check if we should show more
            if show_more_key in st.session_state:
                visible_count = st.session_state[show_more_key]

            for i, fw in enumerate(letter_frameworks[:visible_count]):
                display_name = _format_display_name(fw)
                fw_type = fw.get('type', '')

                fw_cols = st.columns([5, 1])
                with fw_cols[0]:
                    st.markdown(f"**{display_name}**")
                    if fw_type:
                        st.caption(fw_type)
                with fw_cols[1]:
                    if st.button("View", key=f"view_{letter}_{i}"):
                        selected_id = fw.get('id')

            # Show more button if needed
            if visible_count < len(letter_frameworks):
                remaining = len(letter_frameworks) - visible_count
                if st.button(f"Show {min(10, remaining)} more...", key=f"more_{letter}"):
                    st.session_state[show_more_key] = visible_count + 10
                    st.rerun()

        st.markdown("---")

    return selected_id


def render_framework_library(
    frameworks: List[Dict[str, Any]],
    unique_types: List[str],
    unique_domains: List[str]
) -> Optional[str]:
    """
    Main entry point for rendering the Framework Library tab.

    Args:
        frameworks: All framework data
        unique_types: List of unique framework types
        unique_domains: List of unique business domains

    Returns:
        Action string if navigation to chat requested
    """
    init_library_state()

    action = None

    if st.session_state.library_view == 'detail' and st.session_state.library_framework_id:
        # Show detail page
        framework = get_framework_by_id(frameworks, st.session_state.library_framework_id)
        if framework:
            unique_frameworks = get_unique_frameworks(frameworks)
            action = render_framework_detail(framework, unique_frameworks, frameworks)
            if action == 'back':
                navigate_to_index()
                st.rerun()
        else:
            st.error("Framework not found")
            if st.button("Return to Library"):
                navigate_to_index()
                st.rerun()
    else:
        # Show index
        selected_id = render_library_index(frameworks, unique_types, unique_domains)
        if selected_id:
            navigate_to_framework(selected_id)
            st.rerun()

    return action
