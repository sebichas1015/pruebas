# `Migraciones`

El presente archivo README tiene como propósito describir en términos generales el flujo de trabajo para los procesos de migración de tablas al aplicativo Júpiter.

Flujo de tareas:

`import_individual` &rightarrow; `class_entities` &rightarrow; `pivot` &rightarrow; `new_vars` &rightarrow; `table_sources` &rightarrow; `match` &rightarrow; `gen_ids` &rightarrow; `clean_entities` &rightarrow;   `merge_values` &rightarrow; `append` &rightarrow; `homl_validate`


### `1. import_individual (automatizada)`

Corresponde a la primera tarea del flujo. Esta tarea tiene como propósito juntar las salidas de varias tareas del flujo de individual a fin de traer la totalidad de variables originales de la tabla aun cuando estas no se incluyan en el input-records. Asimismo, también se busca traer las variables que se homologan y estandarizan en individual, puesto que estas variables se incluyen dentro del conjunto de campos del aplicativo Júpiter.

Se procede a traer las salidas de `registraduría`, los archivos -canon de `canonicalize` y la salidas de `pivot` o `clean` dependiendo de cuál de estas sea vaya después en flujo de la tabla a migrar.

Una vez se trae la totalidad de salidas de las tareas anteriormente descritas, se consolida una tabla única la cual contendrá las variables originales de la tabla así como las columnas que fueron procesadas en el flujo.

### `2. class_entities (automatizada)`

Esta tarea busca clasificar el tipo de registro en términos del tipo de entidad al que refiere.

En primer lugar, se procede a cargar la tabla producto de la tarea anterior y se trae el archivo `class_recs` de la tarea `filter` de `individual` a fin de identificar los tipos de entidad que no corresponden a personas naturales o que no cuentan con información suficiente como para ingresar al flujo de `match`.

En segundo lugar, se procede con la unión de tablas de forma lateral (left_join) a fin de traer la variable tipo_registro del archivo `class_recs`. En este punto, se asume que todo aquel registro lo que no cruce con la tabla de `class_recs`, corresponde a una persona natural.

### `3. pivot (semi-automatizada)`

`pivot` &rightarrow; `pivot_actor`

La tarea pivot tiene por objeto llevar la tabla objeto de migración al formato tidy-data, esto es: a) cada variable forma una columna, b) cada observación constituye una fila y c) cada valor es una celda. Filas, columnas y celdas deben referir a un único objeto en el mundo o a una única carácterística de ese objeto.

En este mismo sentido, una de las características del formato de destino del aplicativo Júpiter es que los grupos armados colectivamente considerados son en sí mismos entidades y por tanto se deben crear nuevos registros para ellos. Por consiguiente, el vínculo entre víctimas y grupos armados -en tanto perpetrador colectivo- se establece a partir de los identificadores del hecho los cuáles se generan en una tarea posterior.

En términos operativos, la tarea se divide en dos scripts. El primer de ellos es opcional y el segundo es obligatorio. Si la tabla a migrar posee información a ser pivoteada, se realizará en la presente tarea y no en ninguna otra.

El primer script debe contener todos los ejercicios de pivoteo a excepción del pivoteo de grupos armados que derivan en nuevas entidades. El segundo script, por su parte, automatiza el pivoteo de grupos armados colectivamente considerados a fin de convertirlos en nuevas entidades.

La salida de la presente tarea debe satisfacer las siguientes aserciones:

- Se debe exportar un archivo llamado cross_walk en formato parquet.
- El archivo cross_walk debe contener dos columnas llamadas old_recordid, para referirse al `recordid` anterior y una columna `new_recordid` la cual contiene los recordid que se acaban de generar.
- Los recordid de la salida de class_entities deben ser equivalentes a la columna old_recodid del archivo cross_walk.
- Deben estar presentes la totalidad de columnas de los archivos `-canon`, a saber:

Posteriormente, el test_pivot.R verificara cada una de las anteriores aseciones. Este script deberá llamarse al final de la tarea pivot.

### `5. new_vars`

En esta tarea se procede con la creación, estandarización y homologación de los campos que se requieren para ser cargados al aplicativo Júpiter. Estos campos se clasifican en campos que refieren a la a) entidad, b) al hecho y c) a la información de la entidad al momento de los hechos. Estos campos reciben los prefijos "e_", "h_" e "i_", respectivamente. Esta distinción es clave toda vez que permite diferenciar conceptualmente los mismos atributos para contextos diferentes. Así, por ejemplo, permiten diferenciar la pertenencia étnica de la entidad (e_pertenencia_etnica) en contraste con los atributos étnicos del lugar del hecho (h_pertenencia_etnica). 

Esta tarea requiere de la elaboración de tres scripts los cuales llevan las columnas "e_", "h_" e "i_" al formato requerido por Júpiter para la migración. Las salidas de la presente tarea son 3 archivos en formato parquet que deben contener los tres tipos de información anteriormente descritos. Cada uno de estos archivos debe conservar la columna `recordid` a fin de guardar las relaciones con las otras dos tablas. Estos archivos deben poseer el prefijo "e_", "h_" e "i_" a fin de permitir que sean importados por el test de new_vars.

A fin de brindar una lista y descripción de cada uno de los campos de Júpiter, consultar el `Diccionario_Migracion_MC`. Este archivo describe cada campo en términos del tipo de variable que debe recibir, su longitud máxima, su correspondiente catálogo de valores válidos, si se trata de un campo obligatorio, observaciones (explicaciones adicionales para facilitar la comprensión del campo), la sección del aplicativo dónde se aloja el campo, y el nombre exacto que recibe en el aplicativo.

Asimismo, en la ruta `$(HERE)/migraciones/share/new_work_flow/new_vars/` se encuentran los archivos `vars_h.yaml`, `vars_e.yaml` y `vars_i.yaml`, los cuáles contienen la totalidad de variables para las variables del hecho, de la entidad y de la entidad al momento de los hechos, respectivamente. Estos archivos ilustran la forma “limpia” de los nombres de los campos de Júpiter. Posteriormente, en la tarea `homl_validate`, los nombres de las variables se homologarán automáticamente.


### `6. match (Semi-automatizada)`

`fastlink` &rightarrow; `extract_components`

Esta tarea tiene como propósito realizar la vinculación de registros que pertenecen a una misma entidad persona natural. El producto concreto de esta tarea es un identificador de personas únicas que se relaciona con todos los registros que refieren a la misma persona natural.

Esta tarea se compone de los scripts fastlink y extract_components. Mientras que el primero genera los pares a etiquetar y presenta métricas de similitud, el segundo se ocupa de la transitividad para las componentes conectadas.

La tarea de match, a su vez, se subdivide en tres tareas. En lo que sige, se presenta una breve descripción de cada una de ellas.

#### `6.1 fastlink.R (automatizada)`

se realiza con la tabla eque refiere a la información de la entidad (e_) posterior a filtrar las peronas naturales que persistieron en el flujo de `individual` hasta `export`. A continuación, se presenta una breve descripción de esta tarea.

En primer lugar, se procede a calcular el exact_id con las columnas (...), las cuales permiten realizar una primera agrupación de registros que se considera pertenecen a la misma entidad personal natural. Posteriormente, se procede a eliminar registros duplicados por exact_id a fin de reducir la cantidad de comparaciones que -en la siguiente subtarea- ingresan al proceso manual de etiquetado. En tercer lugar, se realiza un fastlink a partir de las siguientes variables de identificación de personas naturales: (...). Finalmente, se genera una tabla por pares de registros para ser etiquetados toda vez que se considere que refieren a la misma persona. Si bien el fastlik brinda unas métricas s similitud a fin de facilitar el ejercicio, la decisión final es discrecional para cada analista.

#### `6.2 etiquetado manual de pares`

Esta tarea se realiza sobre el archivo de pares de registros generado en la tarea anterior. La tarea consiste en analizar los pares de registros a la luz de las variables anteriormente descritas y tomar una decisión sobre si ambos registros refieren a la misma persona o si se trata de personas diferentes. En términos operativos, para esta tarea se debe crear una columna columna llamada match y asignarle 0 en caso de que se considere que no es un par positvo, o asignar 1 si se considera que sí se trata de pares positivos y que por tanto que los registros refieren a la misma entidad.

Por último, el archivo etiquetado se debe cargar en una carpeta hand dentro de la carpeta `fastlik`.

NOTA IMPORTANTE: Bajo ningún motivo se deben subir al repositorio de github registros con información de entidades o hechos sensibles. De manera que, al subir el archivo a la carpeta `hand`, se deben eliminar todas las columnas menos los identificadores y el campo de las eiquetas.

#### `6.3 extract_components.R (automatizada)`

Esta tercera tarea de match tiene como propósito identificar la totalidad de registros que deberían asociarse bajo un mismo `match_group_id`. En la tarea anterior se identificaron pares de registros que deberían vincularse. No obstante, se suele dar el caso que, por ejmplo, A y B fueron etiquetados como pertenencientes a una misma entidad. Asimismo, B y C se etiqueraon como pertenecientes a una misma entidad. Pero nunca se dio la comparación entre A y C. El presente registro realiza ese vínculo de registros bajo la premisa de que si A = B y B = C, entonces A = C.

El resultado final de esta subtarea es un archivo que contienen una columna de `exact_id` y los `match_group_id` que los agrupan.

### `7. gen_ids (automatizada)`

Se procede con la generación de identificadores de hechos, entidades y entidades al momento del hecho. Se recupera el identificador generado en match y se generan los nuevos identificadores aprovechando la información sub-municipal.

Como lo indica su nombre, esta tarea se encarga de generar los identificadores de hechos, entidades y entidades al momento de los hechos para las tablas e_, h_, i_. En este apartado se describe como se genera el código hash en cada caso.

En primer lugar, para el caso de las entidades (e_), se procede a realizar un cálculo atendiendo al tipo de entidad en cada caso. Para las entidades GRUPO ARMADO, se realiza un cálculo basado en las columnas `e_actor`, `e_grupo`, `e_estructura_nivel_1`,  `e_estructura_nivel_2`, `e_estructura_nivel_3`, `e_estructura_nivel_4`, las cuáles permiten identificar e individualizar a los grupos armados.

En línea con lo anterior, el cálculo del identificador de entidades COMUNIDADES ETNICAS se genera atendiendo a las columnas `e_tipo_entidad`, `e_pertenencia_etnica`, `e_comunidad_etnica`, `e_territorio_colectivo`, `e_nombre_comunidad_etnica`, a fin de crear entidades con base en la coincidencia de campos que refieren a las cacterísticas étnicas de la entidad.

Las entidades PERSONA JUÍRICA reciben un trato similar, en tanto que su identificador se construye a partir de las columnas `e_razon_social` y `e_nit`.

En el caso de las personas naturales, se establecen dos reglas. La primera es recuperar los mgis de la salida de `extract_components`. La segunda regla es que, para todas las demas entidades PERSONA NATURAL, se procede a asignarle el exact_id anteriormente calculado.

El tratamiento de hechos sigue una lógica similar. El identificador de hechos únicos se genera a partir de la coincidencia de` h_tipo_hecho`, `h_fecha_inicial`, `h_fecha_final`, `h_departamento`, `h_ciudad`, `h_centro_poblado`, `h_vereda`, esto es, se identifican hechos a partir de las variables del qué, cuando y dónde. Adicional a esto último, el código admite adicionar alguna otra variable que permita mejorar la agrupación de registros al momento de identificar hechos únicos. En caso de contar con un identificador de hechos original de la tabla, el makefile permite adicionarlo como un argumento que se adicionaría a las variables mencionadas.

Finalmente, el identificador de la información al momento de los hechos se genera como una combinación entre hechos y entidades. Es importante mencionar que a los hechos sin entidades o a las entidades sin hechos se les asignará un "0" en su identificador con objeto de evitar su migración a Júpiter.

### `4. clean_entities (automatizada)`

Esta tarea se dirige a limpiar los valores y registros en relación con el tipo de entidad al que refieren. En síntesis, la presente tarea realiza las siguientes operaciones:

- Se almacena el tipo_registro original
- Se homologan entidades NN y ALIAS como personas naturales
- Se homologan los tipo_registro que refieren a COMUNIDADES INDIGENAS y COMUNIDADES AFROCOLOMBIANAS a COMUNIDADES ETNICAS.
- Se filtran todos los registros que no refieren PERSONAS JURÍDICAS, COMUNIDADES ETNICAS, GRUPOS ARMADOS Y PERSONAS NATURALES. Los registros filtrados se almacenarán en el archivo filteres_records.parquet.
- Se convierte a NA todos los valores de las variables que no corresponden al tipo de entidad en cada caso. Así, por ejemplo, variables de sexo, edad, municipio de nacimiento deberían estar en NA para entidades que no son personas naturales.

### `8. merge_values`

Una vez se generaron los identificadores, se procede a llevar cada tabla a una distribución de 1 a 1 entre sus identificadores y el resto de las variables. Esto se logra a) fusionando algunos valores usando la | como delimitador, o b) eliminando registros inconsistentes que posean menos información.

Cada uno de los identificadores del hecho, las entidades y la información de las entidades al momento de los hechos (h_, e_, i_) deben estar asociados a un único valor para la totalidad de los campos de su respectiva tabla. Así, por ejemplo, el identificador del hecho a1 no puede estar asociado -al mismo tiempo- al municipio x1 y al municipio x2. Este tipo de casos van en contravía de la lógica diseñada para el aplicativo júpiter.

No obstante, hay información que lógicamente puede establecer una relación de uno a varios. Es el caso de la vinculación de personas naturales a procesos judiciales. Para estos casos, se propone unir las cadenas de texto y separarlas con el operador "|". En contraposición, las variables en donde relaciones de uno a muchos revelan una posible inconsistencia, reciben otro tratamiento. En estos casos se debe identificar cuál de los registros posee menos valores en NA y se procede a conservar ese registro.

### `9. append (automatizada)`

Esta última tarea tiene como propósito consolidar una tabla única al volver a juntar las tablas de hechos, entidades, e información de la entidad al momento del hecho. Asimismo, esta tarea crea un número recordid, elimina la información duplicada y exporta un archivo cross_walk a fin de no perder las relaciones con las salidas anteriores.

Al momento de verificar registros duplicados, el código también identifica si existen perpetradores cuyo tipo de entidad es `PERSONA NATURAL`, los hechos asociados a estos últimos y -en los casos en los que aplica- elimina las entidades `GRUPO ARMADO` que comparten los mismos valores en los campos jerárquicos relativos a la estructura armada.

Adicionalmente, la tarea realiza mútiples verificaciones orientadas a validar la consistencia de la tabla con los supuestos que deben serguirse para ser migrada al aplicativo júpiter. Se procede a validar la todalidad de campos, que no se tengan valores obligatorios en NA, que los valores no sean distintos al de los diccionarios etc.

### `10 homl_validate (automatizada)`

`homl_jupiter` &rightarrow; `validacion_fuentes_mc`

`homl_jupiter` &rightarrow; `validacion_tabla_hei`

Se procede con la homologación de nombres de campos para ajustarlos a los nombres del aplicativo Júpiter y se realizan las últimas validaciones a fin de detectar cualquier tipo de novedad adicional. Es importante mencionar que esta tarea toma como input la tabla de la salida de `append` y la tabla de fuentes. Esta última corresponde a las fuentes que documentan los registros de la tabla de hechos, entidades información al momento de los hechos (hei).

La tarea se divide en 3 scripts. El primero tiene como propósito homologar los nombres de las columnas al formato del aplicativo Júpiter. El segundo script valida los campos de la tabla de fuentes a partir del diccionario de Júpiter. Esta evaluación tiene en cuenta la longitud de caracteres permitida, el tipo de variable, la existencia de campos dependientes etc. En tercer script realiza un ejercicio similar al anterior, pero aplicado a la tabla hei. El resultado de estos dos últimos scripts son tablas que idenfican los campos con inconsistencias a la vez que enuncian una breve descripción que permite proceder con los ajustes correspondientes. 












