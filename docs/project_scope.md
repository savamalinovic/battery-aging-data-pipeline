# Project Scope

## Dataset

Projekat koristi NASA Li-ion Battery Aging dataset.

MVP skup baterija:

- B0005
- B0006
- B0007
- B0018

Ulazni fajlovi su MATLAB `.mat` fajlovi.

## Pravila računanja

```text
rated_capacity_ah = 2.0

SOH = capacity_ah / 2.0

EOL:
  capacity_ah <= 1.4
  or
  SOH <= 0.70

Warning zone:
  SOH <= 0.80

Life stage:
  early  = SOH >= 0.90
  middle = 0.80 <= SOH < 0.90
  late   = SOH < 0.80

temperature_delta_to_ambient = avg_temperature - ambient_temperature
voltage_drop = start_voltage - end_voltage
