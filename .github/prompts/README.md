# Claude Prompt System for Temus Wind Forecasting

This directory contains prompt files optimized for Claude to assist with the Temus/McKinsey wind power forecasting case study.

## Integration Approach: Automatic Core Knowledge + @workspace for Specific Prompts

### Automatic Integration (settings.json)

The following prompt files are always loaded for every Copilot and Claude interaction via `.vscode/settings.json`:

- `claude-context.prompt.md` — Claude-specific optimization and project context
- `case-requirements.prompt.md` — Submission requirements and success criteria
- `wind-power-domain.prompt.md` — Wind power physics and forecasting knowledge

**Example `.vscode/settings.json`:**

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    { "file": "./.github/prompts/claude-context.prompt.md" },
    { "file": "./.github/prompts/case-requirements.prompt.md" },
    { "file": "./.github/prompts/wind-power-domain.prompt.md" }
  ]
}
```

**Benefits:**
- Core domain knowledge and requirements are always available
- No manual context switching needed for most tasks
- Ensures consistency and quality across all project phases

---

## Using @workspace for Phase-Specific Guidance

For tasks that require detailed, phase-specific workflows (e.g., EDA, model development, MCP service, risk management, presentation), use the `@workspace` command in Copilot Chat or Claude to reference additional prompt files as needed.

### How to Use @workspace

1. **Reference a Prompt File in Chat:**
   - Type `@workspace` followed by the path to the prompt file you want to use for your current task.
   - Example: `@workspace .github/prompts/eda-workflow.prompt.md`

2. **Ask Your Question or Give Your Instruction:**
   - After referencing the file, describe your task or question.
   - Example: `@workspace .github/prompts/model-development.prompt.md
Help me implement the ensemble model architecture for wind power forecasting.`

### Example Scenarios

#### 1. Exploratory Data Analysis (EDA)
```
@workspace .github/prompts/eda-workflow.prompt.md
Please perform a systematic EDA on the GEF2012 wind dataset, following the workflow in this file.
```

#### 2. Model Development
```
@workspace .github/prompts/model-development.prompt.md
Implement a Random Forest and XGBoost model for 48-hour wind power forecasting. Compare their performance.
```

#### 3. MCP Service Implementation
```
@workspace .github/prompts/mcp-service.prompt.md
Guide me through building a FastAPI MCP service for wind power prediction, using the structure in this prompt.
```

#### 4. Risk Management
```
@workspace .github/prompts/risk-management.prompt.md
How should I set up model risk monitoring and automated retraining for this project?
```

#### 5. Presentation Preparation
```
@workspace .github/prompts/presentation-outline.prompt.md
Help me outline a McKinsey-style presentation for the wind forecasting case study.
```

---

## Best Practices

- Use automatic integration for all general coding, analysis, and documentation tasks.
- Use `@workspace` to bring in detailed, phase-specific guidance only when needed.
- Reference prompt files by their relative path from the workspace root (e.g., `.github/prompts/model-development.prompt.md`).
- For multi-step tasks, you can reference more than one prompt file in a single message if needed.

---

## Prompt File Overview

| Prompt File | Purpose |
|-------------|---------|
| `claude-context.prompt.md` | Claude-specific optimization and project context |
| `case-requirements.prompt.md` | Submission requirements and success criteria |
| `wind-power-domain.prompt.md` | Wind power physics and forecasting knowledge |
| `eda-workflow.prompt.md` | Systematic exploratory data analysis (use with @workspace) |
| `model-development.prompt.md` | ML model implementation workflow (use with @workspace) |
| `mcp-service.prompt.md` | MCP service implementation guide (use with @workspace) |
| `risk-management.prompt.md` | Model risk and monitoring framework (use with @workspace) |
| `presentation-outline.prompt.md` | McKinsey-style presentation structure (use with @workspace) |

---

This approach ensures that core knowledge is always available, while detailed, phase-specific workflows can be brought in on demand using `@workspace` for maximum flexibility and efficiency.
