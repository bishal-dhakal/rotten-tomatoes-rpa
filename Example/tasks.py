from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium
from robot.libraries.BuiltIn import BuiltIn
import traceback
import pandas as pd
import time
import sqlite3

movies = []
browser = Selenium()


def mainWork():
    try:
        df = pd.read_excel("../movies.xlsx")
        movie = df["Movie"]

        for m in movie:
            movies.append(m)

        conn = sqlite3.connect('imdb.db')
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        movie_name TEXT,
        tomatometer_score TEXT,
        audience_score TEXT,
        storyline TEXT,
        genres TEXT,
        rating TEXT,
        review_1 TEXT,
        review_2 TEXT,
        review_3 TEXT,
        review_4 TEXT,
        review_5 TEXT,
        status TEXT
        )""")

        browser.open_available_browser("https://www.rottentomatoes.com/", maximized=True)
        
        searchbox_path = '//input[@class="search-text"]'
        movie_list_path ='//search-page-result[@type="movie"]//ul'
        movie_name_path ='//search-page-result[@type="movie"]//ul//a[2]'
        score_detail_path = '//score-details-critics'
        audience_path ='//score-details-audience'
        storyline_path ='//section[@id="movie-info"]//p'
        rating_path ='//section[@id="movie-info"]//ul//p/span'
        genre_path = '//section[@id="movie-info"]//ul//li[2]//span'
        review_path = '//review-speech-balloon'


        #movies
        for movie in movies:
            print(f'Searching on movie { movie }')
            browser.auto_close = False

            #search
            browser.wait_until_element_is_visible(searchbox_path)
            browser.input_text(searchbox_path,movie)
            browser.press_keys(None, 'RETURN')
            
            time.sleep(5)
            
            flim_elements = browser.find_elements(movie_name_path)

            for i in flim_elements:
                movie_name = browser.get_text(i)
                
                if movie_name == movie:
                    link = browser.get_element_attribute(locator=i, attribute='href')
                    break
            browser.go_to(link)

            #tomato meter
            tomato=browser.find_element('//score-details-critics')
            tomato_meter = browser.get_element_attribute(tomato,'value')

            #audience_score
            audience=browser.find_element(audience_path)
            audience_score = browser.get_element_attribute(audience,'value')
            
            #storyline
            storyline = browser.get_text(storyline_path)
            
            #rating
            rating = browser.get_text(rating_path)

            #genre
            genre = browser.get_text(genre_path)

            #review
            reviews = []
            

            critic = browser.find_elements(review_path)
            for i in critic:
                critic_review = browser.get_element_attribute(i,'reviewquote')
                reviews.append(critic_review)
            
            
            if(len(reviews) < 5 ):
                for i in range(5-len(reviews)):
                    reviews.append("Not Found")

            BuiltIn().log_to_console(f"My reviews {reviews}")
            
            status = "Success" if len(flim_elements) >= 1 else "No exact match found"

            if(status=='Success') :
                cur.execute("""INSERT INTO movies (movie_name,tomatometer_score,audience_score, storyline, rating, genres, review_1, review_2, review_3, review_4, review_5, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)""",
                (movie,tomato_meter,audience_score, storyline, rating, genre,  reviews[0], reviews[1], reviews[2], reviews[3], reviews[4], status))

            else:
                cur.execute("""INSERT INTO movies (movie_name,tomatometer_score,audience_score, storyline, rating, genres, review_1, review_2, review_3, review_4, review_5, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,? ,?)""",
                (movie,"Not Found","Not Found","Not Found", "Not Found", "Not Found", "Not Found", 'Not Found', "Not Found", 'Not Found', 'Not Found', status))

            conn.commit()

            print(f'{ movie } added to database')

        browser.close_browser()
    except Exception as e:
        print(e)
        print(traceback.format_exc())

@task
def minimal_task():
    mainWork()
