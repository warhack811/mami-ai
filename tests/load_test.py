from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def send_chat_message(self):
        # Simulate a user sending a message
        self.client.post("/api/v1/chat/chat", json={"message": "Hello Mami AI, how are you?"}, params={"user_id": 1})

    @task(1)
    def check_health(self):
        self.client.get("/health")
