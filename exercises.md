# NovaStore - API, Databas och Cache

## Syfte

Syftet med laborationen är att förstå hur ett API hämtar data från en databas, hur ny data skapas via API:et och hur cache används för att minska belastningen på databasen.

Efter laborationen ska ni kunna förklara hur PostgreSQL, API:er och Redis samverkar i en modern applikation.

## Scenario

NovaStore är en växande e-handelsplattform. Webbshoppen, mobilappen och interna verktyg använder samma backend.

När trafiken ökar får databasen fler och fler förfrågningar. För att förbättra prestandan vill teamet bygga ett API som hämtar data från PostgreSQL och använder Redis för att cachea data som läses ofta.

## Bra att ha öppet

Ha gärna flera terminaler öppna:

- en terminal för Docker Compose
- en terminal för API-test med `curl`
- en terminal för PostgreSQL eller Redis

Starta från projektets rotmapp.

---

## Del 1 - Starta och förstå systemet

### Uppgift 1 - Starta miljön

Starta miljön med Docker Compose:

```bash
docker compose up --build
```

Verifiera att API, PostgreSQL och Redis startar korrekt.

Tips:

- Använd `docker ps` för att se containers.
- Använd `docker compose logs` om något inte fungerar.
- Leta efter felmeddelanden i loggarna.

### Uppgift 2 - Testa API:ets health-endpoint

Verifiera att API:et svarar innan ni börjar arbeta med produktdata.

Öppna i webbläsaren:

```text
http://localhost:5001/health
```

Eller använd `curl`:

```bash
curl http://localhost:5001/health
```

Tips:

- Börja alltid med `/health`.
- Om `/health` inte fungerar kommer resten av API:et sannolikt inte heller fungera.

### Uppgift 3 - Utforska databasen

Anslut till PostgreSQL:

```bash
docker exec -it novastore-db psql -U student -d novastore
```

Undersök `products`-tabellen:

```sql
SELECT * FROM products;
```

Tips:

- Titta på vilka kolumner tabellen har.
- Fundera över vilka fält API:et behöver returnera.

---

## Del 2 - Hämta data från databasen via API

### Uppgift 4 - `GET /products`

Verifiera och förstå hur `GET /products` hämtar produkter från PostgreSQL.

Testa endpointen:

```bash
curl http://localhost:5001/products
```

Tips:

- Börja med att skriva SQL-frågan direkt mot databasen.
- Jämför SQL-frågan med den färdiga funktionen i API:et.
- Titta i `api/app.py` och `api/db.py`.

### Uppgift 5 - `GET /products/{id}`

Implementera en endpoint som hämtar en specifik produkt.

Exempel:

```bash
curl http://localhost:5001/products/1
```

Tips:

- Fundera över vad som skiljer `GET /products/1` från `GET /products`.
- Implementera databaslogiken i `get_product_by_id_from_db(product_id)`.
- Använd en SQL-fråga med `WHERE id = %s`.

### Uppgift 6 - `404 Not Found`

Implementera felhantering om produkten inte existerar.

Testa med ett id som inte finns:

```bash
curl -i http://localhost:5001/products/999
```

Tips:

- Databasfunktionen bör returnera `None` om produkten saknas.
- API:et bör då returnera ett tydligt felmeddelande.


Exempel på svar:

```json
{
  "error": "Product not found"
}
```

### Diskussion

Diskutera:

- Varför ska API:et göra SQL-frågorna istället för klienten?
- Hur hjälper API:et till med säkerhet?
- Varför är det bra att klienten inte behöver känna till databasens struktur?

---

## Del 3 - Skapa data via API

### Uppgift 7 - `POST /products`

Implementera `POST /products` för att skapa nya produkter.

Exempel på request:

```bash
curl -i -X POST http://localhost:5001/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Webcam","price":799,"category":"Electronics","stock":12}'
```

Tips:

- Börja med att läsa JSON från requesten.
- Skriv gärna ut innehållet i terminalen innan ni sparar det.
- Titta på `request.get_json()` i Flask.


### Uppgift 8 - Spara i PostgreSQL

Spara den nya produkten i databasen.

Verifiera med:

```sql
SELECT * FROM products;
```

Tips:

- Implementera databaslogiken i `insert_product_into_db(product)`.
- Använd `INSERT INTO ... RETURNING ...` så att API:et kan returnera den skapade produkten.


### Uppgift 9 - Returnera `201 Created`

Returnera rätt statuskod när en produkt skapats.

Tips:

- Jämför skillnaden mellan `200 OK` och `201 Created`.
- `201 Created` betyder att servern har skapat en ny resurs.


### Uppgift 10 - `400 Bad Request`

Validera inkommande data och stoppa ogiltiga requests.

Följande requests ska inte accepteras:

- `name` saknas
- `price` saknas
- `price` är negativt

Testa exempel:

```bash
curl -i -X POST http://localhost:5001/products \
  -H "Content-Type: application/json" \
  -d '{}'
```

```bash
curl -i -X POST http://localhost:5001/products \
  -H "Content-Type: application/json" \
  -d '{"price":999}'
```

```bash
curl -i -X POST http://localhost:5001/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Webcam","price":-10}'
```

Tips:

- Stoppa felaktig data innan den når databasen.
- Returnera ett tydligt felmeddelande.


---

## Del 4 - Lägg till cache

### Uppgift 11 - Redis

Verifiera att Redis körs och förstå dess roll.

Anslut till Redis:

```bash
docker exec -it novastore-redis redis-cli
```

Testa:

```redis
KEYS *
GET products
```

Tips:

- Fundera över varför vi inte vill fråga databasen varje gång.
- Redis används här för att spara produktlistan tillfälligt.


### Uppgift 12 - Kontrollera cache först

Kontrollera Redis innan PostgreSQL frågas.

Flödet bör vara:

1. API:et tar emot `GET /products`.
2. API:et kontrollerar om produktlistan finns i Redis.
3. Om data finns i Redis används den.
4. Om data saknas i Redis hämtas data från PostgreSQL.

Tips:

- Implementera läsning i `get_cached_products()`.
- Använd funktionen från `api/app.py`.


### Uppgift 13 - Cache Hit och Cache Miss

Implementera loggning för cache hit och cache miss.

Tips:

- Logga tydligt i terminalen.
- Använd till exempel `print("CACHE HIT")` och `print("CACHE MISS")`.


### Uppgift 14 - Spara produktlistan i Redis

Spara resultatet från databasen i cache.

Tips:

- Redis sparar strängar.
- Fundera över hur JSON ska lagras i Redis.
- Använd gärna `json.dumps(...)` för att göra produktlistan till en sträng.
- Funktionen `set_cached_products(json_data)` är tänkt för detta.


### Uppgift 15 - Returnera cachead data

Returnera data från Redis när den finns.

Testa samma endpoint flera gånger:

```bash
curl http://localhost:5001/products
curl http://localhost:5001/products
```

Tips:

- Första anropet bör bli `CACHE MISS`.
- Andra anropet bör bli `CACHE HIT`.
- Använd gärna `json.loads(...)` när cachead JSON ska bli Python-data igen.


---

## Del 5 - Cache invalidation

### Uppgift 16 - Gammal cache

Visa problemet med gammal cache efter att en produkt skapats.

Gör så här:

1. Kör `GET /products` så att produktlistan hamnar i cache.
2. Skapa en ny produkt med `POST /products`.
3. Kör `GET /products` igen.
4. Jämför resultatet.

Tips:

- Om cache inte töms kan API:et returnera gammal information.


### Uppgift 17 - Töm cache efter `POST`

Töm produktcachen efter `POST /products`.

Tips:

- Implementera `clear_products_cache()`.
- Anropa funktionen efter att en produkt har sparats i PostgreSQL.
- Fundera över vilka endpoints som borde rensa cache i verkliga system.


---

## Reflektion

Diskutera:

- När är cache bra i NovaStore?
- Vilken data läses ofta men ändras sällan?
- När kan cache vara farligt?
- Vilken gammal information kan skapa problem för användare eller verksamheten?

## Stretch goals

När grunduppgifterna fungerar kan ni fortsätta med:

- implementera cache med TTL
- implementera cache per produkt
- implementera filtrering på kategori
- implementera sortering på pris

## Inlämning

Ni ska kunna visa att:

- API:et hämtar data från PostgreSQL
- produkter kan skapas via API:et
- `400 Bad Request` hanteras korrekt
- `404 Not Found` hanteras korrekt
- Redis används för cache
- cache invalidation fungerar efter `POST /products`
