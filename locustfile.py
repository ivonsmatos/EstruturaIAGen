from locust import HttpUser, task

class WebsiteUser(HttpUser):
    @task
    def test_home(self):
        self.client.get("/")

    @task
    def test_generate(self):
        self.client.post("/generate", json={"prompt": "Teste"})