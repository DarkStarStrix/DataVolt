import pickle

class VersionManager:
    def save_version(self, obj, version):
        with open(f"{version}.pkl", "wb") as f:
            pickle.dump(obj, f)

    def load_version(self, version):
        with open(f"{version}.pkl", "rb") as f:
            return pickle.load(f)
