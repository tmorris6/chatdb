import requests # type: ignore
import mysql.connector
from tabulate import tabulate # type: ignore
from openai import OpenAI

OpenAiKey = "" # INPUT OUR OWN OPENAI SK-KEY HERE
client = OpenAI(api_key=OpenAiKey)


# These schemas are set up based on my mysql databases that I have formatted in MySQLWorkbench
schemas = {
    "1": {
        "name": "chatdb",
        "schema": """
        - crime(division_number, date_reported, date_occurred, area_code, reporting_distance, part, crime_code, modus_operandi, victim_age, victim_sex, victim_descent, premise_code, premise_description, weapon_code, weapon_description, status, status_description, location, cross_street, latitude, longitude) 
        - area(Code, `Area Name`) 
        - crime_code(code, description)
        """
    },
    "2": {
        "name": "movies_db",
        "schema": """
        - movies(show_id, type, title, director, cast, country, date_added, release_year, rating_code, duration, listed_in, description)
        - rating(rating, rating_code)
        """
    },
    "3":{
        "name": "games_db",
        "schema": """
        - games(game_id, meta_score, title, platform_code, date, user_score, link, esrb_rating, developers, genres, release_year)
        - platform(platform, platform_code)
        """
    }
}



def translate_to_sql(nl_query, schema_text):
    # The prompt starts with the basic set-up for the task, which is the first two lines
    # The extra rules and the line after that were added because of flaws with different models in testing.
    prompt = f""" 
    I am working on a natural language interface for a MySQL database.

    I will give you a natural language question, and based on the provided schema, I want you to output only one valid MySQL query and nothing else.

    Extra rules:
    - Do not include explanations.
    - Do not include multiple questions or examples.
    - Avoid joins unless they are explicitly requested.
    - Use only the table and column names exactly as shown.
    - Some fields may contain empty strings ('') in addition to NULL. To check if a value exists, use: `column IS NOT NULL AND column != ''`

    If the user asks for sample rows, show 5 rows

    Schema:
    {schema_text}

    Question: {nl_query}
    SQL:
    """

    # we then run a try except chain with calling the model
    # the client.chat.completions.create() is from the OpenAI doucmentation
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system",
                 "content": "You convert natural language to MySQL queries using the schema provided"},
                 {"role": "user", "content": prompt}
            ],
            temperature = 0,
            max_tokens = 150
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI error: {e}"




def run_sql(sql_query, db_name):
    mysqlpass = "" # ADD YOUR MYSQL PASSWORD HERE


    try:
        # these settings are for connecting to my mySQLWorkbench. Usually these are the default for running on your local machine so I left them in and removed my password
        conn = mysql.connector.connect(
            host= "localhost",
            port= 3306,
            user= "root",
            password= mysqlpass,
            database= db_name
        )
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # this if else block checks if it is a read or a write query
        # if its a write query dont try to return anything, if its a read - return the results
        if sql_query.strip().lower().startswith(("select", "show", "describe")):
            rows = cursor.fetchall()
            headers = [i[0] for i in cursor.description]
            if not rows:
                print("Query returned no results")
            else:
                print(tabulate(rows[:10], headers=headers, tablefmt="grid"))
        else:
            conn.commit()
            print("Modification successful")

        cursor.close()
        conn.close()
    
    except mysql.connector.Error as err:
        print(f"mysql error: {err}")
        return []



# a helper function specifically for openAI. The outputs would start with ``` and it was messing with my run_sql function
# so this essentially splits the output from openAI to a readable sql query
def clean_sql(sql):
    sql = sql.strip()
    if sql.startswith("```sql"):
        sql = sql.replace("```sql","").strip()
    if sql.endswith("```"):
        sql = sql[:-3].strip()
    return sql.strip()


# the main block just asks which db the user wants to use, and then selects that schema for the NL context to openAI
# then runs the two different functions for translation and running/returning
if __name__ == "__main__":
    print("Which database would you like to use?")
    print("1. Crimes DB\n 2. Movies DB\n 3. Games DB\n")

    choice = input("Enter 1, 2, or 3: ").strip()

    if choice not in schemas:
        print("Please try again and chose an available DB")
        exit()

    db_info = schemas[choice]
    db_name  = db_info["name"]
    schema_text = db_info["schema"]

    user_query = input("\nWhat is your natural language query?\n> ")
    sql = translate_to_sql(user_query, schema_text)
    sql = clean_sql(sql)
    print(f"\nSQL generated: \n{sql}\n")

    run_sql(sql, db_name)