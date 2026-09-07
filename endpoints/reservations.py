import requests

class ReservationsEndpoint:
      def post_new_reservation(self, url):
            response = requests.post(url)
            return response