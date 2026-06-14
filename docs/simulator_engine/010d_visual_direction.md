# 010D Visual Direction

## Direction: Hybrid Premium Simulator

### General Pages (Home, Domains, Login, Profile)
- **Style**: Clean, bright, product-grade SaaS/EdTech
- **Vibe**: Professional training platform, calm and structured
- **Key traits**: Ample whitespace, clear hierarchy, readable typography, consistent card system
- **Inspiration**: High-end EdTech platforms, structured learning environments

### Quest Catalog
- **Style**: Mission cards / professional simulator
- **Vibe**: Each quest is a mission briefing — clear purpose, stakes, and context
- **Key traits**: Card-based layout with hover lift, clear metadata, prominent CTA
- **Inspiration**: Mission briefing screens, interactive learning platforms

### Quest Play
- **Style**: Immersive mission-control training interface
- **Vibe**: The learner is in a scenario — narrative context, status meters, decisions matter
- **Key traits**: Controlled visual density, story panel, progress stepper, status meter
- **Inspiration**: Modern AI product interfaces, mission-control dashboards

### Outcome / Debrief
- **Style**: Clean educational report
- **Vibe**: Professional feedback — structured, actionable, readable
- **Key traits**: Clear sections (strengths, improvement areas, skill profile), status meter recap
- **Inspiration**: Performance review dashboards, learning management reports

### Motion Level: Subtle
- Hover lift on cards: `transition-all duration-200 hover:-translate-y-0.5`
- Focus glow on interactive elements
- Progress bar animation
- Selected option transition
- Respects `prefers-reduced-motion`

### Dark Mode Usage
- Quest surfaces only (immersive backgrounds for quest play)
- General pages remain light
- Infrastructure ready for future toggle

### Design Goal
Readable, premium, consistent, simulator-like — not a generic template.

## Design Principles
1. **Consistency over creativity** — one way to do each thing
2. **Hierarchy through typography** — size and weight communicate importance
3. **Color with purpose** — semantic colors for meaning, not decoration
4. **Subtle motion** — enhance, don't distract
5. **Readability first** — minimum 16px for body text, 17px for story text
