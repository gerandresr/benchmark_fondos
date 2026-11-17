from datetime import date

import pytest

from benchmark_fondos.comun import (calendario_comisiones, codigo_a_moneda,
                                    fechas_comision, frecuencia_meses)


def test_fechas_hacia_atras_hasta_fecha_informe():
    f = fechas_comision(date(2024, 4, 30), date(2024, 12, 31), 3)
    assert f == [date(2024, 12, 31), date(2024, 9, 30), date(2024, 6, 30)]


def test_frecuencia_no_numerica_es_un_solo_pago():
    assert frecuencia_meses("SIN FORMALIZAR") == 1000
    assert frecuencia_meses("12") == 12
    assert fechas_comision(date(2024, 4, 30), date(2026, 1, 1), frecuencia_meses(None)) == [date(2026, 1, 1)]


def test_calendario_suma_el_saldo():
    df = calendario_comisiones(date(2024, 4, 30), date(2025, 4, 30), 1, 1_000.0, 0.083, "CLP")
    assert df.comision.sum() == pytest.approx(1_000.0)
    assert df.comision.iloc[0] == pytest.approx(83.0)
    assert df.fecha_comision.iloc[0] == date(2024, 4, 30)


def test_monedas():
    assert codigo_a_moneda(999) == "CLP"
    assert codigo_a_moneda(998) == "UF"
    assert codigo_a_moneda(13) == "USD"
    assert codigo_a_moneda(1) == "otra moneda"
    assert codigo_a_moneda(1, otra="USD") == "USD"
