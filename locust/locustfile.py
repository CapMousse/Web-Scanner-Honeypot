import random
import string
from locust import HttpUser, task, between

class HoneyPot(HttpUser):
  wait_time = between(1, 5)

  @task
  def random_get(self):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(20))
    self.client.get(f"/{result_str}")