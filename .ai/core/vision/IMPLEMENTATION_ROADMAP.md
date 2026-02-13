# 🚀 ROADMAP DE IMPLEMENTACIÓN: Vision Neuronal v2.0

**Objetivo:** Transformar el MCP de un visualizador pasivo a un córtex cognitivo activo.

---

## 📋 FASE 1: CORRECCIONES CRÍTICAS (Semana 1)

### 1.1 Resolución de Imports (Prioridad: CRÍTICA)

**Archivo:** `cortex_v2/importer.py`

```python
import ast
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

class ImportResolver:
    """
    Resuelve imports a referencias concretas en el grafo.
    Soporta imports absolutos y relativos.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.module_to_file: Dict[str, Path] = {}
        self.file_to_module: Dict[Path, str] = {}
        self._build_module_map()
    
    def _build_module_map(self):
        """Construye mapa de módulos Python a archivos"""
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name.startswith(".") or "__pycache__" in str(py_file):
                continue
            
            # Calcular módulo desde project_root
            relative = py_file.relative_to(self.project_root)
            module_parts = list(relative.with_suffix("").parts)
            
            # Manejar __init__.py
            if py_file.name == "__init__.py":
                module_parts = module_parts[:-1]
            
            module_name = ".".join(module_parts)
            self.module_to_file[module_name] = py_file
            self.file_to_module[py_file] = module_name
    
    def resolve_import(self, node: ast.AST, source_file: Path) -> List[Tuple[str, str]]:
        """
        Resuelve un nodo de import a (source_id, target_id).
        
        Returns:
            Lista de (source_symbol, target_symbol) resueltos
        """
        results = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                # import os -> os
                # import os.path -> os.path
                module_name = alias.name
                target_file = self.module_to_file.get(module_name)
                
                if target_file:
                    target_id = str(target_file.relative_to(self.project_root))
                    source_id = f"{source_file}::{alias.asname or alias.name}"
                    results.append((source_id, target_id))
        
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            level = node.level  # 0 = absoluto, 1 = relativo (.), 2 = (..)
            
            if level > 0:
                # Resolver relativo
                source_module = self.file_to_module.get(source_file, "")
                source_parts = source_module.split(".") if source_module else []
                
                # Subir 'level' niveles
                base_parts = source_parts[:-level] if len(source_parts) >= level else []
                
                if module:
                    full_module = ".".join(base_parts + [module])
                else:
                    full_module = ".".join(base_parts)
            else:
                full_module = module
            
            target_file = self.module_to_file.get(full_module)
            
            if target_file:
                for alias in node.names:
                    name = alias.name
                    
                    # from module import X
                    if name == "*":
                        # Wildcard import - resolver a todo el módulo
                        results.append((
                            f"{source_file}::*",
                            str(target_file.relative_to(self.project_root))
                        ))
                    else:
                        # Buscar si X es un archivo (submódulo) o un símbolo dentro del archivo
                        sub_module = f"{full_module}.{name}"
                        sub_file = self.module_to_file.get(sub_module)
                        
                        if sub_file:
                            # Es un submódulo
                            target_id = str(sub_file.relative_to(self.project_root))
                        else:
                            # Es un símbolo dentro del archivo
                            target_rel = str(target_file.relative_to(self.project_root))
                            target_id = f"{target_rel}::{name}"
                        
                        source_id = f"{source_file}::{alias.asname or name}"
                        results.append((source_id, target_id))
        
        return results
```

**Integración en cortex.py:**
```python
def _scan_file_v2(self, full_path: Path, rel_path: str, root_dir: str) -> tuple:
    """Versión mejorada con resolución de imports"""
    nodes = []
    edges = []
    
    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    file_id = rel_path
    
    # Nodo de archivo
    nodes.append({...})  # Como antes
    
    # Inicializar resolver
    resolver = ImportResolver(Path(root_dir))
    
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            # ... Funciones y clases como antes ...
            
            # NUEVO: Resolver imports
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                resolved = resolver.resolve_import(node, full_path)
                
                for source_sym, target_sym in resolved:
                    edges.append({
                        "source": file_id,
                        "target": target_sym,
                        "type": "imports",
                        "metadata": json.dumps({
                            "source_symbol": source_sym,
                            "import_type": type(node).__name__
                        })
                    })
    
    except SyntaxError:
        logger.warning(f"Syntax error in {rel_path}")
    
    return nodes, edges
```

---

### 1.2 Schema Temporal (Prioridad: ALTA)

**Migración SQL:** `migrations/v2_add_temporal.sql`

```sql
-- V2: Agregar soporte temporal

-- Historial de cambios de nodos
CREATE TABLE IF NOT EXISTS node_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    change_type TEXT NOT NULL,  -- 'created', 'modified', 'deleted'
    content_hash_old TEXT,
    content_hash_new TEXT,
    author TEXT,  -- cerebro/agente que hizo el cambio
    diff_summary TEXT,  -- resumen del diff
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);

CREATE INDEX idx_history_node ON node_history(node_id);
CREATE INDEX idx_history_time ON node_history(timestamp);

-- Métricas evolutivas
CREATE TABLE IF NOT EXISTS node_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cyclomatic_complexity INTEGER,
    lines_of_code INTEGER,
    fan_in INTEGER,
    fan_out INTEGER,
    test_coverage REAL,
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);

-- Tabla de actividad (para heatmaps)
CREATE TABLE IF NOT EXISTS node_activity (
    node_id TEXT NOT NULL,
    date DATE NOT NULL,
    change_count INTEGER DEFAULT 0,
    PRIMARY KEY (node_id, date)
);

-- Trigger para historial automático
CREATE TRIGGER IF NOT EXISTS nodes_update_history
AFTER UPDATE ON nodes
WHEN OLD.content_hash != NEW.content_hash
BEGIN
    INSERT INTO node_history (
        node_id, change_type, content_hash_old, content_hash_new
    ) VALUES (
        NEW.id, 'modified', OLD.content_hash, NEW.content_hash
    );
END;
```

---

## 📋 FASE 2: API SEMÁNTICA (Semana 2)

### 2.1 Endpoints Inteligentes

**Archivo:** `server_v2.py`

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Neuro-Vision Optic Nerve v2")

class ImpactRequest(BaseModel):
    target_file: str
    change_type: str = "modify"  # modify, delete, add

class ImpactResult(BaseModel):
    affected_files: List[str]
    affected_functions: List[str]
    risk_score: float  # 0-1
    suggested_tests: List[str]

@app.post("/api/analyze/impact", response_model=ImpactResult)
async def analyze_impact(request: ImpactRequest):
    """
    Analiza el impacto de modificar un archivo.
    
    Ejemplo: ¿Qué se rompe si modifico auth.py?
    """
    cortex = VisualCortex()
    
    # 1. Encontrar todos los nodos que dependen de target
    with sqlite3.connect(cortex.db_path) as conn:
        # Transitive closure de dependencias
        affected = conn.execute("""
            WITH RECURSIVE dependents AS (
                -- Base case: archivos que importan target
                SELECT DISTINCT source as file
                FROM edges 
                WHERE target = ? AND type = 'imports'
                
                UNION
                
                -- Recursivo: archivos que importan los afectados
                SELECT e.source
                FROM edges e
                INNER JOIN dependents d ON e.target = d.file
                WHERE e.type = 'imports'
            )
            SELECT * FROM dependents
        """, (request.target_file,)).fetchall()
    
    # 2. Calcular risk score
    risk = calculate_risk(request.target_file, affected)
    
    # 3. Sugerir tests
    suggested_tests = find_related_tests(request.target_file)
    
    return ImpactResult(
        affected_files=[a[0] for a in affected],
        affected_functions=[],  # TODO: granularidad a nivel función
        risk_score=risk,
        suggested_tests=suggested_tests
    )

@app.get("/api/query/semantic")
async def semantic_query(
    q: str = Query(..., description="Query semántica"),
    file_pattern: Optional[str] = None,
    node_type: Optional[str] = None
):
    """
    Búsqueda semántica del código.
    
    Ejemplos:
    - /api/query/semantic?q=async+functions
    - /api/query/semantic?q=auth+validation
    - /api/query/semantic?q=complexity:high
    """
    cortex = VisualCortex()
    
    # Parsear query
    if "complexity:high" in q:
        return cortex.query_high_complexity()
    elif "async" in q.lower():
        return cortex.query_async_functions(file_pattern)
    else:
        # Búsqueda por nombre/docstring
        return cortex.query_by_text(q, file_pattern, node_type)

@app.get("/api/detect/smells")
async def detect_code_smells(
    severity: str = Query("all", enum=["all", "high", "medium", "low"])
):
    """Detecta code smells en el proyecto."""
    cortex = VisualCortex()
    return cortex.detect_smells(min_severity=severity)
```

---

## 📋 FASE 3: ML Y PREDICCIÓN (Semana 3-4)

### 3.1 Predictor de Riesgo

**Archivo:** `predictors/risk_model.py`

```python
import sqlite3
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

class BugRiskPredictor:
    """
    Predice probabilidad de bugs basado en:
    - Métricas de código
    - Historial de cambios
    - Autor del código
    """
    
    FEATURES = [
        'cyclomatic_complexity',
        'lines_of_code',
        'fan_in',
        'fan_out',
        'change_frequency',
        'author_count',
        'age_days',
        'test_coverage'
    ]
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.model = None
        self.load_or_train()
    
    def extract_features(self, node_id: str) -> dict:
        """Extrae features de un nodo"""
        with sqlite3.connect(self.db_path) as conn:
            # Métricas actuales
            metrics = conn.execute("""
                SELECT * FROM node_metrics 
                WHERE node_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (node_id,)).fetchone()
            
            # Historial de cambios
            change_count = conn.execute("""
                SELECT COUNT(*) FROM node_history 
                WHERE node_id = ? AND timestamp > datetime('now', '-30 days')
            """, (node_id,)).fetchone()[0]
            
            # Autores únicos
            authors = conn.execute("""
                SELECT COUNT(DISTINCT author) FROM node_history 
                WHERE node_id = ?
            """, (node_id,)).fetchone()[0]
            
            return {
                'cyclomatic_complexity': metrics[3] if metrics else 1,
                'lines_of_code': metrics[4] if metrics else 1,
                'fan_in': metrics[5] if metrics else 0,
                'fan_out': metrics[6] if metrics else 0,
                'change_frequency': change_count,
                'author_count': authors,
                'age_days': 0,  # TODO: calcular desde creación
                'test_coverage': metrics[7] if metrics else 0.0
            }
    
    def predict(self, node_id: str) -> dict:
        """Predice riesgo para un nodo"""
        if not self.model:
            return {"risk_score": 0.5, "confidence": 0.0}
        
        features = self.extract_features(node_id)
        X = np.array([[features[f] for f in self.FEATURES]])
        
        proba = self.model.predict_proba(X)[0]
        
        return {
            "risk_score": float(proba[1]),  # Probabilidad de bug
            "confidence": float(max(proba)),
            "features": features
        }
    
    def train(self, labeled_data: list):
        """
        Entrena el modelo con datos etiquetados.
        
        labeled_data: [(node_id, had_bug_boolean), ...]
        """
        X = []
        y = []
        
        for node_id, had_bug in labeled_data:
            features = self.extract_features(node_id)
            X.append([features[f] for f in self.FEATURES])
            y.append(1 if had_bug else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_train, y_train)
        
        # Evaluar
        accuracy = self.model.score(X_test, y_test)
        print(f"Model accuracy: {accuracy:.2%}")
        
        # Guardar
        joblib.dump(self.model, "bug_predictor.pkl")
    
    def load_or_train(self):
        """Carga modelo existente o usa heurísticas"""
        try:
            self.model = joblib.load("bug_predictor.pkl")
        except FileNotFoundError:
            # Usar heurísticas simples si no hay modelo
            pass
```

---

## 📋 FASE 4: INTEGRACIÓN NEURAL HIVE (Semana 4)

### 4.1 Conector Bidireccional

**Archivo:** `integrations/hive_connector.py`

```python
import asyncio
from typing import Dict, Any, Callable
from core.vision.cortex import VisualCortex
from core.memory.core.synaptic_bus import SynapticBus, MessageType, Priority

class HiveVisionConnector:
    """
    Conecta Visual Cortex con Neural Hive.
    Permite que la colmena "vea" el código.
    """
    
    def __init__(self, cortex: VisualCortex, hive_bus: SynapticBus):
        self.cortex = cortex
        self.hive_bus = hive_bus
        self.subscribers = []
        
        # Registrar queries que la colmena puede hacer
        self.query_handlers = {
            'impact_analysis': self.handle_impact_query,
            'find_definition': self.handle_definition_query,
            'detect_smells': self.handle_smell_query,
            'suggest_refactor': self.handle_refactor_suggestion
        }
    
    async def start(self):
        """Inicia el conector y suscribe a eventos"""
        # Suscribir a queries de la colmena
        self.hive_bus.subscribe(
            MessageType.QUERY, 
            self._on_hive_query
        )
        
        # Suscribir a acciones (para actualizar grafo)
        self.hive_bus.subscribe(
            MessageType.SIGNAL,
            self._on_code_change
        )
    
    def _on_hive_query(self, message: dict):
        """Maneja queries de la colmena"""
        query_type = message.get('content', {}).get('query_type')
        handler = self.query_handlers.get(query_type)
        
        if handler:
            result = handler(message['content'])
            
            # Responder a la colmena
            self.hive_bus.send(
                msg_type=MessageType.RESPONSE,
                from_brain='vision_cortex',
                to_brain=message['from_brain'],
                content=result,
                correlation_id=message['id']
            )
    
    def _on_code_change(self, message: dict):
        """Cuando la colmena modifica código, actualizar grafo"""
        content = message.get('content', {})
        
        if content.get('event') == 'file_modified':
            file_path = content.get('file')
            author = content.get('author', 'unknown')
            
            # Actualizar grafo
            self.cortex.update_file(file_path, self.cortex.project_root)
            
            # Analizar impacto
            impact = self.cortex.analyze_impact(file_path)
            
            # Notificar a toda la colmena
            self.hive_bus.send(
                msg_type=MessageType.MEMORY,
                from_brain='vision_cortex',
                to_brain=None,  # Broadcast
                content={
                    'event': 'code_graph_updated',
                    'file': file_path,
                    'author': author,
                    'impact': impact,
                    'risk_assessment': self.assess_change_risk(file_path, author)
                },
                priority=Priority.HIGH
            )
    
    def handle_impact_query(self, params: dict) -> dict:
        """Query: ¿Qué se rompe si modifico X?"""
        target = params.get('target')
        return self.cortex.analyze_impact(target)
    
    def handle_definition_query(self, params: dict) -> dict:
        """Query: ¿Dónde está definido X?"""
        symbol = params.get('symbol')
        return self.cortex.find_definition(symbol)
    
    def handle_smell_query(self, params: dict) -> dict:
        """Query: Detectar code smells"""
        path = params.get('path', '.')
        return self.cortex.detect_smells(path)
    
    def handle_refactor_suggestion(self, params: dict) -> dict:
        """Query: Sugerencias de refactorización"""
        target = params.get('target')
        return self.cortex.suggest_refactoring(target)
    
    def assess_change_risk(self, file_path: str, author: str) -> dict:
        """Evalúa el riesgo de un cambio"""
        # Usar predictor si está disponible
        file_node = self.cortex.get_file_node(file_path)
        
        if file_node and hasattr(self.cortex, 'risk_predictor'):
            prediction = self.cortex.risk_predictor.predict(file_node['id'])
            return {
                'risk_score': prediction['risk_score'],
                'complexity': prediction['features']['cyclomatic_complexity'],
                'test_coverage': prediction['features']['test_coverage']
            }
        
        return {'risk_score': 0.5, 'note': 'No predictor available'}
```

---

## 🎯 MÉTRICAS DE ÉXITO

### KPIs Técnicos

| Métrica | Línea Base | Target v2.0 |
|---------|------------|-------------|
| Cobertura de imports | 0% | 95% |
| Tiempo de query impact | N/A | <100ms |
| Precisión predictor bugs | N/A | >75% |
| Latencia WebSocket | Echo | <50ms real |
| Queries por segundo | 10 | 1000+ |

### KPIs de Negocio

| Métrica | Impacto |
|---------|---------|
| Tiempo de onboarding de agentes | -80% |
| Bugs detectados pre-commit | +300% |
| Velocidad de refactorización | +50% |
| Confianza en cambios | +40% |

---

## 🛠️ CHECKLIST DE IMPLEMENTACIÓN

### Pre-requisitos
- [ ] Backup de cortex.db existente
- [ ] Tests unitarios para funciones críticas
- [ ] Entorno de staging

### Fase 1
- [ ] Implementar ImportResolver
- [ ] Migrar schema SQL v2
- [ ] Test de resolución de imports

### Fase 2
- [ ] Crear endpoints semánticos
- [ ] Implementar impact analysis
- [ ] Agregar búsqueda semántica

### Fase 3
- [ ] Entrenar modelo de riesgo
- [ ] Implementar detección de smells
- [ ] Crear sistema de eventos

### Fase 4
- [ ] Integrar con Neural Hive
- [ ] WebSocket bidireccional
- [ ] Visualización en tiempo real

---

## 📚 RECURSOS

### Documentación
- `AUDIT_MCP_VISION_NEURONAL.md` - Auditoría completa
- `IMPLEMENTATION_ROADMAP.md` - Este documento

### Código Base
- `cortex.py` - Core actual
- `server.py` - API actual
- `schema.sql` - Schema actual

### Herramientas Recomendadas
- **AST Analysis:** `ast`, `astor`, `jedi`
- **Graph DB:** Considerar Neo4j para v3.0
- **ML:** `scikit-learn`, `pandas`
- **API:** `FastAPI`, `pydantic`

---

## ✅ SIGN-OFF

**Arquitecto:** NEXUS-7 Neural Hive  
**Fecha:** 2026-02-10  
**Status:** Aprobado para implementación  
**Prioridad:** ALTA (Bloqueante para Neural Hive v2.0)

---

*"El código que no puedes ver, no puedes entender. El código que no puedes entender, no puedes mejorar."*
