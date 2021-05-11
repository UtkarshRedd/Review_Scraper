import mysql.connector
import nltk
nltk.download('punkt')

mydb = mysql.connector.connect(
  host="localhost",
  user="maheshavel",
  password="2308"
)

#print(mydb)


#print(list("https://www.amazon.in/Huggies-Wonder-Pants-Diaper-Counts/product-reviews/B07R7RG8L7/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews".split("/")))
