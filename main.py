from flask import Flask, render_template, request
import csv
from random import randrange
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def main():
    meals = get_all_meals_from_csv()
    random_meals = pick_random_meals(meals)
    return render_template('index.html',  random_meals=random_meals, enumerate=enumerate)


@app.route('/generate-meals', methods=['POST'])
def generate_meals():
    meals = get_all_meals_from_csv()
    random_meals = pick_random_meals(meals)
    return render_template('index.html', random_meals=random_meals, enumerate=enumerate)


@app.route('/add-meal', methods=['POST'])
def add_meal():
    meals = get_all_meals_from_csv()
    meal_names = [meal[0].lower() for meal in meals if meal]
    message = None
    if request.form['meal'].lower() in meal_names:
        message = f"Error! meal with name {request.form['meal']} already exists!"

    if not message:
        with open('meals.csv', 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                request.form['meal'],
                request.form['protein'],
                request.form['carb'],
                request.form['sauce'],
                request.form['veg'],
                request.form['optional_veg'],
                request.form['recipe_links'],
                request.form['season'],
            ])
        message= f"meal with name {request.form['meal']} added successfully"

    meals = get_all_meals_from_csv()
    return render_template('all_meals.html', meals=meals, enumerate=enumerate, message=message)


@app.route('/delete-meal', methods=['POST'])
def delete_meal():
    meals = get_all_meals_from_csv()
    meal_names = [meal[0].lower() for meal in meals if meal]
    message = None
    if request.form['meal'].lower() not in meal_names:
        message = f"Error! meal with name {request.form['meal']} doesn't exist!"

    if not message:
        meals_to_keep = [meal for meal in meals if meal and meal[0].lower() != request.form['meal'].lower()]
        with open('meals.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(meals_to_keep)
        message= f"meal with name {request.form['meal']} deleted successfully"

    meals = get_all_meals_from_csv()
    return render_template('all_meals.html', meals=meals, enumerate=enumerate, message_2=message)


@app.route('/get-all-meals')
def get_all_meals():#
    meals = get_all_meals_from_csv()
    return render_template('all_meals.html', meals=meals, enumerate=enumerate)


def current_season():
    month = datetime.now().month
    # October to April is Winter, May to September is Summer
    if month >= 10 or month <= 4:
        return 'Winter'
    return 'Summer'


def meal_matches_season(meal: list, season: str):
    if len(meal) <= 7:
        return True
    meal_season = meal[7].strip().title()
    return meal_season in ('Either', season, '')


def pick_random_meals(meals: list):
    header = meals[0]
    season = current_season()
    meal_rows = [meal for meal in meals[1:] if meal]
    allowed_meals = [meal for meal in meal_rows if meal_matches_season(meal, season)]
    if not allowed_meals:
        allowed_meals = meal_rows

    selected_meals = [header]
    if len(allowed_meals) <= 7:
        selected_meals.extend(allowed_meals)
        return selected_meals

    while len(selected_meals) < 8:
        random_number = randrange(0, len(allowed_meals))
        selected_meal = allowed_meals[random_number]
        if selected_meal not in selected_meals:
            selected_meals.append(selected_meal)

    return selected_meals
    


def get_all_meals_from_csv():
    with open('meals.csv') as csv_file:
        reader = csv.reader(csv_file)
        meals = [r for r in reader if len(r) > 0]
    header = meals.pop(0)
    meals = sorted(meals, key=lambda x: x[0])
    meals.insert(0, header)
    return meals


if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0')
