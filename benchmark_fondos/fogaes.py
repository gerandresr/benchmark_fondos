"""Benchmark FOGAES: comisiones de garantías de construcción y de vivienda.

Uso:
    python -m benchmark_fondos.fogaes --uf 37086
    python -m benchmark_fondos.fogaes --stock data/otro.xlsx --vivienda data/otro2.xlsx --uf 38000
"""

import argparse
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta

from .comun import (a_fecha, calendario_comisiones, codigo_a_moneda,
                    frecuencia_meses, pivotear)

TASA_PROVISION_CONSTRUCCION = 0.083  # 8,30%
TASA_PROVISION_VIVIENDA = 0.025      # 2,50%
# Plazos promedio (años) en que se reparte el stock de vivienda, en partes iguales
PLAZOS_VIVIENDA = [6, 8, 10, 10, 10]


def comisiones_construccion(archivo) -> tuple:
    """Devuelve (flujos, fecha_informe) a partir del registro de stock de construcción."""
    df = pd.read_excel(archivo)
    fecha_informe = a_fecha(df.FEC_INF_MES.iloc[0])
    flujos = []
    for _, fila in df.iterrows():
        flujos.append(calendario_comisiones(
            fecha_informe=fecha_informe,
            fecha_vence=a_fecha(fila.FEC_VEN_FIN),
            frec_meses=frecuencia_meses(fila["FRECUENCIA DE PAGO"]),
            saldo=fila.SDO_GTA_MON_PES,
            tasa_provision=TASA_PROVISION_CONSTRUCCION,
            ccy=codigo_a_moneda(fila.CRD_TIP_MON),
        ))
    return pd.concat(flujos, ignore_index=True), fecha_informe


def comisiones_vivienda(archivo, fecha_informe, uf: float) -> pd.DataFrame:
    """Flujos de las solicitudes de vivienda vigentes (montos en UF pasados a pesos)."""
    df = pd.read_excel(archivo).dropna(subset=["CTL_CSU_IDE_GAV"])
    saldo_por_tramo = df.SOL_CRD_MNT_GAR_UF.sum() * uf / len(PLAZOS_VIVIENDA)
    flujos = [
        calendario_comisiones(
            fecha_informe=fecha_informe,
            fecha_vence=fecha_informe + relativedelta(years=anos),
            frec_meses=1,
            saldo=saldo_por_tramo,
            tasa_provision=TASA_PROVISION_VIVIENDA,
            ccy="UF",
        )
        for anos in PLAZOS_VIVIENDA
    ]
    return pd.concat(flujos, ignore_index=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stock", default="data/Registros Stock Construccion.xlsx")
    p.add_argument("--vivienda", default="data/Solicitudes Vivienda vigentes.xlsx")
    p.add_argument("--uf", type=float, required=True, help="Valor UF para pasar vivienda a pesos")
    p.add_argument("--salida", default="output/comisiones_fogaes.xlsx")
    a = p.parse_args()

    construccion, fecha_informe = comisiones_construccion(a.stock)
    vivienda = comisiones_vivienda(a.vivienda, fecha_informe, a.uf)
    resultado = pivotear(pd.concat([construccion, vivienda], ignore_index=True))

    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    resultado.to_excel(a.salida)
    print(f"Fecha informe {fecha_informe} -> {a.salida}")


if __name__ == "__main__":
    main()
