# Bug Fix Guide - Duplicate Frameworks & Data Quality

## 🐛 Problems Identified

### Bug #1: Duplicate Frameworks in Results
**Symptom:** Same framework appearing multiple times
- "Layer 3: IT Strategy Framework 4"
- "Layer 3: IT Strategy Framework 8"
- "Layer 3: IT Strategy Framework 5"

**Cause:** No deduplication in discovery handler

### Bug #2: Poor Framework Names
**Symptom:** Framework names have numbers appended
- "Layer 3: IT Strategy Framework 4" (should be "Layer 3: IT Strategy Framework")
- "Technology-Enabled Delivery Framework 4" (should be "Technology-Enabled Delivery Framework")

**Cause:** Data quality issue in Excel file

---

## 🚀 Quick Fix (5 minutes)

### Option A: Fix Both Issues (Recommended)

```bash
cd framework-assistant

# Step 1: Diagnose the data issue
python diagnose_data.py

# Step 2: Clean the data
python clean_data.py
# This creates: data/frameworks_cleaned.xlsx

# Step 3: Backup original
mv data/frameworks.xlsx data/frameworks_backup.xlsx

# Step 4: Use cleaned data
mv data/frameworks_cleaned.xlsx data/frameworks.xlsx

# Step 5: Apply code fix for deduplication
cp discovery_FIXED.py handlers/discovery.py

# Step 6: Clear cache (forces re-embedding)
rm cache/embeddings_cache.pkl

# Step 7: Test
streamlit run app.py
```

### Option B: Just Fix Deduplication (Quick, Partial Fix)

```bash
cd framework-assistant

# Apply discovery handler fix
cp discovery_FIXED.py handlers/discovery.py

# Test
streamlit run app.py
```

**Note:** Option B fixes duplicates but names still look weird.

---

## 🔍 What Each Script Does

### diagnose_data.py
**Purpose:** Identify exact data quality issues  
**Output:** Report showing:
- Duplicate IDs
- Names with appended numbers
- Generic structural names
- Identical use cases

**Run:** `python diagnose_data.py`

### clean_data.py
**Purpose:** Automatically fix data issues  
**Actions:**
1. Removes duplicate IDs (keeps first)
2. Cleans names (removes "Framework 4" → "Framework")
3. Consolidates identical frameworks
4. Validates cleaned data

**Run:** `python clean_data.py`  
**Output:** `data/frameworks_cleaned.xlsx`

---

## 📊 Expected Results

### Before Cleaning
```
Query: "technology stacks for law firm"

Results:
1. Layer 3: IT Strategy Framework 4
2. Layer 3: IT Strategy Framework 8  
3. Technology-Enabled Delivery Framework 4
4. Layer 3: IT Strategy Framework 5
5. Challenger Sale

(5 results, 3 duplicates, weird names)
```

### After Cleaning + Deduplication
```
Query: "technology stacks for law firm"

Results:
1. Layer 3: IT Strategy Framework
2. Technology-Enabled Delivery Framework
3. Challenger Sale

(3 unique results, clean names)
```

---

## 🎯 Testing Checklist

After applying fixes:

- [ ] Run `python diagnose_data.py` - No critical issues
- [ ] Frameworks have clean names (no numbers)
- [ ] Same query returns unique frameworks only
- [ ] Framework descriptions are distinct
- [ ] All 3 fixes applied:
  - [ ] Data cleaned
  - [ ] Discovery handler updated
  - [ ] Cache cleared

---

## 🔧 Manual Data Cleaning (If Scripts Fail)

If automated cleaning doesn't work:

1. **Open Excel file:** `data/frameworks.xlsx`

2. **Find duplicate frameworks:**
   - Sort by "name" column
   - Look for identical or very similar names
   - Check if "use_case" is also identical

3. **Remove duplicates:**
   - Keep only one row per unique framework
   - Delete duplicate rows

4. **Clean names:**
   - Find names ending in numbers: "Framework 4"
   - Remove the numbers: "Framework"
   - Ensure each framework has unique, descriptive name

5. **Save and test:**
   - Save Excel file
   - Delete `cache/embeddings_cache.pkl`
   - Restart app

---

## ⚠️ Common Issues

### Issue: "Layer 3: IT Strategy" appears 3 times after cleaning

**Diagnosis:**
- These might be actually different frameworks
- Check if use_case or other fields are different
- Numbers might be important (Layer 3 vs Layer 2)

**Fix:**
- If truly different: Add more descriptive names
  - "Layer 3: IT Strategy - Infrastructure"
  - "Layer 3: IT Strategy - Security"
  - "Layer 3: IT Strategy - Integration"
- If truly duplicates: Delete all but one

### Issue: Clean script removes too many frameworks

**Diagnosis:**
- Script is too aggressive with consolidation

**Fix:**
- Use manual cleaning instead
- Or modify script's similarity threshold

### Issue: Names still look generic after cleaning

**Diagnosis:**
- Your Excel file might have structural labels in "name" field
- Actual framework names might be elsewhere

**Fix:**
- Open Excel and check:
  - Is there another column with better names?
  - Is "name" field populated correctly?
- May need to restructure your data

---

## 📋 Data Quality Checklist

For long-term health:

- [ ] Each framework has unique ID
- [ ] Each framework has descriptive name
- [ ] Names don't have structural artifacts (numbers, "Layer X: ")
- [ ] Use cases are distinct and specific
- [ ] No duplicate rows
- [ ] All required fields populated

---

## 🎓 Understanding the Bug

### Why Duplicates Happen

**In Search Results:**
1. Framework has ID 4, 5, and 8 (different rows)
2. All three match search query
3. Search returns all three
4. Discovery handler doesn't deduplicate by ID
5. Same framework shown 3 times

**Fix:** Deduplication in discovery handler

### Why Names Are Weird

**In Excel File:**
1. Framework name entered as "Layer 3: IT Strategy Framework"
2. Someone added "4", "5", "8" to distinguish rows
3. These became part of the framework name
4. Propagated through entire system

**Fix:** Clean data, remove appended numbers

---

## 💡 Prevention Tips

To avoid this in future:

1. **Use unique IDs** - Don't duplicate framework rows
2. **Descriptive names** - Make each name unique and meaningful
3. **Run validation** - Use `diagnose_data.py` after data changes
4. **Version control** - Keep Excel file in git, track changes
5. **Regular audits** - Monthly check with validation script

---

## 🚨 If You're Stuck

**Still seeing duplicates after both fixes?**

1. Share your diagnose_data.py output
2. Check if frameworks have truly different IDs
3. Verify discovery_FIXED.py was applied
4. Clear cache completely: `rm -rf cache/`

**Names still wrong after cleaning?**

1. Check Excel file directly
2. Look for other columns with better names
3. May need custom cleaning logic for your data

---

## 📞 Next Steps

### Immediate (Fix the Bug)
1. Run diagnosis: `python diagnose_data.py`
2. Clean data: `python clean_data.py`
3. Apply code fix: `cp discovery_FIXED.py handlers/discovery.py`
4. Clear cache: `rm cache/embeddings_cache.pkl`
5. Test: `streamlit run app.py`

### After Bug Fixed (Add New Feature)
1. Proceed with Framework Library feature
2. Follow LIBRARY_FEATURE_GUIDE.md
3. Enjoy browsing 857 clean, unique frameworks

---

**Ready to fix? Start with Option A above! 🚀**
