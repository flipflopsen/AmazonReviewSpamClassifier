class ReviewData:
    def __init__(self, review_text, helpful=None, not_helpful=None, stars=None):
        self.review_text = review_text
        self.helpful = helpful
        self.not_helpful = not_helpful
        self.stars = stars
