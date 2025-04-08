#/2424
# Authors:     SCB
# Maintainers: SCB
# Copyright:   2025
# =========================================
# CO-JEP/individual-GRAI/fase3/SANTUARIOS_DE_PAZ/clean/Makefile

HERE := $(shell git rev-parse --show-toplevel)

.PHONY: all clean

all: output/ruv_sample.parquet

clean:
	-rm output/*

output/ruv_sample.parquet: \
	/mnt/c/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/src/test_cn.py \
	/mnt/c/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/ruv_sample.parquet \
	/mnt/c/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/*cruzan.parquet \
	/mnt/c/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/*canon.parquet
	-mkdir output
	python3 $< \
		--input_df=/mnt/c/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/ruv_sample.parquet \
		--input_df_nc=/mnt/c/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/*cruzan.parquet \
		--input_df_canon=/mnt/c/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/input/*canon.parquet \
		--output_df=/mnt/c/Users/sebas/OneDrive/Documents/intro_polars_r/test_canonicalize_ruv/output/ruv_sample.parquet

# done.
