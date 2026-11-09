#!/bin/bash
export DISPLAY=:99
Xvfb :99 -screen 0 1440x900x24 &
sleep 1
fluxbox &
x11vnc -display :99 -forever -nopw -quiet &
websockify --web /usr/share/novnc 6080 localhost:5900 &
rm -f /profile/Singleton*
google-chrome --no-sandbox --user-data-dir=/profile \
  https://www.upwork.com/ab/account-security/login