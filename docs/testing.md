# Integration Testing Guide

This document outlines the integration testing strategy for DST Skills.

## Testing Overview

DST Skills integration testing verifies that all components work together correctly:
- Infrastructure (database, API client, logging)
- Scripts (all Python scripts execute properly)
- Skills (documentation matches implementation)
- Agents (activation, workflow, collaboration)

## Test Categories

### 1. Infrastructure Tests

**Database**:
```bash
# Initialize database
python scripts/db/init_db.py
# Verify dst_metadata table exists

# Test utilities
python scripts/db/db_utils.py
# Should complete without errors
```

**API Client**:
```bash
# Note: Requires internet connection
python scripts/api/client.py
# Should successfully connect to DST API
```

**Environment**:
```bash
# Verify .env loads correctly
cat .env
# Check all required variables present
```

### 2. Script Integration Tests

**Fetcher Scripts** (requires network):
```bash
# Test complete workflow
python scripts/api/get_subjects.py
python scripts/api/get_tables.py --subject 02
python scripts/api/get_tableinfo.py --table-id FOLK1A
python scripts/fetch_and_store.py --table-id FOLK1A
```

**Analyst Scripts**:
```bash
# Test metadata queries
python scripts/db/query_metadata.py --list-all
python scripts/db/query_metadata.py --table-id FOLK1A
python scripts/db/query_metadata.py --table-id FOLK1A --check-freshness

# Test data queries (requires fetched data)
python scripts/db/table_summary.py --table-id FOLK1A
python scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 10"
```

### 3. Agent Integration Tests

**Fetcher Agent**:
- Activate with: "Fetch population data from DST"
- Verify agent browses subjects
- Verify agent finds tables
- Verify agent fetches and stores data
- Verify agent confirms success

**Analyst Agent**:
- Activate with: "Analyze population trends"
- Verify agent checks data availability
- Verify agent checks freshness
- Verify agent constructs SQL
- Verify agent presents results

### 4. Cross-Agent Workflow Tests

**Complete Workflow**:
1. User: "I want population data"
2. Fetcher Agent activates and fetches
3. User: "Now analyze the population trends"
4. Analyst Agent activates and analyzes
5. Both agents complete successfully

**Missing Data Handoff**:
1. User: "Analyze employment data"
2. Analyst checks - data missing
3. Analyst recommends Fetcher Agent
4. User switches to Fetcher
5. Fetcher fetches employment data
6. User switches back to Analyst
7. Analyst completes analysis

## Testing Checklist

### Pre-Test Setup
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Network connectivity available
- [ ] Logs directory exists

### Infrastructure
- [ ] Database file created
- [ ] dst_metadata table exists
- [ ] API client connects to DST
- [ ] Logging works correctly

### Fetcher Scripts
- [ ] get_subjects.py executes
- [ ] get_tables.py executes with filters
- [ ] get_tableinfo.py returns metadata
- [ ] fetch_and_store.py completes
- [ ] Data stored in DuckDB
- [ ] Metadata updated

### Analyst Scripts
- [ ] query_metadata.py lists tables
- [ ] check_freshness works
- [ ] table_summary.py generates stats
- [ ] query_data.py executes SQL
- [ ] Multiple output formats work

### Skills Validation
- [ ] All 7 skill files have valid YAML
- [ ] All skill examples work
- [ ] Skills documentation accurate
- [ ] File paths correct

### Agent Testing
- [ ] Fetcher activates on fetch keywords
- [ ] Analyst activates on analyze keywords
- [ ] Agents use correct skills
- [ ] Agents execute scripts properly
- [ ] Cross-agent handoff works

### Error Handling
- [ ] Invalid table ID handled gracefully
- [ ] Missing data reported clearly
- [ ] API errors caught and explained
- [ ] Database errors handled properly

## Known Limitations

1. **Network Dependency**: Most tests require internet access to DST API
2. **API Rate Limits**: DST may rate-limit requests during testing
3. **Data Variability**: DST data changes, so exact values may differ
4. **Agent Activation**: Requires Claude Code environment

## Test Data

For consistent testing, use these known-good table IDs:
- **FOLK1A**: Population data (reliable, commonly used)
- **AUP01**: Employment data (if available)

## Manual Test Scenarios

### Scenario 1: First-Time User
1. Follow getting-started.md exactly
2. Note any unclear steps
3. Verify all commands work
4. Document issues

### Scenario 2: Complete Analysis Workflow
1. Fetch population data
2. Check data freshness
3. Run basic query
4. Run complex query with joins
5. Export results

### Scenario 3: Error Recovery
1. Request invalid table
2. Verify helpful error message
3. Request valid table
4. Verify recovery works

## Regression Testing

Create automated test script:

```bash
#!/bin/bash
# tests/run_integration_tests.sh

echo "=== DST Skills Integration Tests ==="

# Test 1: Database
echo "Testing database..."
python scripts/db/init_db.py
if [ $? -eq 0 ]; then echo "✓ Database test passed"; else echo "✗ Database test failed"; exit 1; fi

# Test 2: Metadata (requires fetched data)
echo "Testing metadata..."
python scripts/db/query_metadata.py --list-all > /dev/null
if [ $? -eq 0 ]; then echo "✓ Metadata test passed"; else echo "✗ Metadata test failed"; fi

# Test 3: Query (requires fetched data)
echo "Testing queries..."
python scripts/db/query_data.py --sql "SELECT COUNT(*) FROM dst_metadata" > /dev/null
if [ $? -eq 0 ]; then echo "✓ Query test passed"; else echo "✗ Query test failed"; fi

echo "=== Tests Complete ==="
```

Make executable: `chmod +x tests/run_integration_tests.sh`

## Reporting Issues

When reporting test failures, include:
1. **What you were testing**: Specific step or scenario
2. **Expected behavior**: What should have happened
3. **Actual behavior**: What actually happened
4. **Environment**: Python version, OS, network status
5. **Logs**: Relevant entries from `logs/dst_system.log`
6. **Screenshots**: If applicable

## Continuous Testing

For ongoing development:
1. Run integration tests before major changes
2. Test all affected components after changes
3. Update test documentation when features change
4. Maintain test data samples
5. Document new test scenarios

## Next Steps

After testing:
1. Document results
2. Fix critical issues
3. Update documentation if needed
4. Re-test after fixes
5. Mark project as production-ready

## Resources

- **Task File**: `.claude/dev/tasks/task-integration-testing.md` - Complete testing checklist
- **Logs**: `logs/dst_system.log` - Debugging information
- **Test Directory**: `tests/` - Test scripts and results

---

**Note**: Integration testing is most effective with real DST API access. Some tests may be limited in offline environments.
