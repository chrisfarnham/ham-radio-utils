#!/bin/bash

# adapted for my own purposes from https://github.com/phazus/lofiatc.sh

LOFI_YT=lofiyt.m3u

cat >$LOFI_YT <<EOL
https://open.spotify.com/album/6nakNRC332lsQ7nbDWC76b?si=pjjaWyCZQUm2AIV0OmurEA&nd=1
https://open.spotify.com/album/6nakNRC332lsQ7nbDWC76b?si=pjjaWyCZQUm2AIV0OmurEA&nd=1
https://www.youtube.com/watch?v=-i-3STX7QSs
https://www.youtube.com/watch?v=0Rqte6TTkHs
https://www.youtube.com/watch?v=0WWOLMcCWv4
https://www.youtube.com/watch?v=1Ox6_gvTx5s
https://www.youtube.com/watch?v=2C1nrfpqdPg
https://www.youtube.com/watch?v=3GOylOK4e18
https://www.youtube.com/watch?v=3yZonj6gdt0
https://www.youtube.com/watch?v=5V2nGGbUE6c
https://www.youtube.com/watch?v=61NMgMEMWLg
https://www.youtube.com/watch?v=76JG1KJyqGI
https://www.youtube.com/watch?v=7aW4OPzGvuE
https://www.youtube.com/watch?v=7p9ydzEpePA
https://www.youtube.com/watch?v=96b26qRUFcQ
https://www.youtube.com/watch?v=9DsLlsWuD_4
https://www.youtube.com/watch?v=aU4qUCpeQAk
https://www.youtube.com/watch?v=BJHC7ZBFi-I
https://www.youtube.com/watch?v=bzmM_CXAnxQ
https://www.youtube.com/watch?v=c58j1P6DFXE
https://www.youtube.com/watch?v=cd1q9EWGlUI
https://www.youtube.com/watch?v=ciRuNl7PtGs
https://www.youtube.com/watch?v=Dh6DghQZpUk
https://www.youtube.com/watch?v=EejMDX4E7yU
https://www.youtube.com/watch?v=EkoamWXpKbI
https://www.youtube.com/watch?v=eqmKCRU9rV8
https://www.youtube.com/watch?v=eR0XbyA3gYc
https://www.youtube.com/watch?v=ezORl9JOqkk
https://www.youtube.com/watch?v=FcvRGhG2FnI
https://www.youtube.com/watch?v=FnZiSWohkHA
https://www.youtube.com/watch?v=h5DVCtBD_YA
https://www.youtube.com/watch?v=iPUUU1QPKro
https://www.youtube.com/watch?v=j9ziXYpFs1I
https://www.youtube.com/watch?v=Jg7uJj8aEOA
https://www.youtube.com/watch?v=K7EUBOYmuyE
https://www.youtube.com/watch?v=kKekTf8Ljvo
https://www.youtube.com/watch?v=l_j1PWVzpNM
https://www.youtube.com/watch?v=m_qQg3gQyD8
https://www.youtube.com/watch?v=NjDLja4ob1w
https://www.youtube.com/watch?v=nSZlRU2EPYA
https://www.youtube.com/watch?v=oN_r557ouD8
https://www.youtube.com/watch?v=OpfHoK9VXys
https://www.youtube.com/watch?v=PhxFvu2yEI0
https://www.youtube.com/watch?v=PsA7p0Fc9mQ
https://www.youtube.com/watch?v=pzvBkRE-SRo
https://www.youtube.com/watch?v=S7u5XMV8WFY
https://www.youtube.com/watch?v=SmioVk2rVEY
https://www.youtube.com/watch?v=TJLmyD6Feuo
https://www.youtube.com/watch?v=Tz7MeFIILng
https://www.youtube.com/watch?v=V-0rAbrUb_8
https://www.youtube.com/watch?v=wJ5k63qazng
https://www.youtube.com/watch?v=xjceqbdXUB4
https://www.youtube.com/watch?v=Y4sbNEc94EE
https://www.youtube.com/watch?v=ydgz6cXaA8c
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
