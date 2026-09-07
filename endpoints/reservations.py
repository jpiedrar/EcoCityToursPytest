from endpoints.base_api import BaseAPIClient

class ReservationsEndpoint(BaseAPIClient):
    PATH = 'reservations/'

    def post_new_reservation(self):
        return self.post(self.PATH)
