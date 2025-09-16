FROM node:24-alpine

RUN apk update \
    && apk --no-cache add curl \
    && rm -rf /var/cache/apk/*
# If you use Realtime Database, Cloud Firestore, or Cloud Storage emulator,
# you will need to add `openjdk11-jre-headless`.

RUN npm install -g firebase-tools@14.16.0       
