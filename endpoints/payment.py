import uuid
from http import HTTPStatus
import requests
from endpoints.base_api import BaseAPIClient

class PaymentError(Exception):
    def __init__(self, message, *, error_type, attempts, status_code=None, details=None):
        super().__init__(message)
        self.error_type = error_type
        self.attempts = attempts
        self.status_code = status_code
        self.details = details

class PaymentEndpoint(BaseAPIClient):
    PATH = 'payments/'

    def process_payment(self, payment, idempotency_key=None, max_attempts=3):
        idempotency_key = idempotency_key or str(uuid.uuid4())
        headers = {'Idempotency-Key': idempotency_key}

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.post(self.PATH, json=payment, headers=headers)
            except requests.Timeout as error:
                if attempt == max_attempts:
                    raise PaymentError(
                        f'Payment timed out after {attempt} attempts: {error}',
                        error_type='timeout',
                        attempts=attempt,
                        details=str(error),
                    ) from error
                continue
            except requests.RequestException as error:
                raise PaymentError(
                    f'Payment request failed: {error}',
                    error_type='connection',
                    attempts=attempt,
                    details=str(error),
                ) from error

            if 200 <= response.status_code < 300:
                return response

            if response.status_code < 500 or attempt == max_attempts:
                raise self._payment_error(response, attempt)

    @staticmethod
    def _payment_error(response, attempts):
        try:
            details = response.json()
        except ValueError:
            details = response.text or None

        try:
            reason = HTTPStatus(response.status_code).phrase
        except ValueError:
            reason = 'Unknown Status'

        error_type = 'client' if response.status_code < 500 else 'server'
        message = f'Payment failed with HTTP {response.status_code} {reason}'
        if details:
            message = f'{message}: {details}'

        return PaymentError(
            message,
            error_type=error_type,
            attempts=attempts,
            status_code=response.status_code,
            details=details,
        )
