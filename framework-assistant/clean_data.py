#!/usr/bin/env python3
"""
Framework Data Cleaning Script.

Fixes common data quality issues:
- Removes duplicate frameworks
- Cleans up framework names (removes appended numbers)
- Consolidates frameworks with identical use cases
- Generates clean output file
"""

import pandas as pd
import sys
from pathlib import Path


def clean_framework_data(input_file='data/frameworks.xlsx', output_file=None):
    """
    Clean framework data and save to new file.
    
    Args:
        input_file: Input Excel file path
        output_file: Output Excel file path (default: input_file with '_cleaned' suffix)
    """
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_cleaned{input_path.suffix}"
    
    print("🧹 Framework Data Cleaning\n")
    print("="*60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print("="*60)
    print()
    
    # Load data
    try:
        df = pd.read_excel(input_file, engine='openpyxl')
        print(f"✓ Loaded {len(df)} frameworks\n")
    except Exception as e:
        print(f"❌ ERROR: Could not load file: {e}")
        return False
    
    original_count = len(df)
    changes = []
    
    # Step 1: Remove exact duplicates (same ID)
    print("STEP 1: Removing duplicate IDs")
    print("-"*60)
    duplicate_ids = df[df['id'].duplicated()]
    if len(duplicate_ids) > 0:
        print(f"Removing {len(duplicate_ids)} duplicate IDs:")
        for idx, row in duplicate_ids.iterrows():
            print(f"  - ID {row['id']}: {row['name']}")
        df = df.drop_duplicates(subset=['id'], keep='first')
        changes.append(f"Removed {len(duplicate_ids)} duplicate IDs")
    else:
        print("✓ No duplicate IDs found")
    print()
    
    # Step 2: Clean framework names (remove appended numbers)
    print("STEP 2: Cleaning framework names")
    print("-"*60)
    cleaned_names = 0
    for idx, row in df.iterrows():
        name = str(row['name'])
        # Remove numbers at the end (e.g., "Framework 4" -> "Framework")
        import re
        cleaned = re.sub(r'\s+\d+$', '', name)
        if cleaned != name:
            print(f"  {name} → {cleaned}")
            df.at[idx, 'name'] = cleaned
            cleaned_names += 1
    
    if cleaned_names > 0:
        changes.append(f"Cleaned {cleaned_names} framework names")
        print(f"\n✓ Cleaned {cleaned_names} names")
    else:
        print("✓ No names needed cleaning")
    print()
    
    # Step 3: Consolidate frameworks with identical names AND use cases
    print("STEP 3: Consolidating duplicate frameworks")
    print("-"*60)
    
    # Group by name and use_case
    duplicates = df[df.duplicated(subset=['name', 'use_case'], keep=False)]
    
    if len(duplicates) > 0:
        print(f"Found {len(duplicates)} potential duplicates")
        
        # Keep first occurrence of each name+use_case combo
        before = len(df)
        df = df.drop_duplicates(subset=['name', 'use_case'], keep='first')
        after = len(df)
        removed = before - after
        
        if removed > 0:
            print(f"✓ Consolidated {removed} duplicate frameworks")
            changes.append(f"Consolidated {removed} duplicates")
    else:
        print("✓ No duplicates to consolidate")
    print()
    
    # Step 4: Check for similar names (potential typos or variants)
    print("STEP 4: Checking for similar framework names")
    print("-"*60)
    
    from difflib import SequenceMatcher
    
    similar_pairs = []
    names = df['name'].unique()
    
    for i, name1 in enumerate(names):
        for name2 in names[i+1:]:
            similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
            if similarity > 0.85 and similarity < 1.0:  # Very similar but not identical
                similar_pairs.append((name1, name2, similarity))
    
    if similar_pairs:
        print(f"⚠️  Found {len(similar_pairs)} pairs of similar names:")
        for name1, name2, sim in similar_pairs[:5]:
            print(f"  {sim:.0%} similar: '{name1}' vs '{name2}'")
        if len(similar_pairs) > 5:
            print(f"  ... and {len(similar_pairs) - 5} more pairs")
        print("\n  ℹ️  These may need manual review")
    else:
        print("✓ No similar names found")
    print()
    
    # Step 5: Validate cleaned data
    print("STEP 5: Validating cleaned data")
    print("-"*60)
    
    # Check for required fields
    required_fields = ['id', 'name', 'type', 'business_domains', 'use_case']
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        print(f"❌ Missing required fields: {', '.join(missing_fields)}")
        return False
    
    # Check for empty critical fields
    for field in ['id', 'name']:
        null_count = df[field].isna().sum()
        if null_count > 0:
            print(f"❌ Found {null_count} rows with empty '{field}'")
            return False
    
    print("✓ All required fields present")
    print("✓ No empty critical fields")
    print()
    
    # Summary
    print("="*60)
    print("CLEANING SUMMARY")
    print("="*60)
    print(f"Original frameworks: {original_count}")
    print(f"Cleaned frameworks:  {len(df)}")
    print(f"Removed:             {original_count - len(df)}")
    print()
    
    if changes:
        print("Changes made:")
        for change in changes:
            print(f"  ✓ {change}")
    else:
        print("No changes needed - data was already clean!")
    print()
    
    # Save cleaned data
    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✅ Saved cleaned data to: {output_file}")
        print()
        print("NEXT STEPS:")
        print("1. Review the cleaned file")
        print("2. Backup your original file")
        print("3. Replace original with cleaned file:")
        print(f"   mv {output_file} {input_file}")
        print("4. Restart your application")
        return True
    except Exception as e:
        print(f"❌ ERROR saving file: {e}")
        return False


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data/frameworks.xlsx'
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    clean_framework_data(input_file, output_file)
