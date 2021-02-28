# MQTT driver for Buva Boxstream RF

This code runs on esp32 board with micropython and nrf905 radio and exposes
home ventilation unit (buva vital air system aka boxstream rf) through mqtt.

Fill all config entries in `config.py` to connect to wifi network.

Device should announce itself through mqtt autodiscovery when link to main unit
is established.

Set `network_id` in config to None and pull main unit out of socket for a moment
to enter into linkin mode. After finding out network id, set it in a config.
Network id would visible in homeassistant as part of device name e.g. Fan 988766551.

Note: emulates remote with hardcoded id 89 (dec). To be fixed

Note: for some reason my unit runs on frequency of zehnder, while it's labeled as buva. See `fan.py`.

# Hardware

See https://github.com/eelcohn/nRF905-API/blob/master/HARDWARE.md for hardware setup.

# Thanks

This was build upon existing research:

- https://github.com/eelcohn/ZehnderComfoair
- https://github.com/eelcohn/nRF905-API/
- https://gathering.tweakers.net/forum/list_messages/1728169
