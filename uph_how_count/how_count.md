# `Conteos en el UPH`


El presente archivo de documentación tiene como propósito describir brevemente y ejemplificar los tipo de conteos que a la fecha se realizan a partir del Universo Provisional de Hechos. En primer lugar, se presentan los tipos de conteos y de expone en qué consiste cada uno y qué buscan representar. En segundo lugar, se expone la forma en la que los distintos tipos de conteos se concretizarn en código. Por último, se proponen 3 funciones que podrían facilitar y ser de utilidad para futuros ejercicios de generación de estadísticas descriptivas.

## `Descripción conceptual`


### `Contar víctimas únicas`

Este es el conteo más usual que realizamos cuando se nos solicitan estadísticas descriptivas. En este caso, de lo que se trata es de dimensionar cuántas personas naturales víctimas hacen parte de un determinado estrato, el cual estaría dado por las características (filtros) del requerimiento. En otras palabras, la unidad de análisis en este caso, son las personas naturales víctimas.
Lo anterior exige un ejercicio de deduplicación o identificación de entidades únicas. Este requisito estaría ya cubierto gracias al flujo de match, puesto que, justamente, la salida de este conjunto de tareas es un identificador que agrupa registros a la vez que separa e individualiza entidades. Este paso es fundamental toda vez que evita que una misma víctima se cuente múltiples veces, lo cual derivaría en sobredimensionar las cifras reportadas.

### `Contar victimizaciones`

El conteo de victimizaciones implica cambiar la unidad de análisis del punto anterior. El conteo de víctimas implica contar personas únicas, a pesar de que una misma persona pudo sufrir múltiples violencias en múltiples circunstancias. Es decir, cada persona cuenta como uno, aún cuándo, por ejemplo, ella misma haya padecido desplazamiento, amenazas, retenciones ilegales en varios momentos de su vida. Esto cambia cuando el objetivo es contar victimizaciones. Ya no se trata de contar personas, sino de contar las violencias que estas padecieron.

Teniendo en cuenta que una misma persona natural pudo haber sido víctima de múltiples violencias, el conteo de victimizaciones busca dimensionar los distintos tipos de hecho que se presentaron por persona natural.
La estructura del UPH permite que una misma persona esté relacionada con múltiples tipos de hecho y además, también permite que, dada una víctima relacionada a un determinado tipo hecho, existan n registros asociados siempre que se observe alguna variación en cualquiera de las variables del UPH. En otras palabras, una misma víctima puede tener dos registros de, por ejemplo, desplazamiento forzado. No obstante, dado que no es posible determinar si efectivamente la persona padeció dos desplazamientos o si la multiplicidad de registros se explica por errores en la documentación de la fuente original, se procede a generar un nuevo registro que cumpla con la función de representar al resto de registros para una misma entidad persona natural, un tipo de hecho y un tipo sujeto. Estos registros representantes son, justamente, el producto de la tarea merge.
Conteo de hechos

### `Contar hechos`
Hasta este punto, todos los conteos han tenido lugar dentro del estrado de las víctimas del UPH. Esto cambia al cambiar la unidad de análisis en la metodología del conteo de hechos. En este caso, se busca identificar hechos en términos de registros que coincidan en el tiempo, modo y lugar en el que se ocurrió una violencia.

Para este propósito, el conteo de hechos presupone deduplicar los registros que comparten una fecha (a nivel de día), una ubicación (a nivel municipal) y un tipo de hecho. Una vez se satisface este requisito, se habilita la cuantificación de hechos para un determinado estrato. Como se mencionó anteriormente, esta metodología de conteo no presupone ningún tipo de filtro en el campo del tipo sujeto, puesto que es irrelevante si el hecho se encuentra asociado a una víctima, a un perpetrador a ambos o a cualquier otra configuración valores.

## `Implementación operativa de los tipos de conteo`

El presente apartado está orientado a ilustrar con código algunos ejemplos de cómo se implementan los distintos tipos de conteos anteriormente descritos. Es importante señalar que, en todos los casos, la fuente para realizar los conteos corresponde a la `mr-table`. Esta última se encuentra disponible (en el caso de fase4) en: `/datos/observed-analysis-GRAI/fase4/counts/output/mr-table.parquet`.

Antes de pasar a los conteos, se precisa un pequeño ajuste a la mr-table a fin de garantizar que no se presenten errores en la ejecución del código. En concreto, la variable del año se transformará desde un formato de tipo cadena de texto a un formato de números enteros.


```R
mr_table <- read_parquet("/datos/observed-analysis-GRAI/fase4/counts/output/mr-table.parquet")

n_na_yy <- sum(is.na(mr_table$yy_hecho))

mr_table <- mr_table %>% 
  mutate(yy_hecho = as.integer(yy_hecho)) %>% 
  verify(sum(is.na(yy_hecho)) == n_na_yy)
```

En lo que sigue, se presentan distintos ejemplos de las metodologías de conteo anteriormente expuestas.


### `Códigos de ejemplo para el conteo de víctimas únicas`
```R
## Conteo de víctimas únicas para el municipio de pacho (Cundinamarca) en el periodo comprendido entre los años 1990 – 2005.
count_1 <- mr_table %>% 
  filter(dane_mpio_hecho == "25513",
         between(yy_hecho, 1990, 2005),
         tipo_sujeto_agr == "VICTIMA") %>% 
  summarise(n_vict_uniq = n_distinct(match_group_id, na.rm = TRUE))

```

```R
## Conteo de víctimas únicas para los municipios de Tumaco y Barbacoas (Nariño) para el periodo 1980 – 1998
## desagregado por municipio.
count_2 <- mr_table %>% 
  filter(dane_mpio_hecho %in% c("52835", "52079"),
         between(yy_hecho, 1980, 1998),
         tipo_sujeto_agr == "VICTIMA") %>% 
  #distinct(match_group_id, dane_mpio_hecho, yy_hecho) %>% 
  group_by(dane_mpio_hecho) %>% 
  summarise(n_vict_uniq = n_distinct(match_group_id, na.rm = TRUE)) %>% 
  ungroup()

```

```R
## Conteo de víctimas únicas en el municipio de Turbo (Antioquia) para el periodo 2000 – 2016
## desagregado por sexo.
count_3 <- mr_table %>% 
  filter(dane_mpio_hecho == "05837",
         between(yy_hecho, 2000, 2016),
         tipo_sujeto_agr == "VICTIMA") %>% 
  #distinct(match_group_id, dane_mpio_hecho, yy_hecho, sexo) %>% 
  group_by(sexo) %>% 
  summarise(n_vict_uniq = n_distinct(match_group_id, na.rm = TRUE)) %>% 
  ungroup()
```







