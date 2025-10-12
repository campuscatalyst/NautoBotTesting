from nautobot.apps import jobs
import requests

name = "POC"

class ArubaCentralIntegrationJob(jobs.Job):
    class Meta:
        name = "Aruba Central - Device Fetch Test"

    def run(self):
        base_url = "https://api-ap.central.arubanetworks.com"
        access_token = "YwzVJ3hIMY2D2u2XtrgsuEPu9gS5MGnP"

        if not access_token:
            self.logger.error("Access token not found.")
            return 
        
        api_url = f"{base_url}/monitoring/v2/aps"

        self.logger.info(f"Fetching data from ${api_url}")

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(url=api_url, headers=headers)

            if response.status_code == 200:
                parsed_response = response.json()
                self.logger.info(f"Successfully fetched the data")
            else:
                self.logger.error(f"Error while fetching the data")
                return 

        except Exception as e:
            self.logger.error(f"{str(e)}")
            return 


jobs.register_jobs(ArubaCentralIntegrationJob)