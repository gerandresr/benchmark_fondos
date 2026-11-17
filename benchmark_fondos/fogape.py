"""Benchmark FOGAPE: comisiones del stock de garantías FOGAPE.

Uso:
    python -m benchmark_fondos.fogape --stock "data/Stock Abril 2024 - GFOK MACA - para Tecno Riesgo.xlsx"
"""

import argparse
from pathlib import Path

import pandas as pd

from .comun import (FRECUENCIA_SIN_DATO, a_fecha, calendario_comisiones,
                    codigo_a_moneda, frecuencia_meses, pivotear)

TASA_PROVISION = 0.05  # 5,0%


def comisiones_fogape(archivo) -> tuple:
    """Devuelve (flujos, fecha_informe) a partir del stock FOGAPE."""
    dff = pd.read_excel(archivo)
    dff["FEC_VEN_FIN"] = dff.FEC_VEN_FIN.apply(a_fecha)
    # Otras monedas se tratan como USD
    dff["ccy"] = dff.CRD_TIP_MON.apply(lambda c: codigo_a_moneda(c, otra="USD"))
    dff["FRECUENCIA DE PAGO"] = dff["FRECUENCIA DE PAGO"].fillna(FRECUENCIA_SIN_DATO)
    fecha_informe = a_fecha(dff.FEC_INF_MES.iloc[0])

    # Se excluyen garantías vencidas y se agrupan las operaciones iguales
    dff = dff.loc[dff.FEC_VEN_FIN >= fecha_informe]
    df = (dff.groupby(["ccy", "FEC_VEN_FIN", "FRECUENCIA DE PAGO"])["SDO_GTA_MON_PES"]
             .sum().reset_index())

    flujos = [
        calendario_comisiones(
            fecha_informe=fecha_informe,
            fecha_vence=fila.FEC_VEN_FIN,
            frec_meses=frecuencia_meses(fila["FRECUENCIA DE PAGO"]),
            saldo=fila.SDO_GTA_MON_PES,
            tasa_provision=TASA_PROVISION,
            ccy=fila.ccy,
        )
        for _, fila in df.iterrows()
    ]
    return pd.concat(flujos, ignore_index=True), fecha_informe


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stock", required=True, help="Excel con el stock FOGAPE")
    p.add_argument("--salida", default="output/comisiones_fogape.xlsx")
    a = p.parse_args()

    flujos, fecha_informe = comisiones_fogape(a.stock)
    resultado = pivotear(flujos)

    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    resultado.to_excel(a.salida)
    print(f"Fecha informe {fecha_informe} -> {a.salida}")


if __name__ == "__main__":
    main()
