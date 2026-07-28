# PVPC España 🇪🇸⚡

Integración personalizada para **Home Assistant** que permite consultar los precios horarios de la tarifa regulada **PVPC (Precio Voluntario para el Pequeño Consumidor)** en España mediante la API de ESIOS (Red Eléctrica).

La integración proporciona sensores con información del precio actual, evolución diaria, horas más económicas y clasificación del coste energético.

---

## ✨ Características

- Consulta automática de precios PVPC.
- Actualización mediante `DataUpdateCoordinator`.
- Soporte para zonas:

  - Península
  - Canarias
  - Baleares
  - Ceuta
  - Melilla

- Sensores disponibles:

| Sensor | Descripción |
|---|---|
| Precio actual | Precio de la hora actual en €/kWh |
| Precio siguiente hora | Precio previsto para la siguiente hora |
| Precio mínimo | Precio más bajo del día |
| Precio máximo | Precio más alto del día |
| Precio medio | Media del día |
| Hora más barata | Hora con menor precio |
| Hora más cara | Hora con mayor precio |
| Precio medio restante | Media de las horas restantes |
| Horas restantes | Número de horas disponibles |
| Clasificación del precio | Bajo / Medio / Alto |
| Zona | Zona PVPC configurada |
| Tramo tarifario | Valle / Llano / Punta |
| Ranking hora actual | Posición del precio actual respecto al día |
| Diferencia respecto a la media | Diferencia porcentual |
| Precio mañana mínimo | Precio mínimo previsto para mañana |
| Precio mañana máximo | Precio máximo previsto para mañana |
| Precio mañana medio | Media prevista para mañana |
| Hora más barata mañana | Hora más económica de mañana |
| Hora más cara mañana | Hora más cara de mañana |

---

## 📊 Sensor principal

El sensor de precio actual incluye atributos adicionales para automatizaciones:

```yaml
today_prices:
  - hour: 0
    price: 0.1234
  - hour: 1
    price: 0.1187

tomorrow_prices:
  - hour: 0
    price: 0.1421

minimum_price: 0.0912
maximum_price: 0.2456
average_price: 0.1567
remaining_average: 0.1324
zone: Península
last_update: "2026-01-01T12:00:00"
```

---

# Instalación

## Opción 1: HACS (recomendada)

1. Abrir HACS.
2. Ir a **Integraciones**.
3. Añadir repositorio personalizado.
4. Introducir:

```
https://github.com/@joangpega/pvpc_spain
```

5. Seleccionar tipo:

```
Integration
```

6. Instalar.
7. Reiniciar Home Assistant.

---

## Opción 2: Instalación manual

Copiar la carpeta:

```
custom_components/pvpc_spain
```

dentro de:

```
/config/custom_components/
```

La estructura debe quedar:

```
config/
└── custom_components/
    └── pvpc_spain/
        ├── __init__.py
        ├── api.py
        ├── calculator.py
        ├── config_flow.py
        ├── coordinator.py
        ├── manifest.json
        ├── models.py
        └── sensor.py
```

Reiniciar Home Assistant.

---

# Configuración

La integración requiere un token API de ESIOS.

Puedes obtenerlo desde:

https://api.esios.ree.es/

Durante la configuración se solicitará:

- Token API
- Zona PVPC

---

# Tramos horarios

La integración calcula automáticamente el periodo horario 2.0TD:

## Valle

- 00:00 - 08:00
- Fines de semana
- Festivos nacionales

## Llano

- 08:00 - 10:00
- 14:00 - 18:00
- 22:00 - 00:00

## Punta

- 10:00 - 14:00
- 18:00 - 22:00

---
# Apex Chart disponible

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: PVPC hoy
  show_states: false
  colorize_states: true
graph_span: 24h
span:
  start: day
yaxis:
  - min: 0
    decimals: 3
    apex_config:
      title:
        text: €/kWh
      labels:
        formatter: |
          EVAL:function(value) {
            return value.toFixed(3);
          }
now:
  show: true
  label: Hora actual
series:
  - entity: sensor.pvpc_espana_precio_hoy
    name: Valle
    float_precision: 3
    type: column
    color: "#4CAF50"
    data_generator: |
      const prices = entity.attributes.prices;

      return Object.entries(prices)
        .filter(([_, data]) => data.period === "Valle")
        .map(([time, data]) => {
          const [hour, minute] = time.split(":");

          return [
            new Date(
              new Date().setHours(
                Number(hour),
                Number(minute),
                0,
                0
              )
            ).getTime(),
            data.price
          ];
        });
  - entity: sensor.pvpc_espana_precio_hoy
    name: Llano
    type: column
    float_precision: 3
    color: "#FFC107"
    data_generator: |
      const prices = entity.attributes.prices;

      return Object.entries(prices)
        .filter(([_, data]) => data.period === "Llano")
        .map(([time, data]) => {
          const [hour, minute] = time.split(":");

          return [
            new Date(
              new Date().setHours(
                Number(hour),
                Number(minute),
                0,
                0
              )
            ).getTime(),
            data.price
          ];
        });
  - entity: sensor.pvpc_espana_precio_hoy
    name: Punta
    type: column
    float_precision: 3
    color: "#F44336"
    data_generator: |
      const prices = entity.attributes.prices;

      return Object.entries(prices)
        .filter(([_, data]) => data.period === "Punta")
        .map(([time, data]) => {
          const [hour, minute] = time.split(":");

          return [
            new Date(
              new Date().setHours(
                Number(hour),
                Number(minute),
                0,
                0
              )
            ).getTime(),
            data.price
          ];
        });
apex_config:
  plotOptions:
    bar:
      columnWidth: 100%
  dataLabels:
    enabled: false
  tooltip:
    "y":
      formatter: |
        EVAL:function(value) {
          return Number(value).toFixed(3) + " €/kWh";
        }
```
<img width="380" height="282" alt="image" src="https://github.com/user-attachments/assets/afb1ab27-66be-4e6b-a15e-079cb06f9f97" />


# Automatizaciones de ejemplo

## Aviso cuando empieza la hora más barata

```yaml
automation:
  - alias: "Aviso hora barata PVPC"
    trigger:
      - platform: state
        entity_id: sensor.pvpc_espana_tramo_tarifario
        to: "Valle"

    action:
      - service: notify.mobile_app
        data:
          message: "Ha comenzado el periodo Valle"
```

---

## Encender electrodoméstico cuando el precio sea bajo

```yaml
automation:
  - alias: "Lavadora PVPC barata"
    trigger:
      - platform: numeric_state
        entity_id: sensor.pvpc_espana_precio_actual
        below: 0.10

    action:
      - service: switch.turn_on
        target:
          entity_id: switch.lavadora
```

---

# Desarrollo

Estructura interna:

```
pvpc_spain/
│
├── api.py
│   Cliente API ESIOS
│
├── coordinator.py
│   Gestión de actualizaciones
│
├── models.py
│   Modelos de datos
│
├── calculator.py
│   Lógica de cálculo
│
├── sensor.py
│   Entidades Home Assistant
│
└── config_flow.py
    Configuración desde UI
```

La lógica de negocio está separada del código de entidades para facilitar futuras ampliaciones:

- Binary Sensors
- Servicios
- Triggers
- Blueprints
- Condiciones

---

# Contribuciones

Las contribuciones son bienvenidas.

Si encuentras un error o tienes una propuesta:

1. Abre un issue.
2. Describe el problema.
3. Incluye logs relevantes de Home Assistant.

---

# Licencia

Este proyecto está publicado bajo licencia MIT.

---

# Créditos

Datos de precios proporcionados por:

- Red Eléctrica de España (ESIOS)

Desarrollado para la comunidad Home Assistant.
