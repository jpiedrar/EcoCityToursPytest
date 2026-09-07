import uuid

import requests


class PaymentEndpoint:
    def process_payment(self, url, payment, idempotency_key=None, max_attempts=3):
        idempotency_key = idempotency_key or str(uuid.uuid4())
        headers = {'Idempotency-Key': idempotency_key}

        response = None
        for _ in range(max_attempts):
            response = requests.post(url, json=payment, headers=headers)
            if response.status_code < 500:
                return response

        return response
