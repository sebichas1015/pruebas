# `Migraciones`

El presente archivo README tiene como propósito describir en términos generales el flujo de trabajo para los procesos de migración de tablas al aplicativo Júpiter.

Flujo de tareas:

`import_individual` &rightarrow; `class_entities` &rightarrow; `pivot` (opcional) &rightarrow; `clean_entities` &rightarrow; `new_vars` &rightarrow; `match` &rightarrow; `gen_ids` &rightarrow; `merge_values` &rightarrow; `append`


### `1. import_individual (automatizada)`

Corresponde a la primera tarea del flujo. Esta tarea tiene como propósito juntar las salidas de varias tareas del flujo de individual a fin de traer la totalidad de variables originales de la tabla aun cuando estas no se incluyan en el input-records. Asimismo, también se busca traer las variables que se homologan y estandarizan en individual, puesto que estas variables se incluyen dentro del conjunto de campos del aplicativo Júpiter.

Se procede a traer las salidas de `registraduría`, los archivos -canon de `canonicalize` y la salidas de `pivot` o `clean` dependiendo de cuál de estas sea vaya después en flujo de la tabla a migrar.

Una vez se trae la totalidad de salidas de las tareas anteriormente descritas, se consolida una tabla única la cual contendrá las variables originales de la tabla así como las columnas que fueron procesadas en el flujo.

### `2. class_entities (automatizada)`

Esta tarea busca clasificar el tipo de registro en términos del tipo de entidad al que refiere.

En primer lugar, se procede a cargar la tabla producto de la tarea anterior y se trae el archivo `class_recs` de la tarea `filter` de `individual` a fin de identificar los tipos de entidad que no corresponden a personas naturales o que no cuentan con información suficiente como para ingresar al flujo de `match`.

En segundo lugar, se procede con la unión de tablas de forma lateral (left_join) a fin de traer la variable tipo_registro del archivo class_recs. En este punto, se asume que todo aquel registro lo que no cruce con la tabla de class_recs, corresponde a una persona natural.

### `3. pivot (semi-automatizada)`

`pivot` &rightarrow; `pivot_actor`

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

### `4. clean_entities (automatizada)`

Esta tarea se dirige a limpiar los valores y registros en relación con el tipo de entidad al que refieren. En síntesis, la presente tarea realiza las siguientes operaciones:

- Se almacena el tipo_registro original
- Se homologan entidades NN y ALIAS como personas naturales
- Se homologan los tipo_registro que refieren a COMUNIDADES INDIGENAS y COMUNIDADES AFROCOLOMBIANAS a CAMUNIDADES ETNICAS.
- Se filtran todos los registros que no refieren PERSONAS JURÍDICAS, COMUNICADES ETNICAS, GRUPOS ARMADOS Y PERSONAS NATURALES. Los registros filtrados se almacenarán en el archivo filteres_records.parquet.
- Se convierte a NA todos los valores de las variables que no corresponden al tipo de entidad en cada caso. Así, por ejemplo, variables de sexo, edad, municipio de nacimiento deberían estar en NA para entidades que no son personas naturales.

### `5. new_vars`

En esta tarea se procede con la creación, estandarización y homologación de los campos que se requieren para ser cargados al aplicativo Júpiter. Estos campos se clasifican en campos que refieren a la a) entidad, b) al hecho y c) a la informaciónde la entidad al momento de los hechos.

Esta tarea requiere de la elaboración de tres scripts los cuales llevan las columnas "e_", "h_" e "i_" al formato requerido por Júpiter para la migración. Las salidas de la presente tarea son 3 archivos en formato parquet que deben contener los tres tipos de información anteriormente descritos. Cada uno de estos archivos debe conservar la columna `recordid` a fin de guardar las relaciones con las otras dos tablas. Estos archivos deben poseer el prefijo "e_", "h_" e "i_" a fin de permitir que sean importados por el test de new_vars.

A continuación, se presenta una breve lista de las campos que deben estar presentes en cada una de las tablas que resultan de la presente tarea.

#### `5.1 Campos que refieren al hecho h_ (new_vars_h.R)`

- `h_tipo_hecho`: Tipo de violencia o conducta criminal. En la gran mayoría de los casos, se corresponde con la variable hecho_victimizante_h del flujo de individual.
- `h_conducta_penal`: Permite tipificar penalmente el hecho reportado.
- `h_categoria_conducta`: Es una desagregación de h_tipo_hecho. En la gran mayoría de los casos, se corresponde con la variable clasificacion_hecho_h del flujo de individual.
- `h_tecnica`: Tecnicas con las que se cometió el hecho reportado.
- `h_patrones`: patrones macrocriminales reportados en el marco del hecho registrado.
- `h_medios_desplegados`: Medios desplegados en el marco del hecho registrado.
- `h_es_fecha_inexacta`: Indica si la fecha registrada para el hecho es exacta o si no lo es. Es una variable binaria que asume los valores SI o NO.
- `h_fecha_inicial`: Fecha inicial en la que tuvo lugar el hecho registrado. (adicional formato).
- `h_fecha_final`: Fecha en la termina o consluye el hecho registrado. (adicionar formato)
- `h_departamento`: Departamento en el que tuvo lugar el hecho registrado.
- `h_ciudad`: Municipio en el que tuvo lugar el hecho registrado.
- `h_centro_poblado`: Centro poblado en el que tuvo lugar el hecho registrado.
- `h_commune`: Comuna en la que tuvo lugar el hecho registrado.
- `h_vereda`: Vereda en la que tuvo lugar el hecho registrado.
- `h_toponimia`: Toponimia en la que tuvo lugar le hecho registrado.
- `h_coordenada_x`: Coordenada x en la que tuvo lugar el hecho registrado.
- `h_coordenada_y`: Coordenada y en la que tuvo lugar el hecho registrado.
- `h_latitud`: Latitud en la que tuvo lugar el hecho registrado.
- `h_longitud`: Longitud en la que tuvo lugar el hecho registrado.
- `h_incluye_informacion_etnica`: Indica si el hecho tuvo lugar en un territorio étnico. Se trata de una variable binaria que asume los valores SI o NO.
- `h_pertenencia_etnica`: Es un campo dependiente de h_incluye_informacion_etnica. Indica la pertenencia étnica del lugar en el que tuvo lugar el hecho. A diferencia de e_pertenencia_etnica, alude al lugar del hecho y no a la pertenencia étnica de la entidad asociada al hecho.
- `h_comunidad_etnica`: Es un campo dependiente de h_incluye_informacion_etnica y de h_pertenencia_etnica. Indica el pueblo o comunidad étnica a la que pertenece el lugar en el que tuvo lugar el hecho. A diferencia de e_comunidad_etnica, alude al lugar del hecho y no a la pertenencia étnica de la entidad asociada al hecho.
- `h_nombre_territorio_colectivo`: Es un campo dependiente de h_incluye_informacion_etnica, h_pertenencia_etnica y h_comunidad_etnica. Indica el nombre del territorio colectivo del lugar en el que tuvo lugar el hecho. A diferencia de e_nombre_territorio_colectivo, alude al lugar del hecho y no a la pertenencia étnica de la entidad asociada al hecho.
- `h_otro_nombre_comunidad_etnica`: (pendiente)
- `h_narrativa`: Campo que permite describir en prosa y en detalle el hecho registrado.
- `h_victimas_individuales_no_identificadas`: (pendiente).
- `h_motivacion`: Motivaciones de los perpetradores para cometer el hecho registrado.
- `h_otros_aspectos_a_destacar`: Características adicionales del hecho registrado que ameritan ser descritas en el registro.
- `h_codigo_indexacion_fuente`: Código de indexación de las fuentes asociadas al hecho registrado.
- `h_titulo_fuente`: Título de la fuente que reporta el hecho.
- `h_folio`: Folio de la fuente que reporta el hecho.

#### `5.2 Campos que refieren a la entidad e_ (new_vars_e.R)`

Corresponde a los campos que describen la entidad y que no varían en el tiempo como lo son la fecha y lugar de nacimiento o la pertenencia étnica. Asimismo, también permiten caracterizar datos de la entidad en la actualidad.

- `e_tipo_entidad`: Tipo de entidad asociada al hecho. En la gran mayorái de los casos, se corresponde con la variable `tipo_registro`.
- `e_primer_nombre`: Primer nombre de la entidad reportada.

(pentiente describir el test de new vars el cual evaluar que las variables esten, que tengan el formato que deberían tener y que los valores sean consistentes con el diccionario)

En el caso de los identificadores i_ se podria hacer un case_when y si se tiene un 0 en e_id o en h_id, se puede establecer que i_ es 0 porque no habría una entidad para un hecho o una entidad sin hecho.

#### `5.3 Campos que refieren a la información de la entidad al momento de los hechos i_ (new_vars_i.R)`

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



### `7. gen_ids (automatizada)`

Se procede con la generación de identificadores de hechos, entidades y entidades al momento del hecho. Se recupera el identificador generado en match y se generan los nuevos identificadores aprovechando la información sub-municipal.

### `8. merge_values`

Una vez se generaron los identificadores, se procede a llevar cada tabla a una distribución de 1 a 1 entre sus identificadores y el resto de las variables. Esto se logra a) fusionando algunos valores usando la | como delimitador o eliminando registros inconsistentes que posean menos información.

### `9. append (automatizada)`

Se unen las tres tablas por recordid, se validan la existencia de campos y de sus valores, se valida la distribución 1 a 1, se genera un nuevo recordid, un archivos cross_walk, se eliminan diplicados.












