FROM node:18-alpine

RUN apk update \
    && apk --no-cache add curl \
    && rm -rf /var/cache/apk/*
# If you use Realtime Database, Cloud Firestore, or Cloud Storage emulator,
# you will need to add `openjdk11-jre-headless`.

RUN npm install -g firebase-tools@12.1.0
