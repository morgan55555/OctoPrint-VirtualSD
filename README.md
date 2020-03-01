# OctoPrint-VirtualSD

Klipper virtual SD card is not writable by default. You can get rid with it by changing SD card dir to Octoprint upload folder, but you always need to start printing manually.

With this plugin virtual card can act like regular SD card, you can drag'n'drop files into it, and use any upload plugin like Cura Octoprint plugin.

Now you can print files from Cura through fast Klipper virtual SD card.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/morgan55555/OctoPrint-VirtualSD/archive/master.zip

## Configuration

 - Enable virtual SD Card support - turn on write mode for virtual SD card
 - Enable SD Card remove command (M30) - turn on remove command for files (usefull when SD card is not in default Uploads dir)
 - Use Octoprint upload directory as SD directory - SD files will not move from uploads
 - Virtual SD card directory - set SD directory manually

## Klipper configuration

Just copy that code and change path to any that you need.

```ini
[virtual_sdcard]
path: /home/pi/.octoprint/uploads
```

## Known issues

> SD card printing from Cura Octoprint plugin will show endless "Analyzing" message, if PrintTimeGenius is installed.

Press "Print now" button in this message for printing, or disable PrintTimeGenius.
