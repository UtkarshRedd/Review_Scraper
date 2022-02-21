# ReviewScraper

**Instructions**

**1. Redis Queue Managemant command**
Open a terminal and run 'rq worker'

**2. Run Flask APP command**
Open another terminal and run 'export FLASK_APP=app.main:app && flask run --reload'

**3. Create a MySQL database with one table**

The table Schema:

review1(
jod_id LONGTEXT,
time LONGTEXT,
filename LONGTEXT,
retailer VARCHAR(10),
url LONGTEXT,
status LONGTEXT)

4. Specify the db credentials in "mysql_connection.py" and "main.py"(inside fetch function) files



The app has two-fold functionality as mentioned below.
1. Natural Language Processing (NLP):-
Binary Sentiment Classification model developed in python. Used libraries like NLTK, Sci-kit learn etc.
Used customer review data obtained from PAXCOM (from internal client) as a training dataset. This had around 1lakh reviews of Kimberly-Clark products.
Employed various mechanisms like TF-IDF and Topic Modelling, to find the most frequently occurring features in a negative review.
Employed Naïve Bayes Classifier and Logistic Regression algorithms to predict the Sentiment.
2. Web Scraping
The user should provide the URL of the product and the retailer name. On clicking “get Review” button the customer reviews of that product are downloaded as a CSV file.
This file can then be uploaded to the Sentiment Analysis part of the app which will produce an output with the respective Sentiment scores of all the reviews.

UI Looks like this : -
![image](https://user-images.githubusercontent.com/29978378/154969832-0c453090-4fc9-4252-bbb7-4f14b1a3a13d.png)
![image](https://user-images.githubusercontent.com/29978378/154969860-7dbcd03f-d468-4328-ad6f-15cbfb380279.png)

![image](https://user-images.githubusercontent.com/29978378/154969913-c057e40d-cc12-4eed-98ae-4947b26b1d90.png)


**The Machine Learning model is saved in a pickle file - model.pkl. It is uses the Naive Bayes algorithm for Sentiment Classification. NLP techniques such as Lemmatization, TF-IDF, n-grams and Negation Handling have been incorporated.**
