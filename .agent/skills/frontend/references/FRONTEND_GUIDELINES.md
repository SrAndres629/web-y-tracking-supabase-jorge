# Frontend Architecture & Guidelines: Jorge Aguirre Flores

## 🏗️ Core Architecture
- **Jinja2 Templates**: Component-based structure in `api/templates/components/`.
- **Atomic CSS**: Powered by Tailwind and custom design tokens.
- **Micro-Engines**: Specialized JS modules in `static/engines/` (Tracking, Motion, UI).

## 🎨 Design Principles
- **Silencio de Lujo (Quiet Luxury)**: Minimalist yet premium. Golden accents on dark grounds.
- **Glassmorphism**: Use of `backdrop-blur` and semi-transparent borders for high-depth effects.
- **Micro-Animations**: GSAP-driven subtle transitions using ScrollTrigger.

## 🛠️ Development Workflow
1. **Audit**: `python3 scripts/frontend_orchestrator.py audit`.
2. **Saneamiento**: Cleanup of legacy code.
3. **Modularization**: Refactoring into components.
4. **Validation**: Closing via `auditoria-qa`.
