#skill generator

## Descripción

Esta skill es utilizada para generar skills usando la estructura oficial de skills de antigravity 

## Como Crear habilidades 
La creación de una habilidad en Antigravity sigue una estructura de directorio y un formato de archivo específicos. Esta estandarización garantiza que las habilidades sean portátiles y que el agente pueda analizarlas y ejecutarlas de manera confiable. El diseño es intencionalmente simple y se basa en formatos ampliamente conocidos, como Markdown y YAML, lo que reduce la barrera de entrada para los desarrolladores que desean ampliar las capacidades de su IDE.

Estructura de directorios
Las habilidades se pueden definir en dos permisos, lo que permite personalizaciones específicas del proyecto y del usuario :

Alcance del espacio de trabajo: Se encuentra en <workspace-root>/.agent/skills/. Estas habilidades solo están disponibles dentro del proyecto específico. Esto es ideal para secuencias de comandos específicas del proyecto, como la implementación en un entorno específico, la administración de bases de datos para esa app o la generación de código estándar para un framework propietario.
Alcance global: Se encuentra en ~/.gemini/antigravity/skills/. Estas habilidades están disponibles en todos los proyectos de la máquina del usuario. Esto es adecuado para utilidades generales, como "Formatear JSON", "Generar UUID", "Revisar el estilo de código" o la integración con herramientas de productividad personal.
Un directorio de Skill típico se ve de la siguiente manera:


my-skill/
├── SKILL.md # The definition file
├── scripts/ # [Optional] Python, Bash, or Node scripts
     ├── run.py
     └── util.sh
├── references/ # [Optional] Documentation or templates
     └── api-docs.md
└── assets/ # [Optional] Static assets (images, logos)
Esta estructura separa las preocupaciones de manera eficaz. La lógica (scripts) se separa de la instrucción (SKILL.md) y el conocimiento (references), lo que refleja las prácticas estándar de ingeniería de software.

El archivo de definición SKILL.md
El archivo SKILL.md es el cerebro de la Skill. Le indica al agente qué es la habilidad, cuándo usarla y cómo ejecutarla.

Está compuesto por dos partes:

Frontmatter de YAML
Cuerpo en Markdown.
YAML Frontmatter

Esta es la capa de metadatos. Es la única parte de la habilidad que indexa el enrutador de alto nivel del agente. Cuando un usuario envía una instrucción, el agente la compara semánticamente con los campos de descripción de todas las habilidades disponibles.


---
name: database-inspector
description: Use this skill when the user asks to query the database, check table schemas, or inspect user data in the local PostgreSQL instance.
---
Campos clave:

name: Este campo no es obligatorio. Debe ser único dentro del alcance. Se permiten letras minúsculas y guiones (p.ej., postgres-query, pr-reviewer). Si no se proporciona, se usará el nombre del directorio de forma predeterminada.
description: Este campo es obligatorio y el más importante. Funciona como la "frase de activación". Debe ser lo suficientemente descriptiva para que el LLM reconozca la relevancia semántica. Una descripción vaga, como "Herramientas de base de datos", no es suficiente. Una descripción precisa, como "Ejecuta consultas de SQL de solo lectura en la base de datos local de PostgreSQL para recuperar datos del usuario o de la transacción. Use this for debugging data states" garantiza que la skill se detecte correctamente.
El cuerpo de Markdown

El cuerpo contiene las instrucciones. Esto es "ingeniería de instrucciones" que se persiste en un archivo. Cuando se activa la skill, este contenido se inserta en la ventana de contexto del agente.

El cuerpo debe incluir lo siguiente:

Objetivo: Una declaración clara de lo que logra la habilidad.
Instrucciones: Lógica paso a paso.
Ejemplos: Son ejemplos de pocas tomas de entradas y salidas para guiar el rendimiento del modelo.
Restricciones: Reglas de "no" (p.ej., "No ejecutes consultas DELETE").
Ejemplo de cuerpo de SKILL.md:


Database Inspector

Goal
To safely query the local database and provide insights on the current data state.

Instructions
- Analyze the user's natural language request to understand the data need.
- Formulate a valid SQL query.
 - CRITICAL: Only SELECT statements are allowed.
- Use the script scripts/query_runner.py to execute the SQL.
 - Command: python scripts/query_runner.py "SELECT * FROM..."
- Present the results in a Markdown table.

Constraints
- Never output raw user passwords or API keys.
- If the query returns > 50 rows, summarize the data instead of listing it all.
Integración de secuencias de comandos
Una de las funciones más potentes de las Skills es la capacidad de delegar la ejecución en secuencias de comandos. Esto permite que el agente realice acciones que son difíciles o imposibles de hacer directamente para un LLM (como la ejecución binaria, el cálculo matemático complejo o la interacción con sistemas heredados).

Las secuencias de comandos se colocan en el subdirectorio scripts/. El SKILL.md hace referencia a ellos por ruta de acceso relativa.
5. Habilidades de creación
El objetivo de esta sección es desarrollar Skills que se integren en Antigravity y muestren progresivamente varias funciones, como recursos, secuencias de comandos, etcétera.

Puedes descargar las Skills desde el repo de GitHub aquí: https://github.com/rominirani/antigravity-skills.

Podemos considerar colocar cada una de estas habilidades dentro de la carpeta ~/.gemini/antigravity/skills o la carpeta /.agent/skills.

Nivel 1 : El router básico ( git-commit-formatter )
Consideremos esto como el "Hola mundo" de las Skills.

Los desarrolladores suelen escribir mensajes de confirmación vagos, p.ej., "wip", "fix bug", "updates". Aplicar "Conventional Commits" de forma manual es tedioso y, a menudo, se olvida. Implementemos una habilidad que aplique la especificación de Conventional Commits. Con solo indicarle al agente las reglas, le permitimos actuar como ejecutor.


git-commit-formatter/
└── SKILL.md  (Instructions only)
A continuación, se muestra el archivo SKILL.md:


---
name: git-commit-formatter
description: Formats git commit messages according to Conventional Commits specification. Use this when the user asks to commit changes or write a commit message.
---

Git Commit Formatter Skill

When writing a git commit message, you MUST follow the Conventional Commits specification.

Format
`<type>[optional scope]: <description>`

Allowed Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation

Instructions
1. Analyze the changes to determine the primary `type`.
2. Identify the `scope` if applicable (e.g., specific component or file).
3. Write a concise `description` in an imperative mood (e.g., "add feature" not "added feature").
4. If there are breaking changes, add a footer starting with `BREAKING CHANGE:`.

Example
`feat(auth): implement login with google`
Cómo ejecutar este ejemplo:

Realiza un pequeño cambio en cualquier archivo de tu espacio de trabajo.
Abre el chat y escribe: Confirma estos cambios.
El agente no solo ejecutará git commit. Primero, activará la habilidad git-commit-formatter.
Resultado: Se propondrá un mensaje de confirmación de Git convencional.
Por ejemplo, le pedí a Antigravity que agregara algunos comentarios a un archivo de Python de muestra y terminó con un mensaje de confirmación de Git como docs: add detailed comments to demo_primes.py..

Nivel 2: Utilización de recursos (license-header-adder)
Este es el patrón "Referencia".

Es posible que cada archivo fuente de un proyecto corporativo necesite un encabezado específico de 20 líneas de la licencia Apache 2.0. Es un desperdicio colocar este texto estático directamente en la instrucción (o SKILL.md). Consume tokens cada vez que se indexa la habilidad, y el modelo podría "alucinar" errores tipográficos en el texto legal.

Descarga el texto estático en un archivo de texto sin formato en una carpeta resources/. La habilidad le indica al agente que lea este archivo solo cuando sea necesario.


license-header-adder/
├── SKILL.md
└── resources/
   └── HEADER_TEMPLATE.txt  (The heavy text)
A continuación, se muestra el archivo SKILL.md:


---
name: license-header-adder
description: Adds the standard open-source license header to new source files. Use involves creating new code files that require copyright attribution.
---

# License Header Adder Skill

This skill ensures that all new source files have the correct copyright header.

## Instructions

1. **Read the Template**:
  First, read the content of the header template file located at `resources/HEADER_TEMPLATE.txt`.

2. **Prepend to File**:
  When creating a new file (e.g., `.py`, `.java`, `.js`, `.ts`, `.go`), prepend the `target_file` content with the template content.

3. **Modify Comment Syntax**:
  - For C-style languages (Java, JS, TS, C++), keep the `/* ... */` block as is.
  - For Python, Shell, or YAML, convert the block to use `#` comments.
  - For HTML/XML, use `<!-- ... -->`.
Cómo ejecutar este ejemplo:

Crea un nuevo archivo de Python ficticio: touch my_script.py
Tipo: Add the license header to my_script.py.
El agente leerá license-header-adder/resources/HEADER_TEMPLATE.txt.
Se pegará el contenido exactamente, palabra por palabra, en tu archivo.
Nivel 3: Aprendizaje con ejemplos (json-to-pydantic)
El patrón "Few-Shot".

Convertir datos flexibles (como una respuesta de la API de JSON) en código estricto (como modelos de Pydantic) implica docenas de decisiones. ¿Cómo debemos nombrar las clases? ¿Deberíamos usar Optional? ¿snake_case o camelCase? Escribir estas 50 reglas en inglés es tedioso y propenso a errores.

Los LLM son motores de coincidencia de patrones.

Mostrarles un ejemplo excelente (Input -> Output) suele ser más eficaz que dar instrucciones detalladas.


json-to-pydantic/
├── SKILL.md
└── examples/
   ├── input_data.json   (The Before State)
   └── output_model.py   (The After State)
A continuación, se muestra el archivo SKILL.md:


---
name: json-to-pydantic
description: Converts JSON data snippets into Python Pydantic data models.
---

# JSON to Pydantic Skill

This skill helps convert raw JSON data or API responses into structured, strongly-typed Python classes using Pydantic.

Instructions

1. **Analyze the Input**: Look at the JSON object provided by the user.
2. **Infer Types**:
  - `string` -> `str`
  - `number` -> `int` or `float`
  - `boolean` -> `bool`
  - `array` -> `List[Type]`
  - `null` -> `Optional[Type]`
  - Nested Objects -> Create a separate sub-class.
 
3. **Follow the Example**:
  Review `examples/` to see how to structure the output code. notice how nested dictionaries like `preferences` are extracted into their own class.
 
  - Input: `examples/input_data.json`
  - Output: `examples/output_model.py`

Style Guidelines
- Use `PascalCase` for class names.
- Use type hints (`List`, `Optional`) from `typing` module.
- If a field can be missing or null, default it to `None`.
En la carpeta /examples, se encuentran el archivo JSON y el archivo de salida, es decir, el archivo de Python. Ambos se muestran a continuación:

input_data.json


{
   "user_id": 12345,
   "username": "jdoe_88",
   "is_active": true,
   "preferences": {
       "theme": "dark",
       "notifications": [
           "email",
           "push"
       ]
   },
   "last_login": "2024-03-15T10:30:00Z",
   "meta_tags": null
}
output_model.py


from pydantic import BaseModel, Field
from typing import List, Optional

class Preferences(BaseModel):
   theme: str
   notifications: List[str]

class User(BaseModel):
   user_id: int
   username: str
   is_active: bool
   preferences: Preferences
   last_login: Optional[str] = None
   meta_tags: Optional[List[str]] = None
Cómo ejecutar este ejemplo:

Proporciona al agente un fragmento de código JSON (pégalo en el chat o indícale un archivo).
{ "product": "Widget", "cost": 10.99, "stock": null }

Tipo: Convert this JSON to a Pydantic model.
El agente analiza el par examples en la carpeta de la habilidad.
Genera una clase de Python que imita a la perfección el estilo de codificación, las importaciones y la estructura de output_model.py, incluido el control del stock nulo como opcional.
A continuación, se muestra un ejemplo de resultado (product_model.py):


from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
   product: str
   cost: float
   stock: Optional[int] = None
Nivel 4: Lógica procedimental (database-schema-validator)
Este es el patrón de "Uso de herramientas".

Si le preguntas a un LLM: "¿Este esquema es seguro?", es posible que te diga que todo está bien, incluso si falta una clave principal crítica, simplemente porque el código SQL parece correcto.

Deleguemos esta verificación a un script determinístico. Usamos la habilidad para enrutar el agente y ejecutar una secuencia de comandos de Python que escribimos. La secuencia de comandos proporciona una verdad binaria (verdadero/falso).


database-schema-validator/
├── SKILL.md
└── scripts/
   └── validate_schema.py  (The Validator)
A continuación, se muestra el archivo SKILL.md:


---
name: database-schema-validator
description: Validates SQL schema files for compliance with internal safety and naming policies.
---

# Database Schema Validator Skill

This skill ensures that all SQL files provided by the user comply with our strict database standards.

Policies Enforced
1. **Safety**: No `DROP TABLE` statements.
2. **Naming**: All tables must use `snake_case`.
3. **Structure**: Every table must have an `id` column as PRIMARY KEY.

Instructions

1. **Do not read the file manually** to check for errors. The rules are complex and easily missed by eye.
2. **Run the Validation Script**:
  Use the `run_command` tool to execute the python script provided in the `scripts/` folder against the user's file.
 
  `python scripts/validate_schema.py <path_to_user_file>`

3. **Interpret Output**:
  - If the script returns **exit code 0**: Tell the user the schema looks good.
  - If the script returns **exit code 1**: Report the specific error messages printed by the script to the user and suggest fixes.
A continuación, se muestra el archivo validate_schema.py:


import sys
import re

def validate_schema(filename):
   """
   Validates a SQL schema file against internal policy:
   1. Table names must be snake_case.
   2. Every table must have a primary key named 'id'.
   3. No 'DROP TABLE' statements allowed (safety).
   """
   try:
       with open(filename, 'r') as f:
           content = f.read()
          
       lines = content.split('\n')
       errors = []
      
       # Check 1: No DROP TABLE
       if re.search(r'DROP TABLE', content, re.IGNORECASE):
           errors.append("ERROR: 'DROP TABLE' statements are forbidden.")
          
       # Check 2 & 3: CREATE TABLE checks
       table_defs = re.finditer(r'CREATE TABLE\s+(?P<name>\w+)\s*\((?P<body>.*?)\);', content, re.DOTALL | re.IGNORECASE)
      
       for match in table_defs:
           table_name = match.group('name')
           body = match.group('body')
          
           # Snake case check
           if not re.match(r'^[a-z][a-z0-9_]*$', table_name):
               errors.append(f"ERROR: Table '{table_name}' must be snake_case.")
              
           # Primary key check
           if not re.search(r'\bid\b.*PRIMARY KEY', body, re.IGNORECASE):
               errors.append(f"ERROR: Table '{table_name}' is missing a primary key named 'id'.")

       if errors:
           for err in errors:
               print(err)
           sys.exit(1)
       else:
           print("Schema validation passed.")
           sys.exit(0)
          
   except FileNotFoundError:
       print(f"Error: File '{filename}' not found.")
       sys.exit(1)

if __name__ == "__main__":
   if len(sys.argv) != 2:
       print("Usage: python validate_schema.py <schema_file>")
       sys.exit(1)
      
   validate_schema(sys.argv[1])
Cómo ejecutar este ejemplo:

Crea un archivo SQL incorrecto bad_schema.sql: CREATE TABLE users (name TEXT);
Tipo: Validate bad_schema.sql.
El agente no adivina. Se invocará la secuencia de comandos, que fallará (código de salida 1) y nos informará que "La validación falló porque falta una clave principal en la tabla ‘users’".
Nivel 5: El arquitecto (adk-tool-scaffold)
Este patrón abarca la mayoría de las funciones disponibles en las Skills.

Las tareas complejas suelen requerir una secuencia de operaciones que combinan todo lo que vimos: crear archivos, seguir plantillas y escribir lógica. Para crear una herramienta nueva para el ADK (Kit de desarrollo de agentes), se requiere todo lo anterior.

Combinamos lo siguiente:

Secuencia de comandos (para controlar la creación y la estructura del archivo)
Plantilla (para controlar el texto estándar en los recursos)
Un ejemplo (para guiar la generación de lógica).

adk-tool-scaffold/
├── SKILL.md
├── resources/
│   └── ToolTemplate.py.hbs (Jinja2 Template)
├── scripts/
│   └── scaffold_tool.py    (Generator Script)
└── examples/
    └── WeatherTool.py      (Reference Implementation)
El archivo SKILL.md se muestra a continuación. Puedes consultar el repositorio de habilidades para verificar los archivos en las carpetas de secuencias de comandos, recursos y ejemplos. Para esta habilidad específica, ve a la habilidad adk-tool-scaffold.


---
name: adk-tool-scaffold
description: Scaffolds a new custom Tool class for the Agent Development Kit (ADK).
---

# ADK Tool Scaffold Skill

This skill automates the creation of standard `BaseTool` implementations for the Agent Development Kit.

Instructions

1. **Identify the Tool Name**:
  Extract the name of the tool the user wants to build (e.g., "StockPrice", "EmailSender").
 
2. **Review the Example**:
  Check `examples/WeatherTool.py` to understand the expected structure of an ADK tool (imports, inheritance, schema).

3. **Run the Scaffolder**:
  Execute the python script to generate the initial file.
 
  `python scripts/scaffold_tool.py <ToolName>`

4. **Refine**:
  After generation, you must edit the file to:
  - Update the `execute` method with real logic.
  - Define the JSON schema in `get_schema`.
 
Example Usage
User: "Create a tool to search Wikipedia."
Agent:
1. Runs `python scripts/scaffold_tool.py WikipediaSearch`
2. Editing `WikipediaSearchTool.py` to add the `requests` logic and `query` argument schema.
Cómo ejecutar este ejemplo:

Tipo: Create a new ADK tool called StockPrice to fetch data from an API.
Paso 1 (estructura): El agente ejecuta la secuencia de comandos de Python. Esto crea al instante StockPriceTool.py con la estructura de clase, las importaciones y el nombre de clase StockPriceTool correctos.
Paso 2 (implementación): El agente "lee" el archivo que acaba de crear. Ve # TODO: Implement logic.
Paso 3 (orientación): No se sabe con certeza cómo definir el esquema JSON para los argumentos de la herramienta. Verifica examples/WeatherTool.py.
Completado: Edita el archivo para agregar requests.get(...) y define el argumento del ticker en el esquema, de modo que coincida exactamente con el estilo del ADK.