#!/bin/bash

# adapted for my own purposes from https://github.com/phazus/lofiatc.sh

LOFI_YT=lofiyt.m3u


# taken from https://soundcloud.com/lofi_girl
cat >$LOFI_YT <<EOL
https://soundcloud.com/lofi_girl/get-some-rest
https://soundcloud.com/lofi_girl/drift
https://soundcloud.com/lofi_girl/living-room-flow-of-life
https://soundcloud.com/lofi_girl/parisian-romance
https://soundcloud.com/lofi_girl/john-lee-x-jazzyhan-jazz-in-nature
https://soundcloud.com/lofi_girl/stilte-x-schimmerlicht-existing
https://soundcloud.com/lofi_girl/nadav-cohen-x-robyn-payne-x-fred-paci-around-the-world
https://soundcloud.com/lofi_girl/back-on-fiji-hill
https://soundcloud.com/lofi_girl/in-your-eyes
https://soundcloud.com/lofi_girl/forever-again
https://soundcloud.com/lofi_girl/blue-monday
https://soundcloud.com/lofi_girl/holding-space
https://soundcloud.com/lofi_girl/serenity
https://soundcloud.com/lofi_girl/lofi-girl-christmas-2024
https://soundcloud.com/lofi_girl/kanisan-x-dario-lessing-edda-2
https://soundcloud.com/lofi_girl/lofi-girl-x-chesscom-synthwave-beats
https://soundcloud.com/lofi_girl/tales-of-the-eternal-kingdom
https://soundcloud.com/lofi_girl/sailboats-and-constellations
https://soundcloud.com/lofi_girl/1-pm-study-session
https://soundcloud.com/lofi_girl/drxnk-x-living-room-tales-of-the-past
https://soundcloud.com/lofi_girl/xander-x-lucid-keys-x-felt-galaxy-serenade-of-the-ages
https://soundcloud.com/lofi_girl/saga
https://soundcloud.com/lofi_girl/john-lee-the-lonely-tiger
https://soundcloud.com/lofi_girl/nokiaa-personages
https://soundcloud.com/lofi_girl/d0d-hourglass
https://soundcloud.com/lofi_girl/ethereal
https://soundcloud.com/lofi_girl/theo-aabel-the-search-for-planet-x
https://soundcloud.com/lofi_girl/far-beyond
https://soundcloud.com/lofi_girl/dragonfly
https://soundcloud.com/lofi_girl/hoogway-x-victorr-sketches-from-a-happy-place
https://soundcloud.com/lofi_girl/mell-o-idyllic
https://soundcloud.com/lofi_girl/fleeting-movements
https://soundcloud.com/lofi_girl/soothe
https://soundcloud.com/lofi_girl/under-the-sea
https://soundcloud.com/lofi_girl/sounds-from-my-room
https://soundcloud.com/lofi_girl/antonio-roberto-green-glimmers
https://soundcloud.com/lofi_girl/dreamland
https://soundcloud.com/lofi_girl/nowhere
EOL


if ! command -v "mpv" &>/dev/null; then
    echo "You must have mpv installed"
    echo "https://mpv.io/"
    exit 1
fi

# KBOS;General Edward Lawrence Logan International Airport;http://d.liveatc.net/kbos_final
echo "Playing: KBOS - General Edward Lawrence Logan International Airport" >&2
mpv --no-video --loop "http://d.liveatc.net/kbos_final" &>/dev/null &

# lofi playlist
mpv --no-video --shuffle --loop-playlist $LOFI_YT
