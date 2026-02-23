class ConsoleChannel:
    def send(self, alert):
        print(f"[ALERT] {alert.severity} | {alert.category} | {alert.message}")
        print(alert.context)
