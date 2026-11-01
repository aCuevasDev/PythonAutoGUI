class Button:
    def __init__(self, image_path, confidence=0.85, resolution=(1280, 720)):
        self.image_path = image_path
        self.confidence = confidence
        self.resolution = resolution