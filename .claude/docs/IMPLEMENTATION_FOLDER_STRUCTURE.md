# Implementation Folder Structure Guide

## Current Issue
The workflow is creating implementation files in multiple locations, causing a messy root folder structure.

## ❌ Current (Incorrect) Structure
```
quantumwala/                      # Root getting cluttered!
├── services/                     # ❌ Wrong location
│   └── user-authentication-api/
├── frontend/                     # ❌ Wrong location
│   └── user-authentication-web/
├── ml-services/                  # ❌ Wrong location
│   └── user-authentication-ml/
├── implementations/              # ✅ Correct but incomplete
│   └── user-authentication/
│       └── README.md            # Only README, no actual code
└── infrastructure/
    └── k8s/user-authentication/  # ❌ Should be under implementations
```

## ✅ Correct Structure (Per Steering Docs)
```
quantumwala/
├── implementations/              # ✅ All feature code goes here
│   └── user-authentication/     # Feature-specific folder
│       ├── README.md            # Feature overview
│       ├── services/            # Backend services for THIS feature
│       │   └── user-authentication-api/
│       │       ├── src/
│       │       ├── package.json
│       │       └── Dockerfile
│       ├── frontend/            # Frontend apps for THIS feature
│       │   └── user-authentication-web/
│       │       ├── src/
│       │       └── package.json
│       ├── ml-services/         # ML services for THIS feature
│       │   └── user-authentication-ml/
│       │       ├── app/
│       │       └── requirements.txt
│       ├── infrastructure/      # Infrastructure for THIS feature
│       │   ├── k8s/
│       │   │   └── namespace.yaml
│       │   └── docker/
│       │       └── docker-compose.yml
│       └── docs/               # Feature documentation
│           └── API.md
├── .claude/                    # Claude system (separate)
│   └── specs/
│       ├── backlog/
│       ├── scope/
│       └── completed/
└── [root stays clean]          # ✅ No service folders at root
```

## Why This Structure?

### 1. **Feature Isolation**
- Each feature is completely self-contained
- Easy to find all code related to a feature
- Can delete entire feature by removing one folder

### 2. **Clean Root**
- Root folder doesn't get cluttered with service folders
- Clear separation between features
- Easy to see what features are implemented

### 3. **Better Organization**
- Infrastructure configs stay with the feature
- Documentation stays with the code
- Tests stay with the implementation

### 4. **Deployment Friendly**
- Can deploy features independently
- Easy to create CI/CD pipelines per feature
- Simple to archive or extract features

## Migration Path

### For Existing Implementations
```bash
# Move existing services to proper location
mv services/user-authentication-api implementations/user-authentication/services/
mv frontend/user-authentication-web implementations/user-authentication/frontend/
mv ml-services/user-authentication-ml implementations/user-authentication/ml-services/
mv infrastructure/k8s/user-authentication/* implementations/user-authentication/infrastructure/k8s/
mv infrastructure/docker/user-authentication/* implementations/user-authentication/infrastructure/docker/
```

### Update Workflow Executors
The workflow executors need to be updated to create the correct structure:

```python
# Instead of:
service_path = self.project_root / f"services/{spec_name}-api/"

# Should be:
service_path = self.project_root / f"implementations/{spec_name}/services/{spec_name}-api/"
```

## Implementation Rules

### ✅ DO:
- Create all feature code under `implementations/{feature-name}/`
- Keep feature code isolated and self-contained
- Include README.md with feature overview
- Create proper subfolder structure (services, frontend, ml-services, infrastructure)

### ❌ DON'T:
- Create service folders directly in root
- Mix code from different features
- Create infrastructure configs outside feature folder
- Pollute root with feature-specific folders

## Benefits of Correct Structure

1. **Scalability**: Can have 100s of features without cluttering root
2. **Maintainability**: Easy to find and update feature code
3. **Portability**: Can move features between projects easily
4. **Clarity**: Clear what code belongs to what feature
5. **CI/CD**: Simple to set up per-feature pipelines

## Next Steps

1. **Fix Workflow Executors**: Update all paths to use `implementations/{feature}/` structure
2. **Clean Up Root**: Move existing misplaced folders
3. **Update Documentation**: Ensure all docs reflect correct structure
4. **Validate**: Run cleanup script to verify structure

---

*This structure follows the steering document at `.claude/steering/structure.md`*