# MQTT driver for Buva Boxstream RF

This code runs on esp32 board with micropython and nrf905 radio and exposes
home ventilation unit (buva vital air system aka boxstream rf) through mqtt.

Home assistant configuration is provided as well.

Fill all config entries in `config.py` to connect to wifi network.


Note: `fan.py` has hardcoded netword id (`rx_addr` and `tx_addr`) that you are assumed to know, as linking sequence is not included in the code and emulated remote with hardcoded id 89 (dec).

Note: for some reason my unit runs on frequency of zehnder, while it's labeled as buva. See `fan.py`.

# Hardware

See https://github.com/eelcohn/nRF905-API/blob/master/HARDWARE.md for hardware setup.

# Thanks

This was build upon existing research:

- https://github.com/eelcohn/ZehnderComfoair
- https://github.com/eelcohn/nRF905-API/
- https://gathering.tweakers.net/forum/list_messages/1728169
