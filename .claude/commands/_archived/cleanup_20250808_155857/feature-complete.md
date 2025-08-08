Execute complete feature analysis using all specialized agents in optimal sequence.

## Process

This command will:
1. Use product-manager agent for initial vision and scoping
2. Based on PM output, invoke relevant agents:
   - business-analyst for requirements (always)
   - architect for technical design (if technical complexity detected)
   - uiux-designer for interface design (if UI changes needed)
3. Synthesize all outputs into a unified feature plan
4. Generate implementation tasks

## Intelligent Routing

I'll analyze the product manager's output to determine which agents are needed:
- If the feature mentions "API" or "integration" → include architect
- If the feature mentions "interface" or "user experience" → include uiux-designer
- If the feature mentions "algorithm" or "performance" → include architect with performance focus

## Output Format

The final output will be a comprehensive document containing:
1. Product Vision (from product-manager)
2. Detailed Requirements (from business-analyst)
3. Technical Architecture (from architect, if applicable)
4. UI/UX Specifications (from uiux-designer, if applicable)
5. Implementation Tasks (generated from all inputs)

## Usage
/feature-complete "Feature description"

## Example
/feature-complete "Add real-time collaboration to document editor"