# Benchmark Fondos

Proyecta el calendario de comisiones de los fondos de garantía **FOGAES** y **FOGAPE**
a partir de los archivos de stock del banco, y entrega un Excel con las comisiones
por fecha y moneda (CLP / UF / USD).

## Lógica

Para cada garantía:

1. **Provisión**: en la fecha del informe se reconoce `saldo × tasa de provisión` (va a Money Market).
2. **Resto**: `saldo × (1 − tasa)` se reparte en partes iguales en fechas que van desde el
   vencimiento hacia atrás, cada `FRECUENCIA DE PAGO` meses, mientras sean posteriores a la fecha del informe.
   Si la frecuencia no es numérica (ej. "SIN FORMALIZAR") se asume un solo pago al vencimiento.

| Fondo | Cartera | Tasa provisión | Detalle |
|---|---|---|---|
| FOGAES | Construcción | 8,30% | Una fila por operación del stock |
| FOGAES | Vivienda | 2,50% | Monto garantizado en UF × valor UF, repartido en plazos de 6, 8, 10, 10 y 10 años con pago mensual |
| FOGAPE | Stock FOGAPE | 5,00% | Excluye garantías vencidas y agrupa operaciones con igual moneda, vencimiento y frecuencia. Otras monedas se tratan como USD |

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
