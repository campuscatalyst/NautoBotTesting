from nautobot.apps.jobs import Job, register_jobs, StringVar

name = "Examples"                 # Grouping shown in the UI

class HelloWorldJob(Job):
    class Meta:
        name = "Hello World"      # Job name

    who = StringVar(         # One user‑supplied variable
        description="Whom should we greet?",
        default="world",
    )

    def run(self, *, who):
        self.logger.info("Hello, %s!", who)  # This is the logic that runs when the Job is executed

register_jobs(HelloWorldJob) # <- required in Nautobot 2.x