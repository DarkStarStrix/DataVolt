class Monitor:
    def log(self, message):
        print(f"[LOG] {message}")

    def alert(self, issue):
        print(f"[ALERT] {issue}")
