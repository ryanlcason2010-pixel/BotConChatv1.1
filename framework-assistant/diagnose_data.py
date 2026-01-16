#!/usr/bin/env python3
"""
Quick diagnostic for framework data quality issues.
"""

import pandas as pd
import sys

def diagnose_framework_data(file_path='data/frameworks.xlsx'):
    """Diagnose framework data issues."""
    
    print("🔍 Framework Data Diagnostic\n")
    print("="*60)
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"✓ Loaded {len(df)} frameworks\n")
    except Exception as e:
        print(f"❌ ERROR: Could not load file: {e}")
        return
    
    # Issue 1: Duplicate IDs
    print("1. CHECKING FOR DUPLICATE IDs")
    print("-"*60)
    duplicate_ids = df[df['id'].duplicated(keep=False)]
    if len(duplicate_ids) > 0:
        print(f"❌ Found {len(duplicate_ids)} rows with duplicate IDs:")
        print(duplicate_ids[['id', 'name']].to_string())
    else:
        print("✓ No duplicate IDs")
    print()
    
    # Issue 2: Names with numbers appended
    print("2. CHECKING FOR NAMES WITH APPENDED NUMBERS")
    print("-"*60)
    names_with_numbers = df[df['name'].str.contains(r'\s+\d+$', na=False, regex=True)]
    if len(names_with_numbers) > 0:
        print(f"⚠️  Found {len(names_with_numbers)} frameworks with numbers at end:")
        for idx, row in names_with_numbers.head(10).iterrows():
            print(f"  ID {row['id']}: '{row['name']}'")
        if len(names_with_numbers) > 10:
            print(f"  ... and {len(names_with_numbers) - 10} more")
    else:
        print("✓ No names with appended numbers")
    print()
    
    # Issue 3: Generic/structural names
    print("3. CHECKING FOR GENERIC STRUCTURAL NAMES")
    print("-"*60)
    generic_patterns = ['layer', 'framework \d+', 'module', 'component']
    generic_names = df[df['name'].str.contains('|'.join(generic_patterns), case=False, na=False)]
    if len(generic_names) > 0:
        print(f"⚠️  Found {len(generic_names)} frameworks with generic names:")
        for idx, row in generic_names.head(10).iterrows():
            print(f"  ID {row['id']}: '{row['name']}'")
        if len(generic_names) > 10:
            print(f"  ... and {len(generic_names) - 10} more")
    else:
        print("✓ No generic structural names")
    print()
    
    # Issue 4: Check specific problematic frameworks
    print("4. EXAMINING PROBLEMATIC FRAMEWORKS")
    print("-"*60)
    problem_names = ['Layer 3: IT Strategy Framework 4', 
                     'Layer 3: IT Strategy Framework 8',
                     'Layer 3: IT Strategy Framework 5',
                     'Technology-Enabled Delivery Framework 4']
    
    for name in problem_names:
        matches = df[df['name'] == name]
        if len(matches) > 0:
            print(f"\n'{name}':")
            row = matches.iloc[0]
            print(f"  ID: {row['id']}")
            print(f"  Type: {row.get('type', 'N/A')}")
            print(f"  Use Case: {row.get('use_case', 'N/A')[:100]}...")
        else:
            # Try partial match
            partial = df[df['name'].str.contains(name.split()[0], case=False, na=False)]
            if len(partial) > 0:
                print(f"\nNo exact match for '{name}', but found {len(partial)} similar:")
                print(partial[['id', 'name']].head(3).to_string())
    print()
    
    # Issue 5: Identical use cases
    print("5. CHECKING FOR IDENTICAL USE CASES")
    print("-"*60)
    use_case_counts = df.groupby('use_case').size()
    duplicates = use_case_counts[use_case_counts > 1]
    if len(duplicates) > 0:
        print(f"⚠️  Found {len(duplicates)} use cases shared by multiple frameworks:")
        for use_case, count in duplicates.head(5).items():
            print(f"\n  Used by {count} frameworks: '{use_case[:80]}...'")
            matching = df[df['use_case'] == use_case][['id', 'name']]
            print(matching.to_string(index=False))
    else:
        print("✓ All frameworks have unique use cases")
    print()
    
    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    
    issues = []
    if len(duplicate_ids) > 0:
        issues.append(f"❌ {len(duplicate_ids)} duplicate IDs")
    if len(names_with_numbers) > 0:
        issues.append(f"⚠️  {len(names_with_numbers)} names with numbers")
    if len(generic_names) > 0:
        issues.append(f"⚠️  {len(generic_names)} generic names")
    if len(duplicates) > 0:
        issues.append(f"⚠️  {len(duplicates)} duplicate use cases")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  {issue}")
        print("\n🔧 Run data cleaning script to fix these issues.")
        return False
    else:
        print("\n✅ No major data quality issues found!")
        return True


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'data/frameworks.xlsx'
    diagnose_framework_data(file_path)
