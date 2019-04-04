from bs4 import BeautifulSoup
from google.cloud import vision
from google.cloud.vision import types
from urllib.parse import urlparse
import requests
import json
import traceback
import re
import ReviewDataHolder


class ReviewsProcessor:
    def __init__(self, _parent_link):
        self.parent_link = _parent_link
        self.startVal = 0
        self.count = 0
        self.dataHolder = []
        
    def process_scraping(self):
        print("Start scraping...")
        self.startVal = 0
        self.reloadCount = 0
        self.dataHolder.clear()
        while True:
            if self.reloadCount > 4:
                print ("Cannot load the page anymore")
                break
            try:  
                url = self.parent_link + "?start=" + str(self.startVal)
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')
                jsonVal = soup.find(text=re.compile(r'"reviewRating":'))
                if (jsonVal == None):
                    print("no more to parse")
                    break
                reviews = json.loads(str(jsonVal).replace('<script type="application/ld+json">', '').replace('</script>', ''))
                    
                for review in reviews["review"]:
                    data = ReviewDataHolder.ReviewDataHolder()
                    data.setRatingValue(review['reviewRating']['ratingValue'])
                    data.setDatePublished(review['datePublished'])
                    data.setDescription(review['description'])
                    data.setAuthor(review['author'])
                    root_url = urlparse(self.parent_link)
                    root_url = '{uri.scheme}://{uri.netloc}'.format(uri=root_url)
                    image_data = self.process_image_analysis(root_url + str(soup.find_all('img', alt=review['author'])[0].parent["href"]), review['author'])
                    if image_data is not None:
                        data.setImgData(image_data[0],
                                        image_data[1],
                                        image_data[2],
                                        image_data[3],
                                        image_data[4])
                    self.dataHolder.append(data)
                self.startVal = self.startVal + 20
            except Exception:
               traceback.print_exc()
               self.reloadCount = self.reloadCount + 1
               print ("URL " + url + " not loading. Trying to reload..")

    def process_image_analysis(self, user_url, username):
        print("Parsing image at " + user_url)
        load_retries = 0
        while load_retries < 3:
            try:
                page = requests.get(user_url)
                soup = BeautifulSoup(page.content, 'html.parser')
                image_url = soup.find('img', alt=username)["src"]
                data = requests.get(image_url) 
                content = data.content
                client = vision.ImageAnnotatorClient.from_service_account_file('client_secret.json')
                image = vision.types.Image(content=content)
                face_response = client.face_detection(image=image)
                face_content = face_response.face_annotations
                if not face_content:
                    return None
                return [face_content[0].joy_likelihood,
                        face_content[0].sorrow_likelihood,
                        face_content[0].anger_likelihood,
                        face_content[0].surprise_likelihood,
                        face_content[0].under_exposed_likelihood]
                        
            except Exception:
                traceback.print_exc()
                print ("retrying to load")
                load_retries = load_retries + 1
                
        return None
    
    def getReviewsInXML(self):
        xmlContent = "<root>\r\n"
        for data in self.dataHolder:
            xmlContent = xmlContent + "  <reviewData>\r\n"
            xmlContent = xmlContent + "    <ratingValue>" + str(data.ratingValue) + "</ratingValue>\r\n"
            xmlContent = xmlContent + "    <datePublished>" + str(data.datePublished) + "</datePublished>\r\n"
            xmlContent = xmlContent + "    <description>" + str(data.description) + "</description>\r\n"
            xmlContent = xmlContent + "    <author>" + str(data.author) + "</author>\r\n"
            xmlContent = xmlContent + "    <joy_likelihood>" + str(data.joy_likelihood) + "</joy_likelihood>\r\n"
            xmlContent = xmlContent + "    <sorrow_likelihood>" + str(data.sorrow_likelihood) + "</sorrow_likelihood>\r\n"
            xmlContent = xmlContent + "    <anger_likelihood>" + str(data.anger_likelihood) + "</anger_likelihood>\r\n"
            xmlContent = xmlContent + "    <surprise_likelihood>" + str(data.surprise_likelihood) + "</surprise_likelihood>\r\n"
            xmlContent = xmlContent + "    <under_exposed_likelihood>" + str(data.under_exposed_likelihood) + "</under_exposed_likelihood>\r\n"
            xmlContent = xmlContent + "  </reviewData>\r\n"
        xmlContent = xmlContent + "</root>\r\n"
        return xmlContent

    def getReviewsInJSON(self):
        jsonContent = '[\r\n'
        for data in self.dataHolder:
            jsonContent = jsonContent + '  {\r\n'
            jsonContent = jsonContent + '    "ratingValue":' + str(data.ratingValue) + ', \r\n'
            jsonContent = jsonContent + '    "datePublished":"' + str(data.datePublished) + '", \r\n'
            jsonContent = jsonContent + '    "description":"' + str(data.description).replace('"','\\"').replace("\r","").replace("\n","") + '", \r\n'
            jsonContent = jsonContent + '    "author":"' + str(data.author) + '", \r\n'
            jsonContent = jsonContent + '    "joy_likelihood":' + str(data.joy_likelihood) + ', \r\n'
            jsonContent = jsonContent + '    "sorrow_likelihood":' + str(data.sorrow_likelihood) + ', \r\n'
            jsonContent = jsonContent + '    "anger_likelihood":' + str(data.anger_likelihood) + ', \r\n'
            jsonContent = jsonContent + '    "surprise_likelihood":' + str(data.surprise_likelihood) + ', \r\n'
            jsonContent = jsonContent + '    "under_exposed_likelihood":' + str(data.under_exposed_likelihood) + '\r\n'
            jsonContent = jsonContent + '   } ,\r\n'
        jsonContent = jsonContent[0:-4] + '\r\n'
        jsonContent = jsonContent + ']\r\n'
        return jsonContent
        
    def getReviewData(self):
        return self.dataHolder


#rp = ReviewsProcessor("https://www.yelp.com")
#rp.process_image_analysis("https://www.yelp.com/user_details?userid=sCQLm8A4m8bKUkDmzCQNnw", "Jezelle O.")
#rp.process_scraping("https://www.yelp.com", "peoples-bistro-san-francisco-4")
#print (len(rp.getReviewData()))