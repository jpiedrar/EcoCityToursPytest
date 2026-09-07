from unittest.mock import Mock, patch

from endpoints.payment import PaymentEndpoint

PAYMENT_URL = 'mockedapi.com/api/payments/'
PAYMENT = {'reservationId': 123, 'amount': 100}
IDEMPOTENCY_KEY = 'reservation-123-payment'

def mock_response(status_code, body):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = body
    return response

@patch('requests.post')
def test_payment_succeeds_on_first_attempt(mock_post):
    mock_post.return_value = mock_response(
        200, {'status': 'processed', 'paymentId': 456}
    )

    response = PaymentEndpoint().process_payment(
        PAYMENT_URL, PAYMENT, idempotency_key=IDEMPOTENCY_KEY
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'processed'
    mock_post.assert_called_once_with(
        PAYMENT_URL,
        json=PAYMENT,
        headers={'Idempotency-Key': IDEMPOTENCY_KEY},
    )


@patch('requests.post')
def test_payment_retries_with_same_idempotency_key_and_processes_once(mock_post):
    failed = mock_response(500, {'status': 'failed'})
    processed = mock_response(200, {'status': 'processed', 'paymentId': 456})
    mock_post.side_effect = [failed, processed]

    response = PaymentEndpoint().process_payment(
        PAYMENT_URL, PAYMENT, idempotency_key=IDEMPOTENCY_KEY
    )

    assert response is processed
    assert response.json()['status'] == 'processed'
    assert mock_post.call_count == 2
    assert [call.kwargs['headers']['Idempotency-Key'] for call in mock_post.call_args_list] == [
        IDEMPOTENCY_KEY,
        IDEMPOTENCY_KEY,
    ]
    assert sum(
        result.json()['status'] == 'processed' for result in (failed, processed)
    ) == 1


@patch('requests.post')
def test_payment_is_not_processed_after_three_failed_attempts(mock_post):
    failures = [mock_response(500, {'status': 'failed'}) for _ in range(3)]
    mock_post.side_effect = failures

    response = PaymentEndpoint().process_payment(
        PAYMENT_URL, PAYMENT, idempotency_key=IDEMPOTENCY_KEY
    )

    assert response is failures[-1]
    assert response.json()['status'] == 'failed'
    assert mock_post.call_count == 3
    assert all(
        call.kwargs['headers']['Idempotency-Key'] == IDEMPOTENCY_KEY
        for call in mock_post.call_args_list
    )
    assert all(result.json()['status'] != 'processed' for result in failures)
