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

### `pivot (semi-automatizada)`

La tarea pivot tiene por objeto llevar la tabla objeto de migración al formato tidy-data, esto es: a) cada variable forma una columna, b) cada observación constituye una fila y c) cada valor es una celda. Filas, columnas y celdas deben referir a un único objeto en el mundo o a una única carácterística de ese objeto.

En este mismo sentido, una de las características del formato de destino del aplicativo Júpiter es que los grupos armados colectivamente considerados son en sí mismos entidades y por tanto se deben crear nuevos registros para ellos. Por consiguiente, el vínculo entre víctimas y grupos armados -en tanto perpetrador colectivo- se establece a partir de los identificadores del hecho los cuáles se generan en una tarea posterior.

En términos operativos, la tarea se divide en dos scripts. Ambos scripts son opcionales. Si la tabla a migrar posee información a ser pivoteada, se realizará en la presente tarea y no en ninguna otra.

El primer script debe contener todos los ejercicios de pivoteo a excepción del pivoteo de grupos armados que derivan en nuevas entidades. El segundo script, por su parte, automatiza el pivoteo de grupos armados colectivamente considerados a fin de convertirlos en nuevas entidades.

La salida de la presente tarea debe satisfacer las siguientes aserciones:

- Se debe exportar un archivo llamado cross_walk en formato parquet.
- El archivo cross_walk debe contener dos columnas llamadas old_recordid, para referirse al `recordid` anterior y una columna `new_recordid` la cual contiene los recordid que se acaban de generar.
- Los recordid de la salida de class_entities deben ser equivalentes a la columna old_recodid del archivo cross_walk.
- Deben estar presentes la totalidad de columnas de los archivos `-canon`, a saber:

Posteriormente, el test_pivot.R verificara cada una de las anteriores aseciones. Este script deberá llamarse al final de la tarea pivot.

### `clean_entities (automatizada)`

Esta tarea se dirige a limpiar los valores y registros en relación con el tipo de entidad al que refieren. En síntesis, la presente tarea realiza las siguientes operaciones:

- Se almacena el tipo_registro original
- Se homologan entidades NN y ALIAS como personas naturales
- Se homologan los tipo_registro que refieren a COMUNIDADES INDIGENAS y COMUNIDADES AFROCOLOMBIANAS a CAMUNIDADES ETNICAS.
- Se filtran todos los registros que no refieren PERSONAS JURÍDICAS, COMUNICADES ETNICAS, GRUPOS ARMADOS Y PERSONAS NATURALES. Los registros filtrados se almacenarán en el archivo filteres_records.parquet.
- Se convierte a NA todos los valores de las variables que no corresponden al tipo de entidad en cada caso. Así, por ejemplo, variables de sexo, edad, municipio de nacimiento deberían estar en NA para entidades que no son personas naturales.

### `new vars`

En esta tarea se procede con la creación, estandarización y homologación de los campos que se requieren para ser cargados al aplicativo Júpiter. Estos campos se clasifican en campos que refieren a la a) entidad, b) al hecho y c) a la informaciónde la entidad al momento de los hechos.

Esta tarea requiere de la elaboración de tres scripts los cuales llevan las columnas "e_", "h_" e "i_" al formato requerido por Júpiter para la migración. Las salidas de la presente tarea son 3 archivos en formato parquet que deben contener los tres tipos de información anteriormente descritos. Cada uno de estos archivos debe conservar la columna `recordid` a fin de guardar las relaciones con las otras dos tablas. Estos archivos deben poseer el prefijo "e_", "h_" e "i_" a fin de permitir que sean importados por el test de new_vars.

A continuación, se presenta una breve lista de las campos que deben estar presentes en cada una de las tablas:

- asd
- asd











