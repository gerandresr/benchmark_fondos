# Benchmark Fondos

Proyecta el calendario de comisiones de los fondos de garantía **FOGAES** y **FOGAPE**
a partir de los archivos de stock del banco, y entrega un Excel con las comisiones
por fecha y moneda (CLP / UF / USD).

## Idea general

Cada garantía se trata como un **bono sintético**: el saldo garantizado es el nominal y la
frecuencia de pago define una tabla de desarrollo con "cupones". Al sumar todos los bonos por
fecha y moneda se obtiene la tabla de desarrollo consolidada de cada fondo.

Los flujos de cada garantía suman exactamente su saldo garantizado: no hay tasa de interés ni
descuento, es devolución de capital en el tiempo.

## Cómo se arma cada bono

1. **Provisión**: en la fecha del informe se reconoce `saldo × tasa de provisión` (va a Money Market).
2. **Fechas de cupón**: se parte en el vencimiento y se retrocede cada `FRECUENCIA DE PAGO` meses,
   mientras la fecha sea posterior a la fecha del informe (igual que una tabla de un bono).
   Si la frecuencia no es numérica (ej. "SIN FORMALIZAR") hay un solo pago al vencimiento.
3. **Cupones**: `saldo × (1 − tasa)` se reparte en partes iguales entre las fechas de cupón.

**Ejemplo**: saldo 100, informe 30-abr-2024, vence 30-abr-2025, pago trimestral, provisión 8,3%
→ 8,3 hoy y 22,9 en jul-24, oct-24, ene-25 y abr-25.

## FOGAES (2 archivos)

**Construcción** — `Registros Stock Construccion.xlsx`, un bono por fila:

| Dato | Columna |
|---|---|
| Nominal (en pesos) | `SDO_GTA_MON_PES` |
| Vencimiento | `FEC_VEN_FIN` |
| Frecuencia (meses) | `FRECUENCIA DE PAGO` |
| Moneda (solo etiqueta) | `CRD_TIP_MON`: 999 CLP, 998 UF, 13 USD, resto "otra moneda" |
| Fecha del informe | `FEC_INF_MES` (primera fila) |

Provisión: **8,3%**.

**Vivienda** — `Solicitudes Vivienda vigentes.xlsx`, sin detalle por garantía:

1. Suma el monto garantizado en UF (`SOL_CRD_MNT_GAR_UF`) de las solicitudes vigentes y lo pasa a pesos con la UF entregada (`--uf`).
2. Divide el total en **5 tramos iguales** con vencimiento a 6, 8, 10, 10 y 10 años (60% a 10 años).
3. Cada tramo es un bono con cupones **mensuales** y provisión de **2,5%**. Moneda: UF.

Construcción y vivienda se suman en una sola tabla.

## FOGAPE (1 archivo)

Mismo bono sintético, con estos cambios previos:

1. **Excluye garantías vencidas** (vencimiento anterior a la fecha del informe).
2. **Agrupa** garantías con igual moneda, vencimiento y frecuencia (suma saldos; el resultado es el mismo que tratarlas por separado).
3. Monedas distintas de CLP/UF se tratan como **USD**.
4. Provisión: **5%**. Sin parte de vivienda.

## Comparación

| | FOGAES construcción | FOGAES vivienda | FOGAPE |
|---|---|---|---|
| Provisión | 8,3% | 2,5% | 5% |
| Bonos | uno por garantía | 5 tramos supuestos | por grupo de garantías |
| Saca vencidas | No | n/a | Sí |
| Otras monedas | "otra moneda" | todo UF | USD |

## Observaciones / pendientes

- Los montos están siempre en **pesos**, aunque la columna diga UF o USD.
- FOGAES construcción **no excluye garantías vencidas**: su flujo queda con fecha anterior al informe.
- Los plazos de vivienda (6/8/10/10/10 años) son un supuesto fijo en el código.
- Los cupones son iguales aunque el primer período quede corto (ej. vence en 10 meses con pago trimestral → 4 cuotas iguales, la primera cubre solo 1 mes).

## Estructura

```
benchmark_fondos/
├── benchmark_fondos/
│   ├── comun.py     # calendario de comisiones, monedas, pivote
│   ├── fogaes.py    # construcción + vivienda
│   └── fogape.py    # stock FOGAPE
├── tests/           # pruebas de la lógica común
├── data/            # archivos de entrada (no se suben a GitHub)
└── output/          # resultados (no se suben a GitHub)
```

## Uso

```bash
pip install -r requirements.txt

# FOGAES (por defecto lee data/Registros Stock Construccion.xlsx y data/Solicitudes Vivienda vigentes.xlsx)
python -m benchmark_fondos.fogaes --uf 37086

# FOGAPE
python -m benchmark_fondos.fogape --stock "data/Stock Abril 2024 - GFOK MACA - para Tecno Riesgo.xlsx"
```

Resultados en `output/comisiones_fogaes.xlsx` y `output/comisiones_fogape.xlsx`.
Cada script acepta `--salida` para cambiar el archivo de salida.

## Tests

```bash
python -m pytest
```
