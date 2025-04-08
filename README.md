# AI Speech to Text transcription

The Live Transcription Device is designed to take speech from a user and turn it into text that will be displayed on a screen using vosk. This is a raspberry pi based and requires these components

- Raspberry Pi 4 Model B
- Maono AU-UL10 USB Lavalier Microphone
- 11.9 inche waveshare LCD screen
- 16 GB < microSD card
- USB-C cable
- Micro-HDMI to HDMI connector
- SD card reader

before starting the assembly make sure that the SD card has a version of Raspberry Pi OS Bullseye lite installed on it. This can be done by using the raspberry pi imager. to get the imager go to https://www.raspberrypi.com/software/ and downlaod the imager there. from here follow these steps:

1. for raspbery pi device click the chose button and select raspberry pi 4
2. for operating system click the choose os button
3. click Raspberry Pi OS (other) option then click raspberry pi OS (legacy, 64-bit ) Lite
4. click chose storage andd select your SD card
5. click edit settings and change the general settings for the username and password to what you want
6. Make sure SSH is enabled under services
7. click yes then click ok

After the raspberry pi OS image will be flashed to that SD card. once done edit the config.txt file to have the same content as the one in this repo so that when you connect the screen the raspberry pi will display to it.

## Assembly

The device can be assembled using the following steps:

1. inserting the micro SD card into the back of the raspberry pi

<p align="center"><img src="./physical-pics/RaspberryPi.jpg" alt="Picture Of The Raspberry Pi"/></p>
