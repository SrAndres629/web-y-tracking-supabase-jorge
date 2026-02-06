import requests

class ContentManager:
    def __init__(self):
        self._FALLBACKS = {
            'service1': {'url': 'https://service1.example.com/api', 'timeout': 30},
            'service2': {'url': 'https://service2.example.com/api', 'timeout': 30},
            # ... Add complete service data structure here
        }

    def get_service_info(self, service_name):
        return self._FALLBACKS.get(service_name, None)

    # Add additional methods as necessary
