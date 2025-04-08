# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 22:26:59 2025

@author: sebas
"""

import argparse
import polars as pl
import logging
import os
import glob

logging.basicConfig(format='%(asctime)s %(message)s')

logging.warning("load data")

def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_df",
                        default="/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/ruv_sample.parquet")
    parser.add_argument("--input_df_nc",
                        default="/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/*cruzan.parquet")
    parser.add_argument("--input_df_canon",
                        default="/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/*canon.parquet")
    parser.add_argument("--output_df", default=None)
    return parser.parse_args()

args = getargs()

df = pl.read_parquet(args.input_df)

logging.warning("create objects")

fields_canonicalized = {
    "recordid",
    "edad_h",
    "tipo_sujeto_h",
    "tipo_sujeto_agrupado_h",
    "sexo_h",
    "hecho_victimizante_h",
    "hecho_victimizante_agrupado_h",
    "dane_departamento_h",
    "departamento_h",
    "dane_municipio_h",
    "municipio_h",
    "pertenencia_etnica_h",
    "pueblo_o_comunidad_etnica_h",
    "nombre_territorio_colectivo_h"
    }

perp_cols = {
    "perp_AGENTES_ESTATALES",
    "perp_GRUPOS_POSDESMV_PARAMILITAR",
    "perp_GUERRILLA",
    "perp_GUERRILLA_ELN",
    "perp_GUERRILLA_FARC",
    "perp_GUERRILLA_OTRA",
    "perp_OTRO",
    "perp_PARAMILITARES",
    "perp_TERCERO"
    }

etnias = {
    "AFROCOLOMBIANA",
    "PALENQUERA",
    "PUEBLO INDIGENA",
    "PUEBLO ROM",
    "RAIZAL",
    None
    }

tipo_sujeto = {
    "PRESUNTO RESPONSABLE",
    "RECLUTADOR",
    "VICTIMA",
    "INFORMANTE",
    "VICTIMA INDIRECTA",
    "POSTULADO",
    "PERSONA QUE PONE EN CONOCIMIENTO",
    "DENUNCIANTE",
    "TESTIGO",
    "CITADO A AUDIENCIA",
    "OPOSITOR",
    "COLECTIVO",
    "APODERADO REPRESENTANTE",
    "CONTACTO",
    "OCUPANTE",
    "TRADENTE",
    "SOLICITANTE NO RESTITUIDO",
    "TERCERO OCUPANTE",
    "SOLICITANTE EN ESTUDIO"
    }

tipo_sujeto_agrupado = {
    "DENUNCIANTE",
    "OTRO",
    "PERPETRADOR",
    "TESTIGO",
    "VICTIMA",
    "VICTIMA INDIRECTA"
    }

tipo_hecho = {
    "ABANDONO DE CARGO",
    "ABANDONO DE MENORES",
    "ABANDONO O DESPOJO DE TIERRAS",
    "ABIGEATO",
    "ABORTO",
    "ABUSO DE AUTORIDAD",
    "ABUSO DE CONFIANZA",
    "ABUSO DE FUNCION PUBLICA",
    "ACAPARAMIENTO",
    "ACCIONES BELICAS",
    "ACTOS CONTRA EL ENTORNO NATURAL",
    "ACTOS CONTRA LA PROPIEDAD INDUSTRIAL",
    "ACTOS CONTRA LOS DATOS PERSONALES",
    "ACTOS CONTRA SISTEMAS INFORMATICOS",
    "ACTOS CONTRARIOS A DISPOSICIONES COMERCIALES",
    "ACTOS CONTRARIOS A LA DEFENSA",
    "ACTOS CONTRARIOS AL DERECHO LABORAL",
    "ACTOS DE BARBARIE",
    "ACTOS RELACIONADOS CON FUGA DE PRESOS",
    "ACTOS RELACIONADOS CON LAS ELECCIONES DEMOCRATICAS",
    "ACTO SEXUAL",
    "ADOPCION ILEGAL",
    "AGIOTAJE",
    "ALLANAMIENTO",
    "ALTERACION DEL ESTADO CIVIL",
    "ALZAMIENTO DE BIENES",
    "AMENAZA",
    "ANTICONCEPCION FORZADA",
    "APODERAMIENTO DE BIENES",
    "APROVECHAMIENTO",
    "ATAQUE A POBLADOS",
    "ATENTADOS Y ATAQUES A LA SUBSISTENCIA",
    "ATENTADOS Y ATAQUES CONTRA OBRAS",
    "CAPTACION DE DINEROS PUBLICOS",
    "CELEBRACION INDEBIDA DE CONTRATOS",
    "COHECHO",
    "CONCIERTO PARA DELINQUIR",
    "CONCUSION",
    "CONFINAMIENTO",
    "CONSPIRACION",
    "CONSTRENIMIENTO",
    "CONSTRUCCION Y UTILIZACION DE PISTAS DE ATERRIZAJE ILEGALES",
    "CONTRABANDO",
    "CONTRATACION ILEGAL",
    "CORRUPCION DE ALIMENTOS Y MEDICINAS",
    "CORRUPCION PRIVADA",
    "DANO A BIENES",
    "DANOS",
    "DEFRAUDACION",
    "DELITOS EN LA PRESTACION SERVICIOS DE TELECOMUNICACIONES",
    "DELITOS FINANCIEROS",
    "DESAPARICION FORZADA",
    "DESCONOCIMIENTO DE LA LEY",
    "DESPLAZAMIENTO",
    "DESTINACION ILEGAL DE BIENES",
    "DESTRUCCION O APROPIACION DE BIENES",
    "DESTRUCCION SUPRESION U OCULTAMIENTO DE DOCUMENTOS",
    "DETENCION ARBITRARIA",
    "DETENCION ILEGAL",
    "ENCUBRIMIENTO",
    "ENRIQUECIMIENTO ILICITO",
    "ENTRENAMIENTO PARA ACTIVIDADES ILICITAS",
    "ESCLAVITUD SEXUAL",
    "ESPIONAJE",
    "ESTAFA",
    "EXACCION",
    "EXTERMINIO",
    "EXTORSION",
    "FABRICACION TRAFICO PORTE O USO DE ARMAS O EXPLOSIVOS",
    "FALSA DENUNCIA",
    "FALSEDAD DOCUMENTAL",
    "FALSEDAD MARCARIA",
    "FALSEDAD MONETARIA",
    "FALSEDAD PERSONAL",
    "FALSEDAD TESTIMONIAL",
    "FAVORECIMIENTO",
    "FEMINICIDIO",
    "FRAUDE",
    "GENOCIDIO",
    "GESTION INDEBIDA DE RECURSOS",
    "HOMICIDIO",
    "HOSTIGAMIENTO",
    "HOSTILIDAD MILITAR",
    "HURTO",
    "INCENDIO",
    "INCESTO",
    "INFIDELIDAD A LOS DEBERES PROFESIONALES",
    "INGRESO ILEGAL AL PAIS",
    "INJURIA Y CALUMNIA",
    "INSTIGACION A DELINQUIR",
    "INSTIGACION A LA GUERRA",
    "INSUBORDINACION",
    "INTERVENCION EN POLITICA",
    "INVASION",
    "INVASION Y USURPACION DE TIERRAS",
    "IRRESPETO A CADAVERES",
    "LAVADO DE ACTIVOS",
    "LESIONES",
    "MALTRATO",
    "MALTRATO ANIMAL",
    "MANIPULACION O TRAFICO DE OBJETOS PELIGROSOS",
    "MASACRES",
    "NARCOTRAFICO",
    "OBSTRUCCION DE ACCIONES DE DEFENSA Y ASISTENCIA",
    "OBSTRUCCION DE VIAS PUBLICAS",
    "OMISION DE APOYO Y DOCUMENTACION RELACIONADA",
    "OMISION DE CONTROL",
    "OMISION DE DENUNCIA",
    "OTRAS OMISIONES",
    "OTRAS PERTURBACIONES",
    "OTRO",
    "OTROS ACTOS CONTRA LA LIBERTAD",
    "OTROS DELITOS ASOCIADOS A LA FUNCION PUBLICA",
    "OTROS DELITOS CONTRA LA REPRODUCCION HUMANA",
    "OTROS DELITOS CONTRA MENORES",
    "OTROS DELITOS RELACIONADOS CON LA FAMILIA",
    "OTROS DESPOJOS",
    "OTROS TIPOS DE ABUSO",
    "PECULADO",
    "PERDIDA DE BIENES MUEBLES O INMUEBLES",
    "PERFIDIA",
    "PERSECUCION DE UN GRUPO O COLECTIVIDAD CON IDENTIDAD PROPIA",
    "PERTENENCIA A GAOML",
    "PERTURBACION DE ACTOS OFICIALES O PUBLICOS",
    "PERTURBACION DE SERVICIOS PUBLICOS",
    "PILLAJE",
    "PORTE DE OTRAS SUSTANCIAS NOCIVAS",
    "PREVARICATO",
    "PROPAGACION DE VIRUS",
    "RACISMO O DISCRIMINACION",
    "REBELION",
    "RECEPTACION",
    "RECLUTAMIENTO",
    "REPETIBILIDAD DEL SER HUMANO",
    "REPRESARIAS EN EL MARCO DEL CONFLICTO",
    "RETENCION ILEGAL",
    "REVELACION DE SECRETO",
    "SABOTAJE",
    "SIN DATO",
    "SOBORNO",
    "SUICIDIO ASISTIDO O INCITACION AL SUICIDIO",
    "TENTATIVA FEMINICIDIO",
    "TENTATIVA HOMICIDIO",
    "TENTATIVA DE RETENCION ILEGAL",
    "TERRORISMO",
    "TESTAFERRATO",
    "TOMA DE REHENES",
    "TORTURA",
    "TRABAJO FORZOSO",
    "TRAFICO DE INFLUENCIAS",
    "TRATA DE PERSONAS",
    "TRATOS INHUMANOS",
    "ULTRAJE A SIMBOLOS PATRIOS",
    "USURA",
    "USURPACION O SUPLANTACION DE FUNCIONES PUBLICAS",
    "UTILIZACION ILICITA DE EQUIPOS COMUNICACION",
    "UTILIZACION ILICITA DE UNIFORMES E INSIGNIAS",
    "UTILIZACION INDEBIDA DE INFORMACION",
    "UTILIZACION METODOS DE GUERRA ILICITOS",
    "VIOLACION DE COMUNICACIONES",
    "VIOLACION DE DERECHOS DE AUTOR",
    "VIOLACION DE HABITACION AJENA",
    "VIOLACION DE INHABILIDADES",
    "VIOLACION DE INMUNIDAD DIPLOMATICA",
    "VIOLENCIA CONTRA SERVIDOR PUBLICO",
    "VIOLENCIA DE GENERO",
    "VIOLENCIA INTRAFAMILIAR",
    "VIOLENCIA SEXUAL",
    "DEFORESTACION",
    "ESTERILIZACION FORZADA",
    "PLANIFICACION FORZADA",
    "ANTICONCEPCION FORZADA",
    "CUALQUIER OTRA FORMA DE VIOLENCIA SEXUAL DE GRAVEDAD COMPARABLE",
    "AMENAZA DE VIOLACION",
    "OBLIGACION DE PRESENCIAR ACTOS SEXUALES",
    "MATERNIDAD FORZADA",
    "MUTILACION DE ORGANOS SEXUALES",
    "CAMBIOS FORZADOS EN LA CORPORALIDAD",
    "UNION Y CONVIVENCIA FORZADA",
    "VIOLENCIA REPRODUCTIVA",
    "ACOSO SEXUAL",
    "ACTO SEXUAL",
    "PROSTITUCION",
    "ACCESO CARNAL/VIOLACION SEXUAL",
    "DESNUDEZ FORZADA",
    "EMBARAZO FORZADO",
    "ESCLAVITUD SEXUAL",
    "TRAFICO DE MENORES",
    "PORNOGRAFIA",
    "PROXENETISMO",
    "TURISMO SEXUAL",
    "EXPLOTACION SEXUAL",
    "ABORTO FORZADO",
    "CAZA ILEGAL",
    "CONTAMINACION AMBIENTAL",
    "CONTAMINACION AGUAS",
    "DANO EN RECURSOS NATURALES",
    "DESTRUCCION DEL MEDIO AMBIENTE",
    "EXPERIMENTACION ILEGAL CON ESPECIES ANIMALES O VEGETALES",
    "EXPLOTACION ILEGAL MINERA O PETROLERA",
    "APROVECHAMIENTO ILICITO DE RECURSOS NATURALES",
    "PESCA ILEGAL",
    "USURPACION DE AGUAS",
    "EXPLOTACION ILEGAL DE RECURSOS NATURALES",
    None
    }

tipo_hecho_agrupado = {
    "ABANDONO O DESPOJO DE TIERRAS",
    "ACCIONES BELICAS",
    "ACTOS CONTRA EL ENTORNO NATURAL",
    "AMENAZA",
    "ATENTADO",
    "DELITOS CONTRA EL ESTADO",
    "DELITOS CONTRA EL ORDEN ECONOMICO SOCIAL",
    "DELITOS CONTRA EL PATRIMONIO ECONOMICO",
    "DELITOS CONTRA LA ADMINISTRACION PUBLICA",
    "DELITOS CONTRA LA FAMILIA",
    "DELITOS CONTRA LA FE PUBLICA",
    "DELITOS CONTRA LA INTEGRIDAD",
    "DELITOS CONTRA LA JUSTICIA",
    "DELITOS CONTRA LA SALUD PUBLICA",
    "DELITOS CONTRA LA SEGURIDAD PUBLICA",
    "DELITOS CONTRA LAS PBP-DIH",
    "DESAPARICION FORZADA",
    "DESPLAZAMIENTO FORZADO",
    "DETENCION ARBITRARIA",
    "HOMICIDIO",
    "OTRO",
    "OTROS DELITOS CONTRA LA LIBERTAD",
    "OTROS DELITOS CONTRA LA VIDA",
    "REBELION",
    "RECLUTAMIENTO",
    "RETENCION ILEGAL",
    "TORTURA",
    "VIOLENCIA SEXUAL",
    None
    }

sexo = {
    "HOMBRE",
    "INTERSEXUAL",
    "MUJER",
    None
    }

rango_edad = {
    "0_5",
    "18_24",
    "25_64",
    "6_17",
    "65_MAS",
    None
    }

clasificacion_hecho = {
    "ABSTENCION DEL DEBER DE PROTECCION",
    "ATAQUE A BASES MILITARES Y ESTACIONES DE POLICIA",
    "ATENTADO TERRORISTA",
    "BOMBARDEO",
    "DANO A BIENES CIVILES",
    "DESPLAZAMIENTO INDIVIDUAL",
    "DESPLAZAMIENTO MASIVO",
    "MASACRE",
    "MINAS ANTIPERSONALES Y OTROS REMANENTES EXPLOSIVOS DE GUERRA",
    "MUERTE ILEGITIMAMENTE PRESENTADA COMO BAJA EN COMBATE",
    "PARAPOLITICA",
    "PRESUNTOS HOMICIDIOS ASOCIADOS CON AGENTES DEL ESTADO",
    "PRESUNTOS VINCULOS FUNCIONARIOS PUBLICOS CON GRUPOS ILEGALES",
    "RETEN","SECUESTRO SELECTIVO",
    "TOMA DE POBLACIONES",
    "UTILIZACION DE MEDIOS Y METODOS DE GUERRA ILICITOS",
    "VICTIMIZACIONES A DEFENSORES DDHH",
    "VICTIMIZACIONES A LIDERES SOCIALES O ACTIVISTAS AMBIENTALES",
    "VICTIMIZACIONES A PERSONAS VINCULADAS A ORGANIZACIONES SINDICALES",
    "VICTIMIZACIONES A PERSONAS VINCULADAS A PARTIDOS POLITICOS",
    "VIOLENCIA BASADA EN GENERO",
    "VIOLENCIA INTRAFILAS",
    None
    }

def cannclz_test(df_i):

    (
        df_i
        .with_columns(
            N_missing=pl.sum_horizontal(pl.col(perp_cols).is_null()),
            N_perps=pl.sum_horizontal(pl.col(perp_cols))
        )
        .select(
            (
                (pl.col("N_missing") == 9) | 
                (pl.col("N_perps").is_not_null() & (pl.col("N_perps") >= 1))
            ).all()
        )
        .pipe(lambda x: x.item() or print("Filas inválidas detectadas"))
    )
    
    error_sex = df_i.filter(
        (
            (pl.col("sexo_h") == "INTERSEXUAL") &
            (pl.col("osigd_h") != "SI")
        ) |
        (
            (pl.col("identidad_de_genero_h") == "TRANSGENERO") &
            (pl.col("osigd_h") != "SI")
            
        ) |
        (
            (pl.col("identidad_de_genero_h").is_in(["BISEXUAL",
                                                    "HOMOSEXUAL",
                                                    "ASEXUAL"])) &
            (pl.col("osigd_h") != "SI")
        )
    )   

    if not error_sex.height == 0:
        raise AssertionError(f"Error combinaciones de valores en maestra sexo")
    if not fields_canonicalized.issubset(df_i.columns):
        raise AssertionError(f"La tabla no contiene todas las columnas.")
    if not df_i["pertenencia_etnica_h"].is_in(etnias).all():
        raise AssertionError(f"etnias")
    if not df_i["tipo_sujeto_h"].is_in(tipo_sujeto).all():
        raise AssertionError(f"tipo sujeto")
    if not df_i["tipo_sujeto_agrupado_h"].is_in(tipo_sujeto_agrupado).all():
        raise AssertionError(f"tipo sujeto agrupado")
    if not df_i["hecho_victimizante_h"].is_in(tipo_hecho).all():
        raise AssertionError(f"tipo hecho")
    if not df_i["hecho_victimizante_agrupado_h"].is_in(tipo_hecho_agrupado).all():
        raise AssertionError(f"tipo hecho")
    if not df_i["sexo_h"].is_in(sexo).all():
        raise AssertionError(f"sexo")
    if not df_i["rango_edad_h"].is_in(rango_edad).all():
        raise AssertionError(f"rango edad")
    if not df_i["edad_h"].is_between(1, 110).all():
        raise AssertionError(f"edad")
    if not df_i["menor_de_edad_h"].is_between(0, 1).all():
        raise AssertionError(f"menor edad")
    if not df_i["dd_hecho"].is_between(1, 31).all():
        raise AssertionError(f"dia")
    if not df_i["mm_hecho"].is_between(1, 12).all():
        raise AssertionError(f"mes hecho")
    if not df_i["yy_hecho"].is_between(1900, 2024).all():
        raise AssertionError(f"anio hecho")
    if not df_i["mm_hecho_final"].is_between(1, 12).all():
        raise AssertionError(f"mes hecho final")
    if not df_i["dd_hecho_final"].is_between(1, 31).all():
        raise AssertionError(f"dd hecho final")
    if not df_i["yy_hecho_final"].is_between(1900, 2024).all():
        raise AssertionError(f"anio hecho final")
    if not df_i["dd_nacimiento"].is_between(1, 31).all():
        raise AssertionError(f"dd nacim")
    if not df_i["mm_nacimiento"].is_between(1, 12).all():
        raise AssertionError(f"mes nacimien")
    if not df_i["yy_nacimiento"].is_between(1870, 2024).all():
        raise AssertionError(f"anio naci")
    if not df_i["flag_edad"].is_between(0, 1).all():
        raise AssertionError(f"flag edad")
        
def cannclz_test_cnn(df_i):
    
    if not df_i.height > 0:
        raise AssertionError(f"Registros no cruzan")
    if not fields_canonicalized.issubset(df_i.columns):
        raise AssertionError(f"La tabla no contiene todas las columnas.")
    if not df_i["pertenencia_etnica_h"].is_in(etnias).all():
        raise AssertionError(f"etnias")
    if not df_i["tipo_sujeto_h"].is_in(tipo_sujeto).all():
        raise AssertionError(f"tipo sujeto")
    if not df_i["tipo_sujeto_agrupado_h"].is_in(tipo_sujeto_agrupado).all():
        raise AssertionError(f"tipo sujeto agrupado")
    if not df_i["hecho_victimizante_h"].is_in(tipo_hecho).all():
        raise AssertionError(f"tipo hecho")
    if not df_i["hecho_victimizante_agrupado_h"].is_in(tipo_hecho_agrupado).all():
        raise AssertionError(f"tipo hecho")
    if not df_i["sexo_h"].is_in(sexo).all():
        raise AssertionError(f"sexo")
    if not df_i["rango_edad_h"].is_in(rango_edad).all():
        raise AssertionError(f"rango edad")
        
    df_sr = (
        df_i
        .with_columns(
            pl.col("clasificacion_hecho_h").str.split("|")
            )
        .explode("clasificacion_hecho_h")
        .select(pl.col('clasificacion_hecho_h'))
        )
    
    if not df_sr["clasificacion_hecho_h"].is_in(clasificacion_hecho).all():
        raise AssertionError(f"clasificacion del hecho")
    

logging.warning("starting test for canonicalize")

cannclz_test(df)

df = None

logging.warning("ending test for canonicalize")

logging.warning("starting test for no-cruzan.parquet")

path_no_cross = glob.glob(args.input_df_nc)
path_no_cross = [path.replace("\\", "/") for path in path_no_cross]

df_no_cross = [pl.read_parquet(i) for i in path_no_cross]
df_bind_nc = pl.concat(df_no_cross)

if not df_bind_nc.height == 0:
    raise AssertionError(f"Registros no cruzan")
    
logging.warning("ending test for no-cruzan")

logging.warning("starting test for -canon.parquet")

fields_canonicalized_cnn = [
    "narrativo_lugar",
    "narrativo_hechos",
    "source",
    "alias_c",
    "nombre_informe_c",
    "codigo_indexacion_c",
    "patrones_c",
    "narrativo_ocupacion"
    ]

fields_canonicalized.update(fields_canonicalized_cnn)

path_canon = glob.glob(args.input_df_canon)
path_canon = [path.replace("\\", "/") for path in path_canon]

df_canon = [pl.read_parquet(i) for i in path_canon]
df_bind_canon = pl.concat(df_canon)

cannclz_test_cnn(df_bind_canon)

logging.warning("ending test for -canon.parquet")

logging.warning("done test-canonicalize.py")
#done.