class FeatureExtraction:
    def __init__(self, url):
        self.url = url

    def getFeaturesList(self):
        features = []

        # Feature 1: Uses HTTPS
        features.append(1 if self.url.startswith("https://") else 0)

        # Feature 2: URL length
        features.append(len(self.url))

        # Feature 3: Contains '@'
        features.append(1 if '@' in self.url else 0)

        # Feature 4: Contains '-'
        features.append(1 if '-' in self.url else 0)

        # Feature 5: Number of dots
        features.append(self.url.count('.'))

        return features