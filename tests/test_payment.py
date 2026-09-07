from unittest.mock import Mock, patch
import pytest
import requests
from endpoints.payment import PaymentEndpoint, PaymentError

API_BASE_URL = 'mockedapi.com/api/'
PAYMENT_URL = f'{API_BASE_URL}payments/'
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

    response = PaymentEndpoint(base_url=API_BASE_URL).process_payment(
        PAYMENT, idempotency_key=IDEMPOTENCY_KEY
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'processed'
    mock_post.assert_called_once_with(
        PAYMENT_URL,
        json=PAYMENT,
        headers={'Idempotency-Key': IDEMPOTENCY_KEY},
        timeout=10.0,
    )


@patch('requests.post')
def test_payment_retries_with_same_idempotency_key_and_processes_once(mock_post):
    failed = mock_response(500, {'status': 'failed'})
    processed = mock_response(200, {'status': 'processed', 'paymentId': 456})
    mock_post.side_effect = [failed, processed]

    response = PaymentEndpoint(base_url=API_BASE_URL).process_payment(
        PAYMENT, idempotency_key=IDEMPOTENCY_KEY
    )

    assert response is processed
    assert response.json()['status'] == 'processed'
    assert mock_post.call_count == 2
    assert [call.kwargs['headers']['Idempotency-Key'] for call in mock_post.call_args_list] == [
        IDEMPOTENCY_KEY,
        IDEMPOTENCY_KEY,
    ]
    assert mock_post.call_count == 2

@patch('requests.post')
def test_payment_is_not_processed_after_three_failed_attempts(mock_post):
    failures = [mock_response(500, {'status': 'failed'}) for _ in range(3)]
    mock_post.side_effect = failures

    with pytest.raises(PaymentError) as raised_error:
        PaymentEndpoint(base_url=API_BASE_URL).process_payment(
            PAYMENT, idempotency_key=IDEMPOTENCY_KEY
        )

    assert raised_error.value.error_type == 'server'
    assert raised_error.value.status_code == 500
    assert raised_error.value.attempts == 3
    assert raised_error.value.details == {'status': 'failed'}
    assert mock_post.call_count == 3
    assert all(
        call.kwargs['headers']['Idempotency-Key'] == IDEMPOTENCY_KEY
        for call in mock_post.call_args_list
    )
    assert all(result.json()['status'] != 'processed' for result in failures)

@pytest.mark.parametrize("status_code", [500, 502, 503, 504])
@patch("requests.post")
def test_payment_server_errors(mock_post, status_code):
    failures = [mock_response(status_code, {'status': 'failed'}) for _ in range(3)]
    mock_post.side_effect = failures
    
    with pytest.raises(PaymentError) as raised_error: 
        PaymentEndpoint(base_url=API_BASE_URL).process_payment(
            PAYMENT, idempotency_key=IDEMPOTENCY_KEY
        )
    
    assert raised_error.value.error_type == 'server'
    assert raised_error.value.status_code == status_code
    assert raised_error.value.attempts == 3
    assert raised_error.value.details == {'status': 'failed'}
    assert mock_post.call_count == 3
    
@patch('requests.post')
def test_payment_reports_404_without_retrying(mock_post):
    mock_post.return_value = mock_response(
        404, {'error': 'Payment endpoint was not found'}
    )

    with pytest.raises(PaymentError) as raised_error:
        PaymentEndpoint(base_url=API_BASE_URL).process_payment(PAYMENT)

    error = raised_error.value
    assert str(error) == (
        "Payment failed with HTTP 404 Not Found: "
        "{'error': 'Payment endpoint was not found'}"
    )
    assert error.error_type == 'client'
    assert error.status_code == 404
    assert error.attempts == 1
    mock_post.assert_called_once()


@patch('requests.post')
def test_payment_reports_timeout_after_three_attempts(mock_post):
    mock_post.side_effect = requests.Timeout('request timed out')

    with pytest.raises(PaymentError) as raised_error:
        PaymentEndpoint(base_url=API_BASE_URL).process_payment(
            PAYMENT, idempotency_key=IDEMPOTENCY_KEY
        )
    error = raised_error.value
    assert str(error) == 'Payment timed out after 3 attempts: request timed out'
    assert error.error_type == 'timeout'
    assert error.status_code is None
    assert error.attempts == 3
    assert error.details == 'request timed out'
    assert mock_post.call_count == 3
    assert all(
        call.kwargs['headers']['Idempotency-Key'] == IDEMPOTENCY_KEY
        for call in mock_post.call_args_list
    )

@pytest.mark.parametrize(
    "status_code,expected_type,expected_attempts",
    [
        (404, "client", 1), 
        (500, "server", 3),
        (502, "server", 3),
        (503, "server", 3),
        (504, "server", 3),
    ],
)
@patch("requests.post")
def test_payment_server_errors_multiparams(mock_post, status_code, expected_type, expected_attempts):
    failures = [mock_response(status_code, {'status': 'failed'}) for _ in range(expected_attempts)]
    mock_post.side_effect = failures
    
    with pytest.raises(PaymentError) as raised_error: 
        PaymentEndpoint(base_url=API_BASE_URL).process_payment(
            PAYMENT, idempotency_key=IDEMPOTENCY_KEY
        )
    
    assert raised_error.value.error_type == expected_type
    assert raised_error.value.status_code == status_code
    assert raised_error.value.attempts == expected_attempts
    assert raised_error.value.details == {'status': 'failed'}
    assert mock_post.call_count == expected_attempts