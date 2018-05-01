#!/usr/bin/env bash

gcloud app deploy app.yaml index.yaml queue.yaml cron.yaml --verbosity=debug
