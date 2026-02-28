import random
import time
import uuid

from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Fast requests for 1000/min target

    def on_start(self):
        # Generate a consistent user for this session
        self.user_data = {
            "client_ip_address": "127.0.0.1",
            "client_user_agent": "Locust/LoadTest",
            "external_id": str(uuid.uuid4()),
            "email": f"loadtest_{random.randint(1000, 9999)}@example.com",
            "phone": "59170000000",
        }

    @task(3)
    def page_view(self):
        event_id = f"evt_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        payload = {
            "event_name": "PageView",
            "event_time": int(time.time()),
            "event_id": event_id,
            "event_source_url": "https://jorgeaguirreflores.com/home",
            "action_source": "website",
            "user_data": self.user_data,
            "custom_data": {"load_test": True},
        }
        self.client.post("/api/v1/telemetry", json=payload)

    @task(1)
    def lead_submission(self):
        event_id = f"evt_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        payload = {
            "event_name": "Lead",
            "event_time": int(time.time()),
            "event_id": event_id,
            "event_source_url": "https://jorgeaguirreflores.com/contact",
            "action_source": "website",
            "user_data": self.user_data,
            "custom_data": {"load_test": True, "value": 100.0, "currency": "BOB"},
        }
        self.client.post("/api/v1/telemetry", json=payload)
