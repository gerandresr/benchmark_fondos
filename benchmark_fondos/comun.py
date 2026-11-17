"""Funciones compartidas para proyectar el calendario de comisiones de los fondos de garantía."""

from datetime import date

import pandas as pd
from dateutil.relativedelta import relativedelta

# Códigos de moneda del archivo de stock (columna CRD_TIP_MON)
MONEDAS = {999: "CLP", 998: "UF", 13: "USD"}

# Frecuencia usada cuando la operación no tiene una frecuencia de pago numérica
# (por ejemplo "SIN FORMALIZAR"): equivale a un solo pago al vencimiento.
FRECUENCIA_SIN_DATO = 1000


def a_fecha(x) -> date:
    """Convierte un Timestamp/datetime a date."""
    return date(x.year, x.month, x.day)


def codigo_a_moneda(codigo, otra: str = "otra moneda") -> str:
    """Traduce el código CRD_TIP_MON a CLP/UF/USD; el resto queda como `otra`."""
    return MONEDAS.get(codigo, otra)


def frecuencia_meses(valor) -> int:
    """Frecuencia de pago en meses; si no es numérica usa FRECUENCIA_SIN_DATO."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return FRECUENCIA_SIN_DATO


def fechas_comision(fecha_informe: date, fecha_vence: date, frec_meses: int) -> list:
    """Fechas de pago desde el vencimiento hacia atrás, cada `frec_meses`,
    mientras sean posteriores a la fecha del informe."""
    fechas = [fecha_vence]
    f = fecha_vence
    while f - relativedelta(months=frec_meses) > fecha_informe:
        f = f - relativedelta(months=frec_meses)
        fechas.append(f)
    return fechas


def calendario_comisiones(fecha_informe: date, fecha_vence: date, frec_meses: int,
                          saldo: float, tasa_provision: float, ccy: str) -> pd.DataFrame:
    """Flujo de comisiones de una garantía.

    El primer flujo (en la fecha del informe) es la provisión, que va a Money Market.
    El resto del saldo se reparte en partes iguales en cada fecha de comisión.
    `tasa_provision` va en decimal (8.3% -> 0.083).
    """
    fechas = fechas_comision(fecha_informe, fecha_vence, frec_meses)
    n = len(fechas)
    return pd.DataFrame({
        "ccy": [ccy] * (n + 1),
        "fecha_comision": [fecha_informe] + fechas,
        "comision": [saldo * tasa_provision] + [saldo / n * (1 - tasa_provision)] * n,
    })


def pivotear(flujos: pd.DataFrame) -> pd.DataFrame:
    """Suma las comisiones por fecha (filas) y moneda (columnas)."""
    return pd.pivot_table(flujos, index="fecha_comision", columns="ccy",
                          values="comision", aggfunc="sum")
