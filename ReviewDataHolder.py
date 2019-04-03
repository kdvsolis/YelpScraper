class ReviewDataHolder:
    def __init__(self):
        self.ratingValue = 0
        self.datePublished = ""
        self.description = ""
        self.author = ""
        self.joy_likelihood = 0
        self.sorrow_likelihood = 0
        self.anger_likelihood = 0
        self.surprise_likelihood = 0
        self.under_exposed_likelihood = 0
        
        
    def setRatingValue(self, ratingValue):
        self.ratingValue = ratingValue
        
    def setDatePublished(self, datePublished):
        self.datePublished = datePublished
        
    def setDescription(self, description):
        self.description = description
        
    def setAuthor(self, author):
        self.author = author
        
    def setImgData(self, 
                   _joy_likelihood,
                   _sorrow_likelihood,
                   _anger_likelihood,
                   _surprise_likelihood,
                   _under_exposed_likelihood):

        self.joy_likelihood = _joy_likelihood
        self.sorrow_likelihood = _sorrow_likelihood
        self.anger_likelihood = _anger_likelihood
        self.surprise_likelihood = _surprise_likelihood
        self.under_exposed_likelihood = _under_exposed_likelihood
        
    def getReviewVal(self, var):
        if(var == "ratingValue"):
            return self.ratingValue
        if(var == "datePublished"):
            return self.datePublished
        if(var == "description"):
            return self.description
        if(var == "datePublished"):
            return self.datePublished
        if(var == "description"):
            return self.description
        if(var == "image_data"):
            return [self.joy_likelihood,
                    self.sorrow_likelihood,
                    self.anger_likelihood,
                    self.surprise_likelihood,
                    self.under_exposed_likelihood]