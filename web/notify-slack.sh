#!/bin/bash
if [[ -n $SLACK_WEBHOOK_URL ]]; then
    curl \
        -X POST \
        -H 'Content-type: application/json' \
        -d '{"attachments":[{"blocks":[{"type":"section","text":{"type":"plain_text","text":"[TC] Successfully deployed to Firebase Hosting :ok:","emoji":true}}],"color":"#00c000"}]}' \
        $SLACK_WEBHOOK_URL
fi
