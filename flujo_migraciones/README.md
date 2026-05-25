# `Migraciones`

El presente archivo README tiene como propósito describir en términos generales el flujo de trabajo para los procesos de migración de tablas al aplicativo Júpiter.

Flujo de tareas: `import_individual` &rightarrow; `class_entities` &rightarrow; `pivot` &rightarrow; `clean_entities` &rightarrow; `new_vars` &rightarrow; `match` &rightarrow; `append` (opcional) &rightarrow; `registraduria` &rightarrow; `filter` &rightarrow; `export`

### `import_individual (automatizada)`

Corresponde a la primera tarea del flujo. Esta tarea tiene como propósito juntar las salidas de varias tareas del flujo de individual a fin de traer la totalidad de variables originales de la tabla aun cuando estas no se incluyan en el input-records. Asimismo, también se busca traer las variables que se homologan y estandarizan en individual, puesto que estas variables se incluyen dentro del conjunto de campos del aplicativo Júpiter.

Se procede a traer las salidas de `registraduría`, los archivos -canon de `canonicalize` y la salidas de `pivot` o `clean` dependiendo de cuál de estas sea vaya después en flujo de la tabla a migrar.

Una vez se trae la totalidad de salidas de las tareas anteriormente descritas, se consolida una tabla única la cual contendría las variables originales de la tabla así como las columnas que fueron procesadas en el flujo.

### `class_entities (automatizada)`

Esta tarea busca clasificar el tipo de registro en términos del tipo de entidad al que refiere.

En primer lugar, se procede a cargar la tabla producto de la tarea anterior y se trae el archivo `class_recs` de la tarea `filter` de `individual` a fin de identificar los tipos de entidad que no corresponden a personas naturales o que no cuentan con información suficiente como para ingresar al flujo de `match`.

En segundo lugar, se procede con la unión de tablas de forma lateral (left_join) a fin de traer la variable tipo_registro del archivo class_recs. En este punto, se asume que todo aquel registro lo que no cruce con la tabla de class_recs, corresponde a una persona natural.

Por último, se realiza el cálculo del exact_id para la totalidad de registros de la tabla. La generación de este código hash tendrá en cuenta -entre otras- la variable de tipo_registro.


