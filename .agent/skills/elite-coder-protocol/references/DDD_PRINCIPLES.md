# 🏛️ Referencia Teórica: Arquitectura Limpia y DDD (Para Agentes ELITE)

Este documento no es para leerse rápido. Es el "Código Hammurabi" que dicta cómo el *Elite Coder Protocol* evalúa el código.

## 1. Domain-Driven Design (DDD) Estricto
La aplicación está dividida en capas inquebrantables. **No se pueden saltar.**
*   `app/domain`: La realeza. Aquí van modelos `Pydantic` sueltos, interfaces de Repositorios, lógicas abstractas. **PROHIBIDO** importar HTTP, frameworks web (FastAPI), O ORMs (Supabase/SQL). Si ves esto, falla la auditoría.
*   `app/application`: Los casos de uso (`services/`). Aquí orquestas. Llamas al Repositorio de Infraestructura para buscar el Objeto de Dominio, haces validaciones de negocio, devuelves a la ruta. **ZONA LIBRE DE HTTP**.
*   `app/infrastructure`: La sala de máquinas sucia. Aquí sí importas Supabase, Redis (`upstash`), QStash. Aquí implementas los adaptadores. 
*   `app/interfaces/api`: Los Routers de FastAPI. Son estúpidos. Solo reciben JSON, se lo pasan a `application` y devuelven Códigos HTTP 200/400. Cero lógica de negocio aquí.

## 2. Solid & Separation of Concerns (SoC)
*   **Single Responsibility**: Si un archivo hace dos cosas divergentes (Ej. Valida emails Y guarda en base de datos), refactorízalo inmediatamente en dos Helpers/Módulos. Aplicar Neuron 2.
*   **Dependency Inversion**: Los servicios no instancian los repositorios concretos. Se inyectan. Esto permite el Moking en los Test `L2_components` que acabamos de endurecer.

## 3. Asincronía y Edge (Filosofía Non-Blocking)
*   **Performance is Integrity**: Nunca uses `time.sleep()`. Nunca uses una librería bloqueante si existe una alternativa asíncrona (usa `httpx` no `requests`, usa I/O asíncrono). El Edge de Vercel te matará el request a los 10 segundos si bloqueas el thread.

Si la Neurona 2 (`complexity_analyzer.py`) salta, es porque has violado la regla del Single Responsibility. Vuelve aquí, repasa las capas y aplica Cirugía de Código.
