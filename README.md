# FT017TH Wireless Thermo-/Hygrometer Signal Decoding

## Product Details

- **Name in shop**: Brifit Thermometer Innen/Ausen, Hygrometer Thermometer mit Außensensor, Raumthermometer, Funk Thermometer mit Großem LCD Display, ℃/℉ Schalter, Ideal für Büro, Haus, Zimmer, Weiß
- **Name on box**: Brifit Humidity and Temperature Monitor
- **Model**: FT017TH
- **Manufacturer**: Unit Connection Technology Ltd, Shenzhen
- **Dealer**: Shenzhen Amier Technology CO Ltd (amirtec.com)
- **Frequency**: 433.92MHz
- powered by two 1.5V AAA batteries

## Signal

Sensors transmits approximately once per minute.

Recorded with [gqrx](https://gqrx.dk/) via RTL2832U/R820T (433.893MHz, AM):
![image](gqrx_20201128_100252_433893500.silences-shortened-4s.frames191500-207000.svg)
![image](gqrx_20201128_100252_433893500.silences-shortened-4s.frames-ca500-2500.svg)

After conversion to binary signal:
![image](gqrx_20201128_100252_433893500.silences-shortened-4s.transmission0.digitalized-frames.svg)

## Decoding

Signal is [manchester-encoded](https://en.wikipedia.org/wiki/Manchester_code).

Each transmission contains 3 repeats of the same message:

Each message consists of 65 bits:

| bit range | carried information                                    |
|-----------|--------------------------------------------------------|
| 0-8       | all high bits, probably sync signal                    |
| 9-17      | same byte in all transmissions, maybe sensors address? |
| 18-32     | unknown                                                |
| 33-44     | temperature                                            |
| 45-56     | humidity                                               |
| 57-64     | unknown                                                |
