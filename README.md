# Harkata

## Overview

Harkata is a lightweight, stateless backend for real-time quizzes inspired by platforms like Socrative and Kahoot, but with a focus on simplicity and privacy. The key differentiators:

- No user accounts or authentication required
- No persistent data storage (everything is in-memory)
- Simple HTTP polling instead of WebSockets
- Automatic cleanup of inactive quizzes

## How It Works

### For Teachers

1. Upload a JSON file containing quiz questions following our schema
2. Receive two keys: `x-quiz-public-key` and `x-teacher-key`
3. Share the public key with students
4. Use the teacher key to:
    - View the list of connected students
    - Control quiz progression
    - End the quiz when finished

There is currently no UI for teachers that would allow them to upload a quiz, manage the quiz, view the results or create a quiz JSON. These will be implemented later.

### For Students (Using a separate client)

1. Join using the quiz's public key and a display name
2. Receive a `x-student-session-key` for the duration of the quiz
3. Answer questions as they are presented
4. See results based on teacher settings

Note that multiple different clients can be used to join any quiz, since there is not login process. Maybe a simple SPA WebApp? Or C++ app running on a Raspberry Pi? Or even a simple command line client? The possibilities are endless.

## Technical Features

- RESTful API with simple header-based authentication
- Fully documented with OpenAPI/Swagger UI
- In-memory data storage with automatic cleanup
- Stateless architecture for easy scaling
- No WebSockets required - simple polling mechanism

## How to run

### Development

Development-tilassa sovellus käynnistyy osoitteeseen `http://localhost:3333` ja päivittyy automaattisesti muutosten yhteydessä.

```bash
docker compose up -d
```

Jos haluat, että VS Codessa toimii linter, niin varmista, että sinulla on lokaali node_modules-kansio. Tämä onnistuu ajamalla `src/harkata/` hakemistossa `npm install`.

### Production (local test)

Jos haluat kokeilla sovellusta tuotantotilassa, voit käyttää seuraavaa komentoa:

```bash
docker buildx build -t harkata -f harkata-prd.Dockerfile .
docker run --rm --name harkata -p 8888:5000 harkata
```

### Production (Dokku) - TODO

Varsinainen tuotantoon ajaminen tapahtuu Dokku-palvelimella. Tämä tehdään Github Actionsin toimesta (ks. `.github/workflows/dokku-harkata-deploy.yml`). Dokku käyttää Gittiä nokkellalla tavalla uuden version puskemiseen tuotantoon. Alla esimerkki siitä, miten uusi versio puskettaisiin Dokkuun, jos Actions ei olisi käytössä.

<details>
<summary>Olettaen että nämä on ajettu dokku-hostissa... (click open)</summary>

```bash
app_name=harkata
domain=munpaas.com

# -------- Dokku-palvelimella on pitänyt --------
# 1. Asettaa kaikkien sovellusten yhteinen domain
dokku domains:set-global $domain
# 2. Luoda sovellus
dokku apps:create $app_name
# 3. Asettaa sovellukselle Dockerfile
dokku builder-dockerfile:set $app_name dockerfile-path ./harkata-prd.Dockerfile
```
</details>

... voit puskea uuden version Dokkuun seuraavasti:

```bash
git remote add dokku dokku@$domain:$app_name
git push dokku main
```

Sivusto julkaistana osoitteeseen `{app_name}.{domain}`, esimerkiksi `harkata.munpaas.com`.

## Current Status

This project is currently in development.
