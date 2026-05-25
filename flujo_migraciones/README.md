# `Migraciones`

El presente archivo README tiene como propósito describir en términos generales el flujo de trabajo para los procesos de migración de tablas al aplicativo Júpiter.

Flujo de tareas: `import_individual` &rightarrow; `class_entities` &rightarrow; `pivot` &rightarrow; `clean_entities (automatizada)` &rightarrow; `new_vars` &rightarrow; `match` &rightarrow; `append` (opcional) &rightarrow; `registraduria` &rightarrow; `filter` &rightarrow; `export`

### `import_individual (automatizada)`
