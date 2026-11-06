# Prompt Templates for Deal Agents

## Propensity Scoring Prompt
You are a CRE analyst. Score this property's likelihood to sell in next 12 months (0-1) based on:
- Ownership tenure
- Recent permits or distress signals
- Market conditions
- Refinance date proximity
Output only JSON: {"score": 0.75, "reasons": ["..."]}

## OM Extraction Prompt
Extract structured data from this offering memorandum:
- Asking price
- Cap rate
- NOI
- Occupancy
- Key risks
Use JSON schema. Be precise; flag missing data.

## Outreach Generation Prompt
Generate a personalized email to the property owner based on signals:
Context: {signals}
Tone: professional, value-first, not salesy.
