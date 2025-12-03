# Authorization Testing Framework for File-Sharing Systems

**Automated Experiment for Evaluating Authorization Enforcement Consistency**

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [System Architecture](#system-architecture)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [Understanding the Results](#understanding-the-results)
- [Project Structure](#project-structure)
- [Key Concepts](#key-concepts)
- [Results Summary](#results-summary)
- [Future Enhancements](#future-enhancements)
- [References](#references)

---

## 🎯 Project Overview

This project demonstrates a **systematic approach to testing authorization logic** in file-sharing systems. We design and develop an automated experiment that:

1. **Defines a formal policy model** - Establishes the "ground truth" for what SHOULD happen
2. **Implements a mock file-sharing API** - Creates a realistic system with authorization logic
3. **Generates comprehensive test scenarios** - Creates all possible combinations of access control factors
4. **Executes automated testing** - Programmatically tests every scenario
5. **Identifies inconsistencies** - Compares expected vs actual behavior to find bugs
6. **Visualizes results** - Creates professional charts and heat maps

**Goal:** Demonstrate the importance of systematic testing for authorization logic correctness and visualize inconsistencies across complex access control combinations.

---

## 🚨 Problem Statement

### Why This Matters

Authorization bugs are among the most critical security vulnerabilities in modern applications:

- **Dropbox (2014):** Files accessible without proper permissions
- **Google Drive:** Sharing link vulnerabilities exposed private documents
- **Microsoft OneDrive:** Permission inheritance bugs allowed unauthorized access

### The Challenge

Manual testing of authorization logic is:
- ❌ **Error-prone** - Easy to miss edge cases
- ❌ **Incomplete** - Impossible to test all combinations manually
- ❌ **Time-consuming** - 64+ scenarios to verify
- ❌ **Not repeatable** - Hard to regression test after changes

### Our Solution

An **automated testing framework** that:
- ✅ Tests ALL possible scenarios systematically
- ✅ Finds bugs that manual testing would miss
- ✅ Provides clear visualization of problems
- ✅ Enables continuous verification

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│  1. Policy Model (Ground Truth)                         │
│     └─ Defines expected authorization behavior          │
├─────────────────────────────────────────────────────────┤
│  2. File-Sharing API (System Under Test)                │
│     └─ Mock backend with authorization logic            │
├─────────────────────────────────────────────────────────┤
│  3. Test Framework (Automated Executor)                 │
│     ├─ Generate test scenarios                          │
│     ├─ Execute API calls                                │
│     ├─ Compare expected vs actual                       │
│     └─ Report mismatches                                │
├─────────────────────────────────────────────────────────┤
│  4. Visualization Engine                                │
│     ├─ Heat maps showing patterns                       │
│     ├─ Bar charts comparing results                     │
│     └─ Summary reports                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 💻 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd authorization-testing

# Or download and extract the ZIP file
```

### Step 2: Install Required Libraries

```bash
pip install matplotlib seaborn pandas numpy
```

### Step 3: Verify Installation

```bash
python --version  # Should show Python 3.8+
pip list          # Should show matplotlib, seaborn, pandas, numpy
```

---

## 🚀 How to Run

### Quick Start (Run Everything)

```bash
# Run all components in sequence
python policy_model.py      # Generate policy and scenarios
python test_framework.py    # Run automated tests
python visualizations.py    # Create charts
```

### Detailed Instructions

#### **Step 1: Generate Policy Model**

```bash
python policy_model.py
```

**What it does:**
- Defines 7 authorization rules
- Generates all 64 test scenarios
- Exports to `policy_scenarios.csv`
- Shows statistics about expected behavior

**Expected Output:**
```
============================================================
AUTHORIZATION POLICY STATISTICS
============================================================
Total test scenarios: 64
Expected ALLOW: 24 (37.5%)
Expected DENY: 40 (62.5%)
============================================================

✅ Exported 64 scenarios to policy_scenarios.csv
```

---

#### **Step 2: Run Automated Tests**

```bash
python test_framework.py
```

**What it does:**
- Sets up test users and files
- Tests all 64 scenarios against the API
- Compares actual vs expected results
- Identifies authorization bugs
- Exports results to `test_results.json`

**Expected Output:**
```
============================================================
SETTING UP TEST FIXTURES
============================================================
1️⃣ Creating test users...
   ✅ Created 4 test users

2️⃣ Creating test files...
   ✅ Created 4 test files

3️⃣ Setting up collaboration permissions...
   ✅ Granted collaboration permissions

============================================================
RUNNING AUTOMATED TESTS
============================================================
📊 Total scenarios to test: 64
⏳ Running tests...

   Progress: 64/64 tests completed (50 passed)

============================================================
TEST EXECUTION SUMMARY
============================================================
Total Scenarios: 64
✅ PASSED: 50 (78.1%)
❌ FAILED: 14 (21.9%)
============================================================

🚨 FAILURE ANALYSIS
------------------------------------------------------------
⚠️  OVER-PERMISSIVE (HIGH SEVERITY): 14 cases
   API allows actions that should be DENIED
   
   🐛 Scenario 20: collaborator can share private file
   🐛 Scenario 49: external can read private file
   ... (more bugs listed)

📄 Detailed results exported to test_results.json
```

---

#### **Step 3: Generate Visualizations**

```bash
python visualizations.py
```

**What it does:**
- Reads test results from JSON
- Creates 6 professional charts
- Saves them to `visualizations/` folder

**Expected Output:**
```
============================================================
GENERATING VISUALIZATIONS
============================================================

✅ Created: visualizations/overall_summary.png
✅ Created: visualizations/heatmap_by_audience.png
✅ Created: visualizations/failures_by_audience.png
✅ Created: visualizations/failures_by_action.png
✅ Created: visualizations/pass_rate_by_audience.png
✅ Created: visualizations/severity_matrix.png

============================================================
✅ ALL VISUALIZATIONS CREATED
============================================================

📁 Check the 'visualizations/' folder for all charts!
```

---

## 📊 Understanding the Results

### Files Generated

After running all scripts, you'll have:

```
authorization-testing/
├── policy_model.py
├── file_sharing_api.py
├── test_framework.py
├── visualizations.py
├── README.md
├── policy_scenarios.csv          # All test scenarios with expected results
├── test_results.json              # Detailed test results
└── visualizations/                # Charts and graphs
    ├── overall_summary.png        # Pass/Fail bar chart
    ├── heatmap_by_audience.png    # Authorization matrices (4 heat maps)
    ├── failures_by_audience.png   # Bugs by user type
    ├── failures_by_action.png     # Bugs by action type
    ├── pass_rate_by_audience.png  # Stacked comparison
    └── severity_matrix.png        # Bug severity heat map
```

### Interpreting the Charts

#### 1. **Overall Summary** (`overall_summary.png`)
- Simple bar chart showing total passed vs failed tests
- Shows pass rate percentage
- Quick overview of system health

#### 2. **Heat Maps by Audience** (`heatmap_by_audience.png`)
- 4 heat maps (one for each audience type: owner, collaborator, org_member, external)
- Rows = Actions (read, edit, delete, share)
- Columns = Visibility levels (private, shared, org_public, public)
- Colors:
  - 🟢 Green = ALLOW (correct)
  - 🔴 Red = DENY (correct)
  - 🟠 Orange = BUG! (mismatch between expected and actual)

#### 3. **Failures by Audience** (`failures_by_audience.png`)
- Shows which user types have the most authorization bugs
- Higher bars = more security issues for that user type
- External users typically have most severe bugs

#### 4. **Failures by Action** (`failures_by_action.png`)
- Shows which actions (read, edit, delete, share) have most bugs
- Helps prioritize which operations need fixing

#### 5. **Pass Rate by Audience** (`pass_rate_by_audience.png`)
- Stacked bar chart showing passed (green) vs failed (red) for each audience
- Shows percentage breakdown
- Helps identify which user types are most problematic

#### 6. **Severity Matrix** (`severity_matrix.png`)
- Heat map showing bug count by audience × visibility
- Darker red = more bugs = higher severity
- Private file bugs by external users = CRITICAL

---

## 📁 Project Structure

### Core Files

#### **1. `policy_model.py`**

**Purpose:** Defines the formal authorization policy (ground truth)

**Key Components:**
- `AuthorizationPolicy` class - Contains the policy rules
- `evaluate()` method - Determines if an action should be ALLOWED or DENIED
- `generate_all_scenarios()` - Creates all 64 test combinations
- Policy rules implementation (7 rules)

**Usage:**
```python
from policy_model import AuthorizationPolicy

policy = AuthorizationPolicy()
result = policy.evaluate(
    audience='external',
    visibility='private',
    action='read',
    is_owner=False,
    has_collaboration_permission=False,
    same_org=False
)
# Returns: 'DENY'
```

---

#### **2. `file_sharing_api.py`**

**Purpose:** Mock file-sharing API with authorization enforcement

**Key Components:**
- `User` class - Represents system users
- `File` class - Represents files with visibility levels
- `Permission` class - Represents explicit sharing permissions
- `FileShareAPI` class - Main API with REST-like methods
- `_check_authorization()` - Core authorization logic (contains intentional bugs)

**API Methods:**
```python
from file_sharing_api import FileShareAPI

api = FileShareAPI()

# User management
api.create_user(email, organization_id, name)
api.get_user(user_id)

# File operations
api.create_file(owner_id, name, visibility, content)
api.get_file(file_id, user_id)           # Requires auth
api.update_file(file_id, user_id, content)  # Requires auth
api.delete_file(file_id, user_id)       # Requires auth

# Sharing
api.share_file(file_id, user_id, target_user_id, permission_type)
api.get_file_permissions(file_id, user_id)
```

**Intentional Bugs:**
1. 🐛 Public files allow editing (should be read-only)
2. 🐛 Org members can delete org_public files (should only read)
3. 🐛 Collaborators can share files (should only read/edit)

---

#### **3. `test_framework.py`**

**Purpose:** Automated testing framework that finds authorization bugs

**Key Components:**
- `TestResult` class - Stores individual test results
- `AuthorizationTestFramework` class - Main testing engine
- `setup_test_fixtures()` - Creates test environment
- `test_scenario()` - Tests a single scenario
- `run_all_tests()` - Executes all 64 tests
- `analyze_results()` - Generates statistics

**Usage:**
```python
from test_framework import AuthorizationTestFramework

framework = AuthorizationTestFramework()
framework.setup_test_fixtures()
results = framework.run_all_tests()
framework.print_summary()
framework.export_results('test_results.json')
```

---

#### **4. `visualizations.py`**

**Purpose:** Creates professional charts and graphs from test results

**Key Components:**
- `TestResultVisualizer` class - Main visualization engine
- Methods for creating different chart types
- `generate_all_visualizations()` - Creates all 6 charts at once

**Usage:**
```python
from visualizations import TestResultVisualizer

visualizer = TestResultVisualizer('test_results.json')
visualizer.generate_all_visualizations()
```

---

## 🔑 Key Concepts

### Authorization Factors

Our system models 4 key factors that affect access control decisions:

#### 1. **Audience (Who?)**
- `owner` - The file creator (full access)
- `collaborator` - User with explicit permissions
- `org_member` - User in same organization
- `external` - User from different organization

#### 2. **Visibility (Scope?)**
- `private` - Only owner + explicit collaborators
- `shared` - Only users explicitly shared with
- `org_public` - All organization members
- `public` - Everyone on the internet

#### 3. **Action (What?)**
- `read` - View file content
- `edit` - Modify file content
- `delete` - Remove file permanently
- `share` - Grant access to other users

#### 4. **Context Flags**
- `is_owner` - Boolean: Is the user the file owner?
- `has_collaboration_permission` - Boolean: Explicit sharing?
- `same_org` - Boolean: Same organization as owner?

### Authorization Rules

Our policy implements 7 rules (evaluated in priority order):

```
PRIORITY 1 (HIGHEST): Owner Override
├─ IF user is owner → ALLOW all actions

PRIORITY 2: Public Access
├─ IF visibility = public AND action = read → ALLOW
├─ IF visibility = public AND action ≠ read → DENY

PRIORITY 3: Organization Access  
├─ IF visibility = org_public AND same_org AND action = read → ALLOW
├─ ELSE → DENY

PRIORITY 4: Collaboration Permissions
├─ IF has_collaboration AND action ∈ {read, edit} → ALLOW
├─ IF has_collaboration AND action ∈ {delete, share} → DENY

PRIORITY 5: Shared File Protection
├─ IF visibility = shared AND no collaboration → DENY

PRIORITY 6: Private File Protection
├─ IF visibility = private AND no permission → DENY

PRIORITY 7 (DEFAULT): Deny All
└─ IF no rule matches → DENY
```

### Test Scenario Generation

We generate test scenarios by combining all factor values:

```
4 audiences × 4 visibilities × 4 actions = 64 total scenarios
```

**Example Scenarios:**

| Scenario | Audience | Visibility | Action | Expected |
|----------|----------|------------|--------|----------|
| 1 | owner | private | read | ALLOW |
| 17 | collaborator | private | read | ALLOW |
| 19 | collaborator | private | delete | DENY |
| 49 | external | private | read | DENY |
| 61 | external | public | read | ALLOW |
| 62 | external | public | edit | DENY |

---

## 📈 Results Summary

### Overall Statistics

- **Total Test Scenarios:** 64
- **Passed:** 50 (78.1%)
- **Failed:** 14 (21.9%)
- **All Failures:** Over-permissive (HIGH SEVERITY)

### Bug Distribution

**By Audience:**
- Collaborator: 5 bugs
- Org Member: 2 bugs
- External: 7 bugs (MOST CRITICAL)

**By Action:**
- Read: 3 bugs
- Edit: 5 bugs
- Delete: 2 bugs
- Share: 4 bugs

### Critical Bugs Found

#### 🚨 **Severity: CRITICAL**

**External users can access private files:**
- Scenario 49: External can READ private files
- Scenario 50: External can EDIT private files
- Scenario 52: External can SHARE private files

**Impact:** Complete breach of private file confidentiality

---

#### ⚠️ **Severity: HIGH**

**External users can access shared files:**
- Scenario 53: External can READ shared files
- Scenario 54: External can EDIT shared files
- Scenario 56: External can SHARE shared files

**Impact:** Unauthorized access to sensitive shared documents

---

#### ⚠️ **Severity: MEDIUM**

**Collaborators can share files:**
- Scenario 20: Collaborator can SHARE private files
- Scenario 24: Collaborator can SHARE shared files

**Impact:** Privilege escalation - collaborators become de facto owners

---

**Anyone can edit public files:**
- Scenario 30: Collaborator can EDIT public files
- Scenario 46: Org member can EDIT public files
- Scenario 62: External can EDIT public files

**Impact:** Content integrity - public files should be read-only

---

**Org members can delete org_public files:**
- Scenario 27: Collaborator can DELETE org_public files
- Scenario 43: Org member can DELETE org_public files

**Impact:** Data loss - only owners should delete

---

### Security Impact

These bugs represent **serious security vulnerabilities** that could lead to:
- 🔓 Unauthorized data access (confidentiality breach)
- 📝 Unauthorized modifications (integrity violation)
- 🗑️ Unauthorized deletions (availability threat)
- 🔑 Privilege escalation (authorization bypass)

---

## 🚀 Future Enhancements

### Phase 6: Bug Fixes & Validation

1. **Fix the authorization logic** in `file_sharing_api.py`
2. **Re-run tests** to verify all 64 scenarios pass
3. **Document the fixes** and lessons learned

### Additional Features

**Extend the test framework:**
- ✨ Test permission inheritance (nested folders)
- ✨ Test time-based access (expiring shares)
- ✨ Test concurrent modifications
- ✨ Test permission revocation
- ✨ Test role-based access (admin, viewer, editor)

**Add more test scenarios:**
- Group permissions (teams, departments)
- Link-based sharing (public URLs)
- Guest access (unauthenticated users)
- API key authentication
- Multi-factor authorization

**Improve visualizations:**
- Interactive dashboards (using Plotly Dash)
- Real-time test execution monitoring
- Historical trend analysis
- Exportable PDF reports

**Integration with CI/CD:**
- Automated testing on every code commit
- Pre-deployment authorization verification
- Regression test suite
- Performance benchmarks

---

## 🎓 Learning Outcomes

This project demonstrates:

1. ✅ **Systematic Testing Methodology** - How to test complex systems comprehensively
2. ✅ **Formal Policy Modeling** - Defining expected behavior precisely
3. ✅ **Test Automation** - Building frameworks that scale
4. ✅ **Security Testing** - Finding authorization vulnerabilities
5. ✅ **Data Visualization** - Presenting technical findings clearly
6. ✅ **Software Engineering** - Modular design, clean code, documentation

---

## 📚 References

### Academic Papers
- "A Survey of Access Control Models" - Hu et al.
- "Automated Testing of Access Control Policies" - Martin & Xie
- "RBAC: Role-Based Access Control" - Sandhu et al.

### Industry Standards
- OWASP Top 10 - Broken Access Control
- NIST RBAC Standard
- OAuth 2.0 Authorization Framework

### Real-World Incidents
- Dropbox Data Exposure (2014)
- Google Drive Sharing Vulnerabilities
- Microsoft OneDrive Permission Bugs

---



## 🤝 Contributing

This is a class project, but suggestions are welcome! To contribute:

1. Review the code structure
2. Identify potential improvements
3. Test your changes
4. Submit suggestions with clear documentation

---

## ❓ Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'matplotlib'`
**Solution:** 
```bash
pip install matplotlib seaborn pandas numpy
```

---

**Issue:** No visualizations folder created
**Solution:** 
```bash
# Create folder manually
mkdir visualizations

# Run visualization script
python visualizations.py
```

---

**Issue:** JSON file not found
**Solution:** 
```bash
# Make sure to run test framework first
python test_framework.py

# Then run visualizations
python visualizations.py
```

---

**Issue:** Charts look distorted
**Solution:**
- Ensure you have matplotlib version 3.0+
- Update libraries: `pip install --upgrade matplotlib seaborn`

---

## 📞 Support

For questions or issues:
- Review this README thoroughly
- Check the code comments in each Python file
- Review the generated JSON for detailed test data
- Examine the visualization charts

---

## 🎉 Acknowledgments

Special thanks to:
- The Anthropic Claude team for AI assistance
- Open-source libraries: matplotlib, seaborn, pandas
- Security research community for real-world examples

---

**End of Documentation**

*Last Updated: December 2024*
*Version: 1.0*

---

## Quick Reference Card

### Run Everything
```bash
python policy_model.py && python test_framework.py && python visualizations.py
```

### View Results
```bash
# Open these files:
- visualizations/*.png  (charts)
- test_results.json     (detailed data)
- policy_scenarios.csv  (all scenarios)
```

### Clean Up
```bash
# Remove generated files
rm test_results.json policy_scenarios.csv
rm -rf visualizations/
```

---

✨ **You're all set! Good luck with your presentation!** ✨