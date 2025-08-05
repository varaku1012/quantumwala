# Planning Command

Unified planning and parallel execution coordinator for all workflow phases.

## Usage
```
/planning [phase] [spec-name]
```

## Implementation

Execute the planning script:
```bash
python .claude/scripts/planning_executor.py [phase] [spec-name]
```

For JSON output (programmatic use):
```bash
python .claude/scripts/planning_executor.py [phase] [spec-name] --output json
```

## Phases

### 1. Analysis Planning
```
/planning analysis "feature-name"
```
Identifies parallel analysis opportunities:
- Business requirements (business-analyst)
- Technical feasibility (architect)
- UI/UX design (uiux-designer)
- Security review (security-engineer)

### 2. Design Planning
```
/planning design "feature-name"
```
Coordinates parallel design work:
- Frontend components (uiux-designer)
- Backend architecture (architect)
- Data models (data-engineer)
- Infrastructure needs (devops-engineer)

### 3. Implementation Planning
```
/planning implementation "feature-name"
```
Analyzes tasks.md and creates execution batches:
- Groups independent tasks
- Identifies dependencies
- Creates parallel execution plan
- Generates batch commands

### 4. Testing Planning
```
/planning testing "feature-name"
```
Orchestrates parallel testing:
- Unit tests (qa-engineer)
- Integration tests (qa-engineer)
- Security scans (security-engineer)
- Performance tests (architect)

## Planning Process

1. **Load Context**
   ```python
   # Load spec files
   requirements = load_file(".claude/specs/{spec}/requirements.md")
   design = load_file(".claude/specs/{spec}/design.md")
   tasks = load_file(".claude/specs/{spec}/tasks.md")
   ```

2. **Analyze Dependencies**
   ```python
   # Identify what can run in parallel
   task_groups = analyze_dependencies(tasks)
   parallel_opportunities = identify_parallel_work(task_groups)
   ```

3. **Generate Execution Plan**
   ```yaml
   execution_plan:
     batch_1:  # No dependencies
       - task: "1.1 Create user model"
         agent: developer
         command: /{spec}-task-1-1
       - task: "1.2 Create role model"
         agent: developer
         command: /{spec}-task-1-2
     
     batch_2:  # Depends on batch_1
       - task: "2.1 Create auth service"
         agent: developer
         dependencies: [1.1]
       - task: "2.2 Create permission service"
         agent: developer
         dependencies: [1.2]
   ```

4. **Output Commands**
   ```
   ## Parallel Execution Plan
   
   ### Batch 1 (Can run simultaneously):
   - `/{spec}-task-1-1` - Create user model
   - `/{spec}-task-1-2` - Create role model
   
   ### Batch 2 (After Batch 1):
   - `/{spec}-task-2-1` - Create auth service
   - `/{spec}-task-2-2` - Create permission service
   ```

## Integration Points

### Updates Chief Product Manager V2
Replace incorrect reference:
```diff
- 1. Use the parallel-executor agent to identify task batches
+ 1. Use `/planning implementation` to identify task batches
```

### Works With All Agents
- **product-manager**: Uses planning for roadmap phases
- **business-analyst**: Uses planning for parallel analysis
- **architect**: Uses planning for system components
- **qa-engineer**: Uses planning for test suites

## Benefits

1. **Unified Approach**: Single command for all planning needs
2. **Phase-Specific**: Tailored planning for each workflow phase
3. **Dependency Aware**: Respects task dependencies
4. **Maximizes Parallelism**: Identifies all parallel opportunities
5. **Clear Output**: Actionable command lists

## Example Usage

```
User: /planning implementation user-auth