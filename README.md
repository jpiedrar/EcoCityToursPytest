# Eco City Tours Test Suite

Automated tests for the [Eco City Tours](https://eco-city-tours.vercel.app/) website and its reservation and payment API clients.

The project uses:

- `pytest` as the test runner
- Selenium WebDriver for browser tests
- `requests` for API clients
- `unittest.mock` for isolated API tests

## Test coverage

### Website tests

The Selenium tests verify:

- The home page URL
- Visibility of the tours, guide, and contact sections
- The home page hero title
- Navigation to the contact page

Chrome runs in headless mode at a `1920x1080` viewport. These tests open the deployed Eco City Tours website and therefore require an internet connection and an installed Chrome browser.

### Reservation API tests

The reservation tests mock the HTTP request and cover:

- A successful reservation
- A reservation that cannot be fulfilled
- The successful response contract, including its required fields and data types

### Payment API tests

The payment tests mock all HTTP requests and cover three core retry scenarios:

1. The payment succeeds on the first attempt.
2. The first attempt fails and the second succeeds. Both requests reuse the same idempotency key, and the payment is processed once.
3. All three attempts fail and the payment is not processed.

The payment client retries server errors up to three times. It sends the same `Idempotency-Key` header with every attempt so a retried request cannot create a second payment when supported by the payment service.

Additional tests cover detailed HTTP 404 and timeout errors. Failed payments raise `PaymentError` with structured `error_type`, `status_code`, `attempts`, and `details` attributes. Client errors such as HTTP 404 fail immediately, while server errors and timeouts are retried up to the configured attempt limit.

## Project structure

```text
.
├── conftest.py
├── endpoints/
│   ├── api_client.py
│   ├── payment.py
│   └── reservations.py
├── pages/
│   ├── base_page.py
│   ├── contact_page.py
│   ├── header.py
│   └── home_page.py
└── tests/
    ├── test_contact.py
    ├── test_home.py
    ├── test_payment.py
    └── test_reservation.py
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the test dependencies:

```bash
python3 -m pip install pytest requests selenium
```

## Running the tests

Run the complete suite:

```bash
python3 -m pytest -q
```

Run only the mocked API tests:

```bash
python3 -m pytest -q tests/test_reservation.py tests/test_payment.py
```

Run only the browser tests:

```bash
python3 -m pytest -q tests/test_home.py tests/test_contact.py
```

Use verbose output while investigating a failure:

```bash
python3 -m pytest -v
```

## Notes

- API tests do not call real reservation or payment services; their responses are mocked.
- Reservation and payment clients inherit their base URL and request timeout configuration from `APIClient`.
- Set `API_BASE_URL` and `API_TIMEOUT` to override the API defaults. Tests inject their own base URL.
- Browser tests target the deployed site configured by `BasePage.BASE_URL`.
- The Selenium fixture creates a fresh browser for every test and closes it afterward.
