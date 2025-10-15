from nautobot.apps import jobs
from nautobot.dcim.models import Manufacturer, DeviceType, Device, Location, LocationType
from nautobot.extras.models.roles import Role
from nautobot.extras.models.statuses import Status
from nautobot.ipam.models import IPAddress, Prefix
import requests

name = "POC"

aruba_to_nautobot_status = {
    "Up": "Active",
    "Down": "Offline",
    "Provisioning": "Planned",
}

class ArubaCentralIntegrationJob(jobs.Job):
    class Meta:
        name = "Aruba Central - Device Fetch Test"

    def run(self):
        base_url = "https://api-ap.central.arubanetworks.com"
        access_token = "Asel81I9LKctwXXpSXT24JWD5pLF4kYI"

        if not access_token:
            self.logger.error("Access token not found.")
            return 
        
        api_url = f"{base_url}/monitoring/v2/aps"

        self.logger.info(f"Fetching data from {api_url}")

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            manufacturer, _ = Manufacturer.objects.get_or_create(name="Aruba")
            device_role, _ = Role.objects.get_or_create(name="Access Point")

            self.logger.info([f.name for f in Device._meta.fields])
            self.logger.info([f.name for f in LocationType._meta.get_fields()])
            self.logger.info([f.name for f in Location._meta.get_fields()])

            response = requests.get(url=api_url, headers=headers)

            if response.status_code == 200:
                parsed_response = response.json()
                aps = parsed_response.get("aps")
                self.logger.info(f"Successfully fetched the data")

                for ap in aps:
                    name = ap.get("name") or ap.get("serial")
                    serial = ap.get("serial")
                    model = ap.get("model", "Unknown")
                    ip_addr = ap.get("ip_address")
                    aruba_status = ap.get("status", "Up")
                    nautobot_status_name = aruba_to_nautobot_status.get(aruba_status, "Planned")
                    status_name = Status.objects.get(name__iexact=nautobot_status_name)
                    location_status = Status.objects.get(name__iexact="Active")


                    loc_type, _ = LocationType.objects.get_or_create(name="Site")

                    location, _ = Location.objects.get_or_create(
                        name="Hyderabad HQ",
                        location_type=loc_type,
                        defaults={
                            "description": "Main Hyderabad office",
                            "status": location_status,
                        }
                    )

                
                    device_type, _ = DeviceType.objects.get_or_create(
                        manufacturer=manufacturer,
                        model=model
                    )

                    device, created = Device.objects.get_or_create(
                        name=name,
                        defaults={
                            "device_type": device_type,
                            "role": device_role,
                            "status": status_name,
                            "serial": serial,
                            "location": location
                        }
                    )

                    if created:
                        self.logger.info(f"Created {device.name}")
                    else:
                        self.logger.info(f"Device already exists: {device.name}")

                    # if ip_addr:
                    #     ip_obj, _ = IPAddress.objects.get_or_create(address=f"{ip_addr}/32")
                    #     device.primary_ip4 = ip_obj
                    #     device.save()
                    
                    self.logger.info("Successfully added device into nautobot")

            else:
                self.logger.error(f"Error while fetching the data")
                return 

        except Exception as e:
            self.logger.error(f"{str(e)}")
            return 


jobs.register_jobs(ArubaCentralIntegrationJob)
