# Quick Test Guide - Dev Workflow Integration

## ✅ Integration Complete!

The chief-product-manager is now integrated with the planning tools. Here's how to test it:

## Test Command

```bash
/dev-workflow "build a simple calculator app"
```

## What Should Happen

The chief-product-manager will now:

1. **Create Spec**
   - Output: `/spec-create simple-calculator-app "..."`

2. **Run Planning Analysis**
   - Output: `/planning analysis simple-calculator-app`
   - Shows which agents to use

3. **Execute Identified Agents**
   - business-analyst for requirements
   - architect for technical design
   - uiux-designer for UI (if needed)

4. **Generate Requirements**
   - Output: `/spec-requirements`

5. **Run Planning Design**
   - Output: `/planning design simple-calculator-app`
   - Shows parallel design opportunities

6. **Create Design**
   - Output: `/spec-design`

7. **Generate Tasks**
   - Output: `/spec-tasks`

8. **Run Planning Implementation**
   - Output: `/planning implementation simple-calculator-app`
   - Shows task batches for parallel execution

9. **Execute Task Batches**
   - Batch 1: Tasks that can run in parallel
   - Batch 2: Tasks with dependencies
   - etc.

10. **Run Planning Testing**
    - Output: `/planning testing simple-calculator-app`
    - Shows parallel testing opportunities

11. **Final Review**
    - Output: `/spec-review 1`

## Verification Points

Look for these indicators that planning integration is working:

✅ **Good Signs**:
- See `/planning` commands being executed
- See "Based on planning output" messages
- See "Batch 1 (Parallel)" execution groups
- See specific agent assignments from planning

❌ **Bad Signs** (old behavior):
- No `/planning` commands
- Generic agent selection
- Sequential task execution only
- No batch grouping

## If It Doesn't Work

1. **Check the agent was updated**:
   ```bash
   cat .claude/agents/chief-product-manager.md | head -20
   ```
   Should show version 5.0.0

2. **Test planning directly**:
   ```bash
   /planning implementation test-spec
   ```
   Should return task batches

3. **Check Python scripts exist**:
   ```bash
   ls -la .claude/scripts/planning_executor.py
   ls -la .claude/scripts/unified_dev_workflow.py
   ```

## Success Metrics

When working correctly, you should see:
- **50% faster execution** (parallel batches)
- **Data-driven agent selection** (from planning)
- **Automatic progression** (no stops between phases)
- **Complete workflow** (all phases executed)

## Next Feature to Build

Once verified, try a real feature:
```bash
/dev-workflow "build user authentication with email verification"
```

This will fully exercise the planning integration with multiple agents and parallel tasks.