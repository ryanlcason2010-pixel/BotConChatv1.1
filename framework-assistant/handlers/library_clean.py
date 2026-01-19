"""
Framework Library Handler.

Handles the Framework Library tab with alphabetical browsing,
filtering, and detail page views.
"""

from typing import Dict, List, Any, Optional, Tuple
import streamlit as st

from components.framework_index_clean import (
    group_frameworks_alphabetically,
    render_framework_list_item,
    get_framework_navigation,
    render_navigation_buttons,
    get_framework_name_by_id
)
from utils.search import SemanticSearch


def render_framework_library(
    all_frameworks: List[Dict[str, Any]],
    search_engine: SemanticSearch
) -> None:
    """
    Render the complete framework library interface.
    
    Args:
        all_frameworks: List of all framework dicts
        search_engine: Search engine for detail lookups
    """
    # Initialize session state
    if 'library_view' not in st.session_state:
        st.session_state.library_view = 'index'  # 'index' or 'detail'
    
    if 'library_framework_id' not in st.session_state:
        st.session_state.library_framework_id = None
    
    if 'library_search_query' not in st.session_state:
        st.session_state.library_search_query = ""
    
    if 'library_expanded_sections' not in st.session_state:
        st.session_state.library_expanded_sections = set()  # Nothing expanded by default
    
    # Render based on current view
    if st.session_state.library_view == 'detail' and st.session_state.library_framework_id:
        render_framework_detail_page(
            st.session_state.library_framework_id,
            all_frameworks,
            search_engine
        )
    else:
        render_framework_index_page(all_frameworks)


def render_framework_index_page(all_frameworks: List[Dict[str, Any]]) -> None:
    """
    Render the main framework index page with alphabetical sections.
    
    Args:
        all_frameworks: List of all framework dicts
    """
    # Header
    st.title("Framework Library")
    st.markdown(f"*{len(all_frameworks)} frameworks available*")
    st.markdown("---")
    
    # Search and filter row
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search frameworks",
            value=st.session_state.library_search_query,
            placeholder="Search by name...",
            key="library_search"
        )
        st.session_state.library_search_query = search_query
    
    with col2:
        # Get unique types
        all_types = sorted(set(fw.get('type', 'General') for fw in all_frameworks))
        type_filter = st.selectbox(
            "Type",
            options=['All'] + all_types,
            key="library_type_filter"
        )
    
    with col3:
        # Get unique domains (just first domain for filter)
        all_domains = set()
        for fw in all_frameworks:
            domains = fw.get('business_domains', '').split(',')
            if domains:
                all_domains.add(domains[0].strip())
        
        domain_filter = st.selectbox(
            "Domain",
            options=['All'] + sorted(all_domains),
            key="library_domain_filter"
        )
    
    # Apply filters
    filtered_frameworks = all_frameworks
    
    if type_filter != 'All':
        filtered_frameworks = [
            fw for fw in filtered_frameworks 
            if fw.get('type', '') == type_filter
        ]
    
    if domain_filter != 'All':
        filtered_frameworks = [
            fw for fw in filtered_frameworks
            if domain_filter in fw.get('business_domains', '')
        ]
    
    if search_query:
        # String search
        query_lower = search_query.lower()
        filtered_frameworks = [
            fw for fw in filtered_frameworks
            if query_lower in fw.get('name', '').lower()
        ]
    
    # Show count
    if len(filtered_frameworks) < len(all_frameworks):
        st.info(f"Showing {len(filtered_frameworks)} of {len(all_frameworks)} frameworks")
    
    st.markdown("---")
    
    # Render frameworks
    if search_query or type_filter != 'All' or domain_filter != 'All':
        # Filtered view: show flat list
        render_filtered_list(filtered_frameworks)
    else:
        # Default view: alphabetical sections
        render_alphabetical_sections(filtered_frameworks)


def render_alphabetical_sections(frameworks: List[Dict[str, Any]]) -> None:
    """
    Render frameworks in alphabetical sections.
    
    Args:
        frameworks: List of framework dicts to display
    """
    # Group by letter
    grouped = group_frameworks_alphabetically(frameworks)
    
    # Jump links - Simple display
    st.markdown("**Jump to:** " + " | ".join(sorted(grouped.keys())))
    st.markdown("---")
    
    # Render each section
    for letter, letter_frameworks in grouped.items():
        render_alphabetical_section(letter, letter_frameworks)


def render_alphabetical_section(
    letter: str, 
    frameworks: List[Dict[str, Any]]
) -> None:
    """
    Render a single alphabetical section.
    
    Args:
        letter: Section letter
        frameworks: Frameworks in this section
    """
    # Section header
    is_expanded = letter in st.session_state.library_expanded_sections
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        st.markdown(f"### {letter} ({len(frameworks)} frameworks)")
    
    with col2:
        # Toggle button
        if is_expanded:
            if st.button("Collapse", key=f"toggle_{letter}"):
                st.session_state.library_expanded_sections.remove(letter)
                st.rerun()
        else:
            if st.button("Expand", key=f"toggle_{letter}"):
                st.session_state.library_expanded_sections.add(letter)
                st.rerun()
    
    st.markdown("---")
    
    # Show frameworks if expanded
    if is_expanded:
        # Show first 10
        visible_count = min(10, len(frameworks))
        
        for fw in frameworks[:visible_count]:
            if render_framework_list_item(fw, show_metadata=False, key_prefix=f"{letter}_"):
                # Navigate to detail page
                st.session_state.library_view = 'detail'
                st.session_state.library_framework_id = fw.get('id')
                st.rerun()
        
        # Show "load more" if needed
        if len(frameworks) > visible_count:
            remaining = len(frameworks) - visible_count
            if st.button(f"Show {min(remaining, 10)} more... ({remaining} remaining)", key=f"more_{letter}"):
                # Expand this section fully
                st.session_state[f'section_{letter}_full'] = True
                st.rerun()
        
        # Show remaining if fully expanded
        if st.session_state.get(f'section_{letter}_full', False):
            for fw in frameworks[visible_count:]:
                if render_framework_list_item(fw, show_metadata=False, key_prefix=f"{letter}_full_"):
                    st.session_state.library_view = 'detail'
                    st.session_state.library_framework_id = fw.get('id')
                    st.rerun()
    
    st.markdown("")  # Spacing


def render_filtered_list(frameworks: List[Dict[str, Any]]) -> None:
    """
    Render frameworks as flat filtered list.
    
    Args:
        frameworks: Filtered frameworks to display
    """
    if not frameworks:
        st.warning("No frameworks match your filters.")
        return
    
    st.markdown(f"### Search Results ({len(frameworks)})")
    st.markdown("---")
    
    # Show all results (paginate if > 50)
    page_size = 50
    
    if len(frameworks) > page_size:
        total_pages = (len(frameworks) + page_size - 1) // page_size
        page = st.selectbox("Page", range(1, total_pages + 1), key="filtered_page")
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        frameworks_to_show = frameworks[start_idx:end_idx]
    else:
        frameworks_to_show = frameworks
    
    # Render frameworks
    for fw in frameworks_to_show:
        if render_framework_list_item(fw, show_metadata=True, key_prefix="filtered_"):
            st.session_state.library_view = 'detail'
            st.session_state.library_framework_id = fw.get('id')
            st.rerun()


def render_framework_detail_page(
    framework_id: int,
    all_frameworks: List[Dict[str, Any]],
    search_engine: SemanticSearch
) -> None:
    """
    Render detailed framework page.
    
    Args:
        framework_id: Framework ID to display
        all_frameworks: All frameworks for navigation
        search_engine: Search engine for lookups
    """
    # Get framework data
    result = search_engine.get_framework_by_id(framework_id)
    
    if not result:
        st.error("Framework not found.")
        if st.button("Back to Library"):
            st.session_state.library_view = 'index'
            st.rerun()
        return
    
    framework = result.framework_data
    
    # Navigation header
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Back to Library", key="back_to_library"):
            st.session_state.library_view = 'index'
            st.rerun()
    
    with col2:
        if st.button("Ask about this framework in chat", key="ask_in_chat"):
            # Set up chat with pre-filled query
            st.session_state.prefill_query = f"Tell me more about {framework.get('name')}"
            st.session_state.switch_to_chat = True
            st.rerun()
    
    st.markdown("---")
    
    # Framework title and metadata
    name = framework.get('name', 'Unknown')
    fw_type = framework.get('type', 'General')
    difficulty = framework.get('difficulty_level', 'intermediate')
    domains = framework.get('business_domains', '')
    
    st.title(name)
    st.markdown(f"**{fw_type}** • **{difficulty.capitalize()}** • {domains}")
    
    st.markdown("---")
    
    # What it is
    st.markdown("### What it is")
    use_case = framework.get('use_case', 'No description available.')
    st.markdown(use_case)
    
    st.markdown("")
    
    # When to use it
    st.markdown("### When to use it")
    symptoms = framework.get('problem_symptoms', 'Not specified.')
    st.markdown(symptoms)
    
    st.markdown("")
    
    # Business domains
    st.markdown("### Business domains")
    st.markdown(domains)
    
    st.markdown("---")
    
    # Related frameworks
    related_str = framework.get('related_frameworks', '')
    if related_str:
        st.markdown("### Related frameworks")
        
        try:
            related_ids = [int(x.strip()) for x in related_str.split(',') if x.strip()]
            
            if related_ids:
                for rid in related_ids:
                    related_result = search_engine.get_framework_by_id(rid)
                    if related_result:
                        related_name = related_result.framework_data.get('name', 'Unknown')
                        if st.button(f"{related_name}", key=f"related_{rid}"):
                            st.session_state.library_framework_id = rid
                            st.rerun()
            else:
                st.markdown("*No related frameworks defined*")
        except ValueError:
            st.markdown("*Error loading related frameworks*")
    else:
        st.markdown("### Related frameworks")
        st.markdown("*No related frameworks defined*")
    
    st.markdown("---")
    
    # Previous/Next navigation
    prev_id, next_id = get_framework_navigation(framework_id, all_frameworks)
    
    # Get names for prev/next
    prev_name = get_framework_name_by_id(prev_id, all_frameworks) if prev_id else None
    next_name = get_framework_name_by_id(next_id, all_frameworks) if next_id else None
    
    clicked_nav = render_navigation_buttons(prev_id, next_id, prev_name, next_name)
    
    if clicked_nav:
        st.session_state.library_framework_id = clicked_nav
        st.rerun()
