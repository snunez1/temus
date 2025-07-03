# Temus Wind Power Forecasting Presentation - v4 Modular

This directory contains a 45-minute McKinsey-style presentation on wind power forecasting for sustainability, built using reveal.js with modular sections and custom HTML slide support.

## Quick Start

1. **Install VS Code Live Server Extension**
   ```bash
   code --install-extension ms-vscode.live-server
   ```

2. **Open and Build the Presentation**
   ```bash
   # Open the main Temus project in VS Code
   code /workspaces/temus
   
   # Build slides.md from sections using VS Code task
   # Press Ctrl+Shift+P → "Run Task" → "Build Presentation"
   # Or run manually:
   python presentation/scripts/concat-sections.py
   ```

3. **Start Live Preview**
   - Navigate to `presentation/index.html` in VS Code Explorer
   - Right-click on `index.html`
   - Select "Open with Live Server"
   - Browser opens at `http://localhost:5500`
   - Or use VS Code task: "Start Presentation Live Server"

4. **Edit Sections**
   - Edit individual files in `presentation/sections/` directory
   - Run "Build Presentation" task after changes (Ctrl+Shift+P → Run Task)
   - Browser auto-refreshes with Live Server

## Directory Structure

```
presentation/
├── README.md              # This file
├── index.html             # Reveal.js container
├── slides.md              # AUTO-GENERATED - Do not edit!
├── sections/              # EDIT THESE FILES
│   ├── 00-title.md       # Title slide
│   ├── 01-executive-summary.md
│   ├── 02-problem-statement.md
│   ├── 03-data-insights.md
│   ├── 04-model-performance.md
│   ├── 05-mcp-architecture.md
│   ├── 06-business-impact.md
│   ├── 07-next-steps.md
│   └── custom/           # Custom HTML slides
│       └── *.html
├── assets/
│   ├── css/              # Styling
│   ├── js/               # Scripts
│   └── images/           # Charts and diagrams
├── scripts/
│   └── concat-sections.py # Combines sections
└── exports/              # PDF outputs
```

**Note**: VS Code configuration is in the main project root (`/workspaces/temus/.vscode/`)

## Modular Editing Workflow

### Why Modular Sections?
- **Isolated editing**: Work on one topic without scrolling through 30 slides
- **Version control**: Git shows cleaner diffs for section changes
- **Collaboration**: Multiple people can work on different sections
- **Reusability**: Sections can be reused across presentations

### Editing Process
1. Open the specific section file in `sections/`
2. Make your changes
3. Run concatenate task: `Ctrl+Shift+B`
4. Preview updates in browser

### Section File Naming
- `00-title.md` - Opening slide
- `01-executive-summary.md` - Overview sections
- `02-problem-statement.md` - Problem definition
- etc.

Numbers determine slide order in final presentation.

## Custom HTML Slides

### When to Use Custom HTML
- **Interactive visualizations**: Chart.js, D3.js, Plotly
- **Complex layouts**: Beyond markdown capabilities
- **Animations**: CSS or JavaScript animations
- **External embeds**: iframes, videos, web components

### How to Include Custom HTML

1. **Create HTML file** in `sections/custom/`:
   ```html
   <!-- sections/custom/my-visualization.html -->
   <div class="custom-slide">
     <h2>Interactive Visualization</h2>
     <!-- Your HTML content -->
   </div>
   ```

2. **Include in markdown section**:
   ```markdown
   <!-- In any section file -->
   ## Regular Markdown Slide

   ---

   <!-- include-html: my-visualization.html -->

   ---

   ## Next Regular Slide
   ```

3. **Run concatenate**: The HTML will be embedded as a reveal.js section

### Custom HTML Best Practices
- Include all styles within the HTML file or use `<style>` tags
- Use reveal.js events for initialization: `Reveal.on('slidechanged', ...)`
- Keep files self-contained for portability
- Test in presentation mode (not just preview)

## Advanced Custom Slides Examples

### 1. Interactive Chart (Chart.js)
See `sections/custom/interactive-eda-chart.html` for a complete example with:
- Dynamic chart updates
- Button controls
- Reveal.js integration

### 2. Animated Timeline
```html
<!-- sections/custom/timeline.html -->
<div class="timeline-container">
  <h2>Implementation Timeline</h2>
  <div class="timeline">
    <div class="phase" data-delay="0">Phase 1: Foundation</div>
    <div class="phase" data-delay="1">Phase 2: Development</div>
    <div class="phase" data-delay="2">Phase 3: Deployment</div>
  </div>
</div>

<style>
.phase {
  opacity: 0;
  transform: translateX(-50px);
  transition: all 0.5s ease;
}
.phase.active {
  opacity: 1;
  transform: translateX(0);
}
</style>

<script>
Reveal.on('slidechanged', event => {
  if (event.currentSlide.querySelector('.timeline')) {
    const phases = event.currentSlide.querySelectorAll('.phase');
    phases.forEach((phase, i) => {
      setTimeout(() => phase.classList.add('active'), i * 500);
    });
  }
});
</script>
```

### 3. Embedded Dashboard
```html
<!-- sections/custom/dashboard.html -->
<div style="height: 100%; width: 100%;">
  <h2>Live MCP Service Dashboard</h2>
  <iframe 
    src="https://your-grafana-instance.com/dashboard"
    width="100%" 
    height="80%" 
    frameborder="0">
  </iframe>
</div>
```

## Slide Writing Guide

### Basic Slide
```markdown
---

## Slide Title

- Bullet point 1
- Bullet point 2
- **Bold text** for emphasis

Note: Speaker notes go here (press 'S' in presentation)
```

### Two-Column Layout
```markdown
---

## Two Column Slide

<div class="columns">
<div class="column">

### Left Column
- Point 1
- Point 2

</div>
<div class="column">

### Right Column  
- Point A
- Point B

</div>
</div>
```

### Statistics Grid
```markdown
---

## Key Metrics

<div class="stats-grid">
<div class="stat-box">
<h3>47%</h3>
<p>RMSE Improvement</p>
</div>
<div class="stat-box">
<h3>$3.2M</h3>
<p>Annual Savings</p>
</div>
<div class="stat-box">
<h3>42,000</h3>
<p>Tons CO2 Reduced</p>
</div>
</div>
```

### Code Blocks
```markdown
---

## Technical Implementation

```python
@mcp.tool()
async def predict_wind_power(wind_farm_id: str) -> float:
    """Predict wind power generation"""
    features = engineer_features(wind_farm_id)
    return model.predict(features)
```
```

## Adding Charts from Notebooks

1. **Export charts from Jupyter notebooks as PNG**
   - In notebook: `plt.savefig('model_performance.png', dpi=300, bbox_inches='tight')`
   
2. **Copy to presentation**
   ```bash
   cp /workspaces/temus/notebooks/outputs/figures/*.png assets/images/
   ```

3. **Reference in sections**
   ```markdown
   ![Model Performance](assets/images/model_performance.png)
   ```

## Presentation Controls

- **Next slide**: Space, Arrow Right, or Click
- **Previous slide**: Arrow Left
- **Speaker notes**: Press 'S'
- **Overview**: Press 'ESC'
- **Full screen**: Press 'F'
- **Black screen**: Press 'B'
- **Search**: Ctrl+F

## VS Code Workflow

1. **Split Screen Setup**
   - Open section file in editor
   - Press `Ctrl+\` to split editor
   - Keep browser on second monitor

2. **Quick Navigation**
   - `Ctrl+P` → Quick file open (jump between sections)
   - `Ctrl+Shift+O` → Outline view
   - `Ctrl+F` → Find content within section

3. **Live Editing**
   - Changes save automatically with `files.autoSave`
   - Run `Ctrl+Shift+B` to concatenate sections
   - Browser refreshes with updated slides

## VS Code Shortcuts

### Essential Commands
- **Ctrl+Shift+P → "Run Task" → "Build Presentation"**: Build (concatenate sections)
- **Ctrl+K V**: Preview markdown section
- **Ctrl+P**: Quick file open (jump between sections)
- **Ctrl+Shift+F**: Search across all files including sections

### Recommended Workflow
1. **Open main project**: `code /workspaces/temus`
2. **Navigate to section**: Ctrl+P, type `presentation/sections/filename`
3. **Edit section**: Make changes
4. **Build**: Ctrl+Shift+P → Run Task → "Build Presentation"
5. **Check browser**: Auto-refreshes with changes

## Tips for Section-Based Development

### Organization
- Keep sections focused: 2-4 slides per section file
- Use descriptive filenames
- Group related content in same section

### Consistency
- Start each section with a main topic slide
- Use `---` for slide breaks consistently
- Include speaker notes with `Note:`

### Collaboration
- Assign sections to team members
- Use git branches for section development
- Merge sections in numerical order

## Exporting to PDF

### Manual Method (Recommended)
1. Open presentation in Chrome
2. Add `?print-pdf` to URL: `http://localhost:5500/?print-pdf`
3. Press `Ctrl+P` to print
4. Select "Save as PDF"
5. Settings:
   - Layout: Landscape
   - Margins: None
   - Background graphics: Yes

### Automated Method (Optional)
```bash
# Install decktape globally
npm install -g decktape

# Export to PDF
decktape reveal http://localhost:5500 exports/temus-presentation.pdf
```

## Presentation Tips

### Content Guidelines
- **Title slides**: Clear, action-oriented headlines
- **Bullet points**: Maximum 6 per slide
- **Data**: One key chart per slide
- **Text**: Sans-serif, left-aligned
- **Colors**: McKinsey blue (#003A70) for emphasis

### Timing (45 minutes)
- **Introduction**: 2-3 minutes (slides 1-3)
- **Problem/Opportunity**: 5 minutes (slides 4-7)
- **Technical Approach**: 15 minutes (slides 8-17)
- **Results/Impact**: 10 minutes (slides 18-22)
- **Implementation**: 8 minutes (slides 23-27)
- **Q&A Buffer**: 5 minutes (slides 28-30)
- **Discussion**: 15 minutes

### McKinsey Style
- Avoid adjectives like "comprehensive", "innovative", "cutting-edge"
- Lead with insights, not process
- Quantify impact in business terms
- Use professional, clean visualizations
- Include clear next steps

## Troubleshooting

### Sections Not Updating
1. Ensure you ran concat-sections.py
2. Check for syntax errors in markdown
3. Verify file naming (must start with number)

### Custom HTML Not Showing
1. Check file path in include directive
2. Ensure HTML file exists in sections/custom/
3. Look for errors in browser console

### Live Server Not Working
- Ensure extension is installed
- Check port 5500 is not in use
- Try different port in settings

### Images Not Showing
- Check file paths are relative: `assets/images/chart.png`
- Ensure images are in PNG or JPG format
- Verify image files exist in directory

## Build Automation

For automatic rebuilding on save:
```bash
# Install watchdog (optional)
pip install watchdog

# Run watcher
python scripts/watch-sections.py
```

## Next Steps

1. Review existing section files
2. Add missing charts to `assets/images/`
3. Create any needed custom HTML visualizations
4. Run final build and export to PDF

The modular structure makes it easy to iterate on individual sections while maintaining the overall presentation flow.

## File Structure Summary

```
✓ index.html - Main reveal.js container
✓ sections/00-title.md - Title slide
✓ sections/01-executive-summary.md - Overview and key messages
✓ sections/02-problem-statement.md - Challenge definition
✓ sections/03-data-insights.md - EDA and feature engineering
✓ sections/04-model-performance.md - ML results and validation
✓ sections/05-mcp-architecture.md - Production deployment
✓ sections/06-business-impact.md - ROI and environmental impact
✓ sections/07-next-steps.md - Implementation roadmap
✓ sections/custom/interactive-eda-chart.html - Example custom slide
✓ assets/css/theme.css - McKinsey styling
✓ assets/css/custom.css - Additional styles
✓ scripts/concat-sections.py - Build automation
✓ .vscode/tasks.json - VS Code integration
✓ slides.md - Generated presentation (auto-created)
```

The presentation workflow is now fully implemented and ready for use!
