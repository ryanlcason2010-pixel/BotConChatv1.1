"""
Framework Index Component.

Provides quick search functionality and framework index UI components
for the Framework Library feature.
"""

import re
from typing import Dict, List, Any, Optional

import streamlit as st


def _clean_framework_name(name: str) -> str:
    """
    Clean framework name by stripping trailing numbers.

    Args:
        name: Original framework name

    Returns:
        Cleaned name without trailing numbers
    """
    return re.sub(r'\s+\d+$', '', name or '')


def fuzzy_search_frameworks(
    frameworks: List[Dict[str, Any]],
    query: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Perform fuzzy search on framework names.

    Uses simple substring matching with scoring based on match position.

    Args:
        frameworks: List of framework dicts
        query: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of matching frameworks sorted by relevance
    """
    if not query or len(query) < 2:
        return []

    query_lower = query.lower().strip()
    matches = []

    for fw in frameworks:
        name = fw.get('name', '')
        cleaned_name = _clean_framework_name(name)
        name_lower = cleaned_name.lower()

        # Check for matches
        if query_lower in name_lower:
            # Score based on position (earlier = better) and length match
            position = name_lower.find(query_lower)
            length_ratio = len(query_lower) / len(name_lower) if name_lower else 0

            # Bonus for exact start match
            start_bonus = 10 if position == 0 else 0

            score = start_bonus + length_ratio * 5 - position * 0.1

            matches.append({
                **fw,
                '_search_score': score,
                '_display_name': cleaned_name
            })

    # Sort by score (descending) and return top matches
    matches.sort(key=lambda x: x.get('_search_score', 0), reverse=True)

    # Deduplicate by cleaned name
    seen_names = set()
    unique_matches = []
    for m in matches:
        display_name = m.get('_display_name', '')
        if display_name not in seen_names:
            seen_names.add(display_name)
            unique_matches.append(m)
            if len(unique_matches) >= max_results:
                break

    return unique_matches


def render_quick_search(
    frameworks: List[Dict[str, Any]],
    compact: bool = False,
    key_prefix: str = "quick_search"
) -> Optional[int]:
    """
    Render the quick search component.

    Args:
        frameworks: List of all frameworks
        compact: If True, render in compact mode for sidebar
        key_prefix: Unique key prefix for Streamlit widgets

    Returns:
        Framework ID if one was selected, None otherwise
    """
    selected_fw_id = None

    # Search input
    placeholder = "Search frameworks..." if compact else "Quick search by name..."
    search_query = st.text_input(
        "Search",
        placeholder=placeholder,
        key=f"{key_prefix}_input",
        label_visibility="collapsed" if compact else "visible"
    )

    if search_query and len(search_query) >= 2:
        matches = fuzzy_search_frameworks(frameworks, search_query, max_results=5)

        if matches:
            if compact:
                # Compact mode: Show as selectbox
                options = ["Select a framework..."] + [
                    m.get('_display_name', m.get('name', 'Unknown'))
                    for m in matches
                ]
                selected_idx = st.selectbox(
                    "Results",
                    range(len(options)),
                    format_func=lambda i: options[i],
                    key=f"{key_prefix}_select",
                    label_visibility="collapsed"
                )
                if selected_idx > 0:
                    selected_fw_id = matches[selected_idx - 1].get('id')
            else:
                # Full mode: Show as clickable list
                st.markdown("**Matching frameworks:**")
                for i, match in enumerate(matches):
                    display_name = match.get('_display_name', match.get('name', 'Unknown'))
                    fw_type = match.get('type', '')
                    type_badge = f" ({fw_type})" if fw_type else ""

                    if st.button(
                        f"{display_name}{type_badge}",
                        key=f"{key_prefix}_btn_{i}",
                        use_container_width=True
                    ):
                        selected_fw_id = match.get('id')

                # View all link
                if len(matches) == 5:
                    st.caption(f"Showing top 5 results. Go to Library tab for full search.")
        else:
            st.caption("No matching frameworks found.")

    return selected_fw_id


def render_alphabet_jump_links(
    grouped_frameworks: Dict[str, List[Dict]],
    key_prefix: str = "alpha_jump"
) -> Optional[str]:
    """
    Render alphabetical jump links for quick navigation.

    Args:
        grouped_frameworks: Frameworks grouped by first letter
        key_prefix: Unique key prefix for Streamlit widgets

    Returns:
        Selected letter if clicked, None otherwise
    """
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["#"]
    selected_letter = None

    # Create two rows of letters
    cols_per_row = 14
    for row_start in range(0, len(alphabet), cols_per_row):
        row_letters = alphabet[row_start:row_start + cols_per_row]
        cols = st.columns(len(row_letters))

        for i, letter in enumerate(row_letters):
            with cols[i]:
                # Check if this letter has frameworks
                has_frameworks = letter in grouped_frameworks and len(grouped_frameworks[letter]) > 0

                if has_frameworks:
                    if st.button(
                        letter,
                        key=f"{key_prefix}_{letter}",
                        use_container_width=True
                    ):
                        selected_letter = letter
                else:
                    # Disabled style for empty letters
                    st.markdown(
                        f"<span style='color: #888; padding: 5px;'>{letter}</span>",
                        unsafe_allow_html=True
                    )

    return selected_letter


def group_frameworks_alphabetically(
    frameworks: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group frameworks by first letter of their cleaned name.

    Args:
        frameworks: List of framework dicts

    Returns:
        Dict mapping letters to list of frameworks
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    # Deduplicate by cleaned name first
    seen_names = set()
    unique_frameworks = []

    for fw in frameworks:
        name = fw.get('name', '')
        cleaned_name = _clean_framework_name(name)

        if cleaned_name and cleaned_name not in seen_names:
            seen_names.add(cleaned_name)
            unique_frameworks.append({
                **fw,
                '_display_name': cleaned_name
            })

    # Sort by cleaned name
    unique_frameworks.sort(key=lambda x: x.get('_display_name', '').upper())

    # Group by first letter
    for fw in unique_frameworks:
        display_name = fw.get('_display_name', '')
        if not display_name:
            continue

        first_char = display_name[0].upper()
        if first_char.isalpha():
            letter = first_char
        else:
            letter = "#"  # Non-alphabetic

        if letter not in grouped:
            grouped[letter] = []
        grouped[letter].append(fw)

    return grouped


def render_framework_card(
    framework: Dict[str, Any],
    show_details_btn: bool = True,
    key_prefix: str = "fw_card"
) -> Optional[int]:
    """
    Render a framework card for the library view.

    Args:
        framework: Framework dict
        show_details_btn: Whether to show "View Details" button
        key_prefix: Unique key prefix

    Returns:
        Framework ID if details button was clicked
    """
    selected_id = None
    display_name = framework.get('_display_name', framework.get('name', 'Unknown'))
    fw_type = framework.get('type', '')
    domains = framework.get('business_domains', '')
    difficulty = framework.get('difficulty_level', 'intermediate')

    # Card container
    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"**{display_name}**")
            if fw_type:
                st.caption(f"Type: {fw_type}")
            if domains:
                first_domain = domains.split(',')[0].strip() if domains else ''
                if first_domain:
                    st.caption(f"Domain: {first_domain}")

        with col2:
            if show_details_btn:
                if st.button(
                    "View",
                    key=f"{key_prefix}_{framework.get('id', 0)}_view",
                    type="secondary"
                ):
                    selected_id = framework.get('id')

        st.markdown("---")

    return selected_id
