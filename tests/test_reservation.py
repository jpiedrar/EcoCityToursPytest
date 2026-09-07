from unittest.mock import patch
from endpoints.reservations import ReservationsEndpoint

RESERVATION_CONTRACT = {
    'name': str,
    'reservationId': int,
    'date': str,
    'amountOfPeople': int,
    'status': str,
    'message': str,
}

def assert_reservation_contract(body):
    assert set(body) == set(RESERVATION_CONTRACT)
    for field, expected_type in RESERVATION_CONTRACT.items():
        assert isinstance(body[field], expected_type), (
            f"{field} must be {expected_type.__name__}"
        )

@patch('requests.post')
def test_new_reservation(mock_post):
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'name': 'Juan Piedra', 
        'reservationId': 123, 
        'date': 'sept 6',
        'amountOfPeople': 5,
        'status': 'booked',
        'message': 'created'
    }
    client = ReservationsEndpoint(base_url='mockedapi.com/api/')
    reservation = client.post_new_reservation()
    body = reservation.json()

    assert_reservation_contract(body)
    assert body['name'] == 'Juan Piedra'
    assert body['reservationId'] == 123
    assert body['status'] == 'booked'
    assert reservation.status_code == 200
    mock_post.assert_called_once_with(
        'mockedapi.com/api/reservations/', timeout=10.0
    )

@patch('requests.post')
def test_no_reservation_available(mock_post):
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'name': 'Juan Piedra',
        'reservationId': None,
        'date': 'Sept 7',
        'amountOfPeople': 0,
        'status': 'invalid',
        'message': 'There is no room for the reservation'
    }
    client = ReservationsEndpoint(base_url='mockedapi.com/api/')
    reservation = client.post_new_reservation()

    assert reservation.json()['name'] == 'Juan Piedra'
    assert reservation.json()['reservationId'] is None
    assert reservation.json()['status'] == 'invalid'
    assert reservation.json()['message'] == 'There is no room for the reservation'
    assert reservation.status_code == 200
    mock_post.assert_called_once_with(
        'mockedapi.com/api/reservations/', timeout=10.0
    )