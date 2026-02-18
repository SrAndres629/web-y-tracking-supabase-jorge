"""
🧪 Silicon Valley Testing Infrastructure

Arquitectura de testing por capas:
- unit/: Tests puros sin dependencias externas (pyramid base)
- integration/: Tests con infraestructura fake/in-memory
- e2e/: Tests de flujo completo (pyramid top)

Principios:
1. FAST: Tests unitarios < 10ms
2. ISOLATED: Sin side effects entre tests
3. REPEATABLE: Mismo resultado siempre
4. SELF-VALIDATING: Boolean pass/fail
5. TIMELY: Escritos antes o con el código
"""
