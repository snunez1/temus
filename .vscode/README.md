# VS Code Workspace Configuration

This directory contains VS Code workspace configuration for the Temus case study project.

## Extensions Required

The following extensions are automatically installed when opening this workspace:

- **ms-vscode.live-server** (Live Preview) - For presentation development
- **ms-python.python** - Python development support  
- **ms-toolsai.jupyter** - Jupyter notebook support
- **ms-azuretools.vscode-docker** - Docker support
- **yzhang.markdown-all-in-one** - Markdown editing
- **streetsidesoftware.code-spell-checker** - Spell checking
- **esbenp.prettier-vscode** - Code formatting

## Tasks Available

Use `Ctrl+Shift+P` → "Tasks: Run Task" to access:

- **Build Presentation** - Concatenates sections into slides.md
- **Start Presentation Live Preview** - Builds and previews presentation
- **Watch Presentation Sections** - Auto-rebuilds on section changes
- **MCP Server Start** - Starts the Model Context Protocol server

## Live Preview Setup

The presentation is configured to use Live Preview extension:

1. **Auto-start**: Live Preview should automatically detect `presentation/index.html`
2. **Port**: Configured to use port 3000
3. **Auto-refresh**: Enabled for saved file changes
4. **Default path**: Set to `/presentation/index.html`

### To Preview Presentation

1. Right-click on `presentation/index.html`
2. Select "Show Preview" or "Open with Live Preview"
3. Or use Command Palette: "Live Preview: Show Preview"

### Troubleshooting

If Live Preview doesn't work:
1. Check extension is installed: `ms-vscode.live-server`
2. Restart VS Code to reload extension
3. Use Command Palette: "Live Preview: Start Server"
4. Check port 3000 is not in use by other applications
