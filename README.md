## How to Use this app

#### Build Docker

```
docker build -t ner-app .
```

#### Run Docker

```
docker run -p 8000:8000 ner-app
```

#### API

##### Endpoint

```
POST /api/upload/
```

##### Request Body

```
curl -X POST http://127.0.0.1:8000/api/upload/ \
     -H "Content-Type: multipart/form-data" \
     -F "file=@example.pdf"

```

##### Response

```
{
    "file_name": "example.pdf",
    "extracted_text": "Dear Mr. John Doe, your appointment is on 12th Feb 2025...",
    "entities": {
        "PERSON": ["John Doe"],
        "DATE": ["12th Feb 2025"],
        "ORG": ["Example Corp"]
    }
}

```
