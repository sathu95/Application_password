## Production Environment

https://mysecret.studio/

## Setup Development Enviroment

Read the following documentation to get your local enviroment setup. You will also need git to work.

* https://cloud.google.com/appengine/docs/standard/python/quickstart
* https://cloud.google.com/appengine/docs/standard/python/download

If you can get the tutorial working you can get the application to work.
* https://cloud.google.com/appengine/docs/standard/python/getting-started/creating-guestbook

Some command line commands:
```
sudo apt-get install google-cloud-sdk-app-engine-python google-cloud-sdk-app-engine-python-extras google-cloud-sdk-datalab google-cloud-sdk-datastore-emulator google-cloud-sdk-pubsub-emulator kubectl
```
optional:
```
python -m pip install google-cloud
python -m pip install google-cloud-datastore
sudo apt-get install python-mysqldb
```

## Start Development Server

* [local admin console - http://localhost:8000](http://localhost:8000)
* [local application - http://localhost:8080](http://localhost:8080)
* [vm admin console](http://172.29.255.244:8000)
* [vm application](http://172.29.255.244:8080)
* [0.0.0.0 application](http://0.0.0.0:8000)

```console
./dev.sh
```
---

## Source Code

Clone the source code from here. For help look at https://www.atlassian.com/git/tutorials

```
https://[USER NAME]@bitbucket.org/jaycangel/inm429_cloud_computing_jands.git
```
---
## Push Code Changes to Git
```console
git add
git commit -m "SOME DESCRIPTION OF THE WORK"
git push
```
---

## Deploy Code to Production

```console
gcloud app deploy app.yaml index.yaml --verbosity=debug
gcloud app browse
gcloud app logs tail
```

## Update Components

Sometimes if the gcloud app deploy hangs you need to update your local components.

```console
gcloud update components
```