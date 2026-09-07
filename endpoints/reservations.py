from endpoints.api_client import APIClient

class ReservationsEndpoint(APIClient):
    PATH = 'reservations/'

    def post_new_reservation(self):
        return self.post(self.PATH)
