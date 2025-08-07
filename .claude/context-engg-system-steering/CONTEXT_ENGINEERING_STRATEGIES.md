# Context Engineering Strategies

## Definition
Context engineering is the art and science of managing information flow to LLM agents, ensuring they have exactly the right information at the right time while minimizing token usage.

## Four Core Strategies

### 1. WRITE - Structured Output Generation
**Purpose**: Create well-structured outputs that can be efficiently consumed by subsequent agents.

**Implementation**:
```python
# Structure outputs for easy parsing
output = {
    "summary": "Brief overview",
    "details": "Full information",
    "next_actions": ["action1", "action2"],
    "metadata": {"tokens": 1500, "duration": 2.3}
}
```

**Best Practices**:
- Use consistent schemas across agents
- Include metadata for tracking
- Separate summary from details
- Mark critical vs supplementary info

### 2. SELECT - Relevant Context Retrieval
**Purpose**: Choose only the most relevant information for each agent's task.

**Implementation**:
```python
def select_context(agent_type, task, full_context):
    relevance_map = {
        'developer': ['requirements', 'design', 'current_code'],
        'qa-engineer': ['requirements', 'implementation', 'test_plan'],
        'architect': ['requirements', 'constraints', 'existing_arch']
    }
    
    selected = {}
    for key in relevance_map.get(agent_type, []):
        if key in full_context:
            selected[key] = full_context[key]
    
    return selected
```

**Selection Criteria**:
- Agent-specific requirements
- Task-specific needs
- Temporal relevance (recent > old)
- Dependency relationships

### 3. COMPRESS - Token Optimization
**Purpose**: Reduce context size while preserving information content.

**Compression Techniques**:

#### Progressive Compression
```python
compression_levels = [
    remove_whitespace,      # Level 1: -10% tokens
    summarize_sections,     # Level 2: -30% tokens
    extract_key_points,     # Level 3: -50% tokens
    use_references         # Level 4: -70% tokens
]

def compress_to_limit(context, max_tokens=4000):
    for compression_fn in compression_levels:
        context = compression_fn(context)
        if count_tokens(context) <= max_tokens:
            break
    return context
```

#### Hierarchical Summarization
```python
def hierarchical_summary(text):
    # Full detail → Paragraph summary → Section summary → Document summary
    levels = {
        'document': 50,    # 50 token summary
        'section': 200,    # 200 tokens per section
        'paragraph': 500,  # 500 tokens per paragraph
        'full': None      # Full text if space allows
    }
    
    # Choose appropriate level based on available space
    return select_detail_level(text, available_tokens)
```

### 4. ISOLATE - Context Separation
**Purpose**: Prevent context contamination between agents and tasks.

**Isolation Mechanisms**:

#### Namespace Isolation
```python
class ContextNamespace:
    def __init__(self, agent_id):
        self.namespace = f"agent_{agent_id}_{timestamp()}"
        self.context = {}
    
    def get_isolated_context(self):
        # Deep copy to prevent mutations
        return deepcopy(self.context)
```

#### Scope Boundaries
```python
scope_boundaries = {
    'global': ['project_config', 'steering_docs'],
    'phase': ['phase_requirements', 'phase_outputs'],
    'task': ['task_description', 'task_context'],
    'agent': ['agent_memory', 'agent_state']
}
```

## Context Flow Pipeline

```
Raw Input (20KB)
    ↓ [Validation]
Clean Input (18KB)
    ↓ [Selection]
Relevant Context (10KB)
    ↓ [Compression]
Compressed Context (4KB)
    ↓ [Isolation]
Agent Context (4KB isolated)
    ↓ [Enrichment]
Final Context (5KB with memories)
```

## Memory Integration

### Three-Tier Memory Architecture

#### Short-Term Memory (In-Context)
- Last 30 minutes of execution
- Current workflow state
- Recent agent interactions
- Size: ~1000 tokens

#### Long-Term Memory (Database)
- All past executions
- Indexed by task type
- Searchable by similarity
- Size: Unlimited

#### Episodic Memory (Few-Shot)
- Successful execution examples
- Ranked by relevance
- Task-specific patterns
- Size: 3-5 examples, ~500 tokens each

### Memory Selection Algorithm
```python
def get_relevant_memories(task):
    memories = {
        'short_term': get_recent_context(minutes=30),
        'long_term': search_similar_tasks(task, limit=5),
        'episodic': get_best_examples(task.type, limit=3)
    }
    
    # Compress if needed
    if total_tokens(memories) > MEMORY_BUDGET:
        memories = prioritize_memories(memories, MEMORY_BUDGET)
    
    return memories
```

## Token Budget Management

### Allocation Strategy
```python
TOKEN_BUDGET = 4000  # Claude's optimal context size

allocation = {
    'system_prompt': 500,      # Agent instructions
    'task_description': 300,   # Current task
    'context': 2000,           # Task context
    'memories': 1000,          # Retrieved memories
    'buffer': 200             # Safety margin
}
```

### Dynamic Reallocation
```python
def reallocate_tokens(actual_usage):
    # If one category uses less, redistribute
    unused = TOKEN_BUDGET - sum(actual_usage.values())
    
    # Prioritize context and memories
    if unused > 0:
        actual_usage['context'] += unused * 0.6
        actual_usage['memories'] += unused * 0.4
    
    return actual_usage
```

## Context Quality Metrics

### Relevance Score
```python
def calculate_relevance(context, task):
    keyword_overlap = keyword_similarity(context, task)
    semantic_similarity = embedding_similarity(context, task)
    recency_score = time_decay_factor(context.timestamp)
    
    return (keyword_overlap * 0.3 + 
            semantic_similarity * 0.5 + 
            recency_score * 0.2)
```

### Compression Ratio
```python
compression_ratio = original_tokens / compressed_tokens
# Target: 3-5x compression without information loss
```

### Isolation Integrity
```python
def verify_isolation(context1, context2):
    # Ensure no shared references
    assert id(context1) != id(context2)
    # Check for contamination
    assert no_shared_mutations(context1, context2)
```

## Anti-Patterns to Avoid

### Context Poisoning
- **Problem**: Hallucinations entering context
- **Solution**: Validate all agent outputs before adding to context

### Context Explosion
- **Problem**: Context grows unbounded
- **Solution**: Aggressive compression and selection

### Context Confusion
- **Problem**: Mixing unrelated information
- **Solution**: Clear scope boundaries

### Context Starvation
- **Problem**: Too little context for task
- **Solution**: Minimum context requirements per agent

## Optimization Techniques

### 1. Caching
```python
context_cache = {}

def get_cached_context(cache_key):
    if cache_key in context_cache:
        if not is_stale(context_cache[cache_key]):
            return context_cache[cache_key]
    
    context = prepare_context()
    context_cache[cache_key] = context
    return context
```

### 2. Lazy Loading
```python
class LazyContext:
    def __init__(self, loader_fn):
        self.loader_fn = loader_fn
        self._loaded = False
        self._data = None
    
    def get(self):
        if not self._loaded:
            self._data = self.loader_fn()
            self._loaded = True
        return self._data
```

### 3. Streaming
```python
async def stream_context(agent, chunks):
    for chunk in chunks:
        compressed = compress(chunk)
        if fits_in_window(compressed):
            yield compressed
        else:
            yield summarize(compressed)
```

## Implementation Checklist

- [ ] Implement all four strategies (Write, Select, Compress, Isolate)
- [ ] Set up three-tier memory system
- [ ] Define token budgets per agent
- [ ] Create compression pipeline
- [ ] Add context validation
- [ ] Implement caching layer
- [ ] Monitor context metrics
- [ ] Set up isolation boundaries
- [ ] Test contamination prevention
- [ ] Optimize for performance