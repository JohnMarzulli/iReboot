# iReboot

This is a Python scipt that controls an AC/DC relay attached to a Raspberry Pi
with a Cable or Fiber modem plugged into it.

When the code detects that internet connectivity is lost, it will reboot
the cable modem.

## Acknowledgements

This was based on the piWarmer project and would not have been possible
without it. It probably uses some GPIO code from it.
[https://github.com/mdegrazia/piWarmer](https://github.com/mdegrazia/piWarmer)

I want to extend my many thanks to Maria for starting such an amazing project!

## Disclaimer

**iReboot is to be used at your own risk**                    |

## Setup

You may wish to modify the iReboot.config file to include websites
that you are most concerned about.


## Wiring

**Note**: Physical pin numbering is used.

### Relay

* Red wire from GPIO22 to Relay "+"
* Black wire from Relay "-" to GPIO GND


## Additional Links And Setup Notes

## Materials List

All the parts listed are from Amazon

### Absolutely Required

This assumes you are building "from scratch" and need to buy a Raspberry Pi and
associate parts. I have picked a version of the Pi Zero that has Wireless, which
is good if you want to pull the code down directly onto the Pi


A MicroUSB to USB adapter is required for the modem to connect into the Pi
Zero's ****only**** USB port.

* [ ] [Raspberry Pi W, case, and IO pins](https://www.amazon.com/Raspberry-Starter-Power-Supply-Premium/dp/B0748MBFTS/ref=sr_1_3?s=electronics&ie=UTF8&qid=1512070820&sr=1-3&keywords=raspberry+pi+zero+pins)
qid=1512070675&sr=8-5&keywords=adafruit+lipo)
* [ ] [MicroUSB to USB adapter](https://www.amazon.com/Ksmile%C2%AE-Female-Adapter-SamSung-tablets/dp/B01C6032G0/ref=sr_1_1?dd=tLyVcVfk00xcTUme6zjHhQ%2C%2C&ddc_refnmnt=pfod&ie=UTF8&qid=1512071097&sr=8-1&keywords=micro+usb+adapter&refinements=p_97%3A11292772011)
* [ ] [Iot Power Relay](https://www.amazon.com/gp/product/B00WV7GMA2/ref=oh_aui_detailpage_o01_s01?ie=UTF8&psc=1)
* [ ] [Experimentation board with wires](https://www.amazon.com/gp/product/B01LYN4J3B/ref=oh_aui_detailpage_o08_s00?ie=UTF8&psc=1)


### Adapters

The Raspberry Pi zero uses a mini HDMI port for display. If you do not have an
adapter, you will need one to perform the setup. This is not required in the installation once the
device is "deployed". The USB hub makes coding and debugging on the PI possible
as it allows a keyboard and mouse to be connected
simultanously.

In normal use, no USB devices would be plugged in.

* [ ] [MiniHDMI to HDMI adapter](https://www.amazon.com/Adapter-VCE-Converter-Camcorder-Devices/dp/B01HYURR04/ref=sr_1_8?s=electronics&ie=UTF8&qid=1512070954&sr=1-8&keywords=mini+hdmi+adapter)
* [ ] [USB Hub](https://www.amazon.com/gp/product/B00XMD7KPU/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1)
