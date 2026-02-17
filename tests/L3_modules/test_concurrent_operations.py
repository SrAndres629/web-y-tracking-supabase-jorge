"""
⚡ Concurrent Operations Tests

Tests para verificar comportamiento thread-safe y race conditions.
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from app.core.result import Result
from app.domain.models.lead import Lead
from app.domain.models.values import ExternalId, Phone
from app.domain.models.visitor import Visitor

# =============================================================================
# ASYNC CONCURRENCY TESTS
# =============================================================================


class TestAsyncConcurrency:
    """Tests para operaciones async concurrentes"""

    @pytest.mark.asyncio
    async def test_concurrent_visitor_creation(self):
        """
        Múltiples creaciones de visitantes concurrentes deben funcionar
        sin errores de integridad.
        """

        async def create_visitor_task(ip_suffix: int) -> Visitor:
            return Visitor.create(ip=f"192.168.1.{ip_suffix}", user_agent=f"TestBot/{ip_suffix}")

        # Crear 100 visitantes concurrentemente
        tasks = [create_visitor_task(i) for i in range(100)]
        visitors = await asyncio.gather(*tasks)

        # Verificar que todos se crearon
        assert len(visitors) == 100

        # Verificar que todos tienen IDs únicos (diferentes IP+UA)
        external_ids = [v.external_id.value for v in visitors]
        assert len(set(external_ids)) == 100

    @pytest.mark.asyncio
    async def test_concurrent_external_id_generation(self):
        """
        Generación concurrente de ExternalIds debe ser determinística.
        """

        async def generate_id(ip: str) -> str:
            return ExternalId.from_request(ip, "Mozilla/5.0").value

        # Múltiples tareas con el mismo IP deben generar mismo ID
        tasks = [generate_id("1.1.1.1") for _ in range(50)]
        ids = await asyncio.gather(*tasks)

        # Todos deben ser iguales (determinismo)
        assert len(set(ids)) == 1

    @pytest.mark.asyncio
    async def test_concurrent_result_operations(self):
        """
        Operaciones concurrentes con Result type.
        """

        async def process_value(value: int) -> Result[int, str]:
            await asyncio.sleep(0.001)  # Simular trabajo
            if value % 2 == 0:
                return Result.ok(value * 2)
            return Result.err(f"Odd number: {value}")

        tasks = [process_value(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        # Verificar que los resultados son correctos
        ok_count = sum(1 for r in results if r.is_ok)
        err_count = sum(1 for r in results if r.is_err)

        assert ok_count == 50  # Números pares
        assert err_count == 50  # Números impares

    @pytest.mark.asyncio
    async def test_async_repositories_concurrent_access(self, mock_visitor_repository):
        """
        Repositorios deben soportar acceso concurrente.
        """
        from unittest.mock import AsyncMock

        # Setup mock
        mock_visitor_repository.get_by_external_id = AsyncMock(return_value=None)
        mock_visitor_repository.save = AsyncMock(return_value=None)

        external_id = ExternalId.from_request("1.1.1.1", "Test")

        async def access_repo():
            await mock_visitor_repository.get_by_external_id(external_id)
            visitor = Visitor.create(ip="1.1.1.1", user_agent="Test")
            await mock_visitor_repository.save(visitor)
            return True

        # 50 accesos concurrentes
        tasks = [access_repo() for _ in range(50)]
        results = await asyncio.gather(*tasks)

        assert all(results)
        assert mock_visitor_repository.save.call_count == 50


# =============================================================================
# THREAD SAFETY TESTS
# =============================================================================


class TestThreadSafety:
    """Tests para verificar thread-safety"""

    def test_event_id_generation_thread_safety(self):
        """
        Generación de EventIds desde múltiples threads debe ser segura.
        """
        from app.domain.models.values import EventId

        event_ids = []
        errors = []

        def generate_ids():
            try:
                for _ in range(100):
                    event_ids.append(EventId.generate().value)
            except Exception as e:
                errors.append(str(e))

        # Crear y ejecutar threads
        threads = [threading.Thread(target=generate_ids) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No debe haber errores
        assert len(errors) == 0, f"Errors during concurrent generation: {errors}"

        # Debe haber 1000 IDs únicos
        assert len(set(event_ids)) == 1000

    def test_result_thread_safety(self):
        """
        Result type debe ser thread-safe (inmutable).
        """
        results = []

        def create_results():
            for i in range(100):
                if i % 2 == 0:
                    results.append(Result.ok(i))
                else:
                    results.append(Result.err(f"error {i}"))

        threads = [threading.Thread(target=create_results) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verificar que no hay corrupción
        ok_results = [r for r in results if r.is_ok]
        err_results = [r for r in results if r.is_err]

        assert len(ok_results) == 250
        assert len(err_results) == 250

    def test_concurrent_phone_parsing(self):
        """
        Parsing de teléfonos concurrente debe ser seguro.
        """
        phone_numbers = [f"777{i:05d}" for i in range(1000)]
        results = []

        def parse_phones(numbers):
            for num in numbers:
                result = Phone.parse(num, country="BO")
                results.append(result)

        # Dividir trabajo entre threads
        chunk_size = 250
        threads = [
            threading.Thread(target=parse_phones, args=(phone_numbers[i : i + chunk_size],))
            for i in range(0, len(phone_numbers), chunk_size)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Todos deben ser exitosos
        assert all(r.is_ok for r in results)

        # Todos deben tener formato correcto
        phones = [r.unwrap() for r in results]
        assert all(p.number.startswith("+591") for p in phones)


# =============================================================================
# RACE CONDITION TESTS
# =============================================================================


class TestRaceConditions:
    """Tests específicos para race conditions"""

    @pytest.mark.asyncio
    async def test_no_race_in_visitor_visit_count(self):
        """
        Simular race condition en visit_count del visitor.

        Nota: En una implementación real con persistencia,
        esto requeriría locks optimistas o transacciones.
        """
        visitor = Visitor.create(ip="1.1.1.1", user_agent="Test")
        initial_count = visitor.visit_count

        async def increment_visit():
            # En memoria, esto es atómico para un objeto
            visitor.record_visit()

        # Múltiples incrementos concurrentes
        tasks = [increment_visit() for _ in range(100)]
        await asyncio.gather(*tasks)

        # En memoria (sin persistencia), el resultado es correcto
        # porque Python's GIL protege operaciones atómicas simples
        assert visitor.visit_count == initial_count + 100

    @pytest.mark.asyncio
    async def test_concurrent_deduplication_simulation(self):
        """
        Simular sistema de deduplicación concurrente.
        """
        processed_events = set()
        duplicate_count = [0]  # Mutable para contar desde coroutines

        async def process_event(event_id: str) -> bool:
            if event_id in processed_events:
                duplicate_count[0] += 1
                return False  # Duplicado
            processed_events.add(event_id)
            await asyncio.sleep(0.001)  # Simular procesamiento
            return True

        # Enviar eventos, algunos duplicados
        event_ids = [f"event_{i % 50}" for i in range(200)]  # 200 events, 50 únicos
        tasks = [process_event(eid) for eid in event_ids]
        results = await asyncio.gather(*tasks)

        # Solo 50 deben ser procesados únicos
        assert sum(results) == 50
        assert duplicate_count[0] == 150  # 150 duplicados


# =============================================================================
# STRESS TESTS
# =============================================================================


class TestStress:
    """Tests de carga y estrés"""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_stress_value_object_creation(self):
        """
        Crear miles de value objects bajo carga.
        """
        start_time = time.time()

        async def create_batch(batch_id: int) -> int:
            count = 0
            for i in range(100):
                phone = Phone.parse(f"777{i:05d}", country="BO")
                if phone.is_ok:
                    Lead.create(phone=phone.unwrap(), name=f"Lead {batch_id}-{i}")
                    count += 1
            return count

        # 50 batches concurrentes = 5000 operaciones
        tasks = [create_batch(i) for i in range(50)]
        results = await asyncio.gather(*tasks)

        elapsed = time.time() - start_time

        assert sum(results) == 5000
        assert elapsed < 10  # Debe completarse en menos de 10 segundos

    @pytest.mark.slow
    def test_stress_external_id_generation(self):
        """
        Generar millones de ExternalIds y verificar unicidad.
        """
        ids = set()

        def generate_batch(start: int):
            batch_ids = set()
            for i in range(10000):
                ip = f"192.168.{(start + i) // 256}.{(start + i) % 256}"
                external_id = ExternalId.from_request(ip, f"Agent/{i}")
                batch_ids.add(external_id.value)
            return batch_ids

        # Usar thread pool
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(generate_batch, i * 10000) for i in range(4)]
            for future in as_completed(futures):
                ids.update(future.result())

        # Debe haber 40000 IDs únicos
        assert len(ids) == 40000


# =============================================================================
# DEADLOCK PREVENTION TESTS
# =============================================================================


class TestDeadlockPrevention:
    """Tests para prevenir deadlocks"""

    @pytest.mark.asyncio
    async def test_no_deadlock_in_async_operations(self):
        """
        Múltiples operaciones async no deben causar deadlock.
        """

        async def operation_a():
            await asyncio.sleep(0.01)
            return "A"

        async def operation_b():
            await asyncio.sleep(0.01)
            return "B"

        # Combinar operaciones que dependen entre sí
        async def combined():
            a, b = await asyncio.gather(operation_a(), operation_b())
            return f"{a}-{b}"

        # Ejecutar muchas veces
        tasks = [combined() for _ in range(100)]
        results = await asyncio.gather(*tasks)

        assert all(r == "A-B" for r in results)

    @pytest.mark.timeout(5)  # Timeout de 5 segundos
    @pytest.mark.asyncio
    async def test_timeout_prevents_infinite_wait(self):
        """
        Las operaciones deben tener timeout para prevenir bloqueos infinitos.
        """

        async def slow_operation():
            await asyncio.sleep(10)  # Muy lento
            return "done"

        try:
            # Debe timeout antes de 10 segundos
            await asyncio.wait_for(slow_operation(), timeout=0.1)
            assert False, "Should have timed out"
        except asyncio.TimeoutError:
            pass  # Expected


# =============================================================================
# CONSISTENCY TESTS
# =============================================================================


class TestConsistency:
    """Tests de consistencia de datos bajo concurrencia"""

    @pytest.mark.asyncio
    async def test_eventual_consistency_simulation(self):
        """
        Simular consistencia eventual en sistema distribuido.
        """
        # Simular múltiples nodos actualizando
        node_states = {}

        async def update_from_node(node_id: int, value: int):
            await asyncio.sleep(0.001)  # Latencia de red
            node_states[node_id] = value

        # Múltiples actualizaciones concurrentes
        tasks = [update_from_node(i, i * 10) for i in range(20)]
        await asyncio.gather(*tasks)

        # Cada nodo debe tener su valor correcto
        for i in range(20):
            assert node_states[i] == i * 10
