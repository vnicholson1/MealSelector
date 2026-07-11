from flask import Flask, render_template, request, redirect, url_for
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


@app.route('/edit-meal')
def edit_meal():
    meal_name = request.args.get('meal', '').strip()
    meals = get_all_meals_from_csv()
    selected_meal = None

    for meal in meals[1:]:
        if meal and meal[0].lower() == meal_name.lower():
            selected_meal = meal
            break

    if not selected_meal:
        return redirect(url_for('get_all_meals'))

    return render_template('edit_meal.html', meal=selected_meal, original_meal=meal_name, enumerate=enumerate)


@app.route('/update-meal', methods=['POST'])
def update_meal():
    meals = get_all_meals_from_csv()
    meal_names = [meal[0].lower() for meal in meals if meal]
    message = None

    original_meal = request.form.get('original_meal', '').strip()
    new_meal_name = request.form.get('meal', '').strip()

    if not original_meal:
        message = 'Error! Please provide a meal name to update.'
    elif original_meal.lower() not in meal_names:
        message = f"Error! meal with name {original_meal} doesn't exist!"
    elif not new_meal_name:
        message = 'Error! Please provide a meal name.'
    elif new_meal_name.lower() in meal_names and new_meal_name.lower() != original_meal.lower():
        message = f"Error! meal with name {new_meal_name} already exists!"

    if not message:
        updated_meal = [
            new_meal_name,
            request.form['protein'],
            request.form['carb'],
            request.form['sauce'],
            request.form['veg'],
            request.form['optional_veg'],
            request.form['recipe_links'],
            request.form['season'],
        ]

        updated_meals = []
        for meal in meals:
            if meal and meal[0].lower() == original_meal.lower():
                updated_meals.append(updated_meal)
            else:
                updated_meals.append(meal)

        with open('meals.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(updated_meals)
        return redirect(url_for('get_all_meals', message_3=f"Meal '{new_meal_name}' updated successfully"))

    return render_template('edit_meal.html', meal=[new_meal_name, request.form.get('protein',''), request.form.get('carb',''), request.form.get('sauce',''), request.form.get('veg',''), request.form.get('optional_veg',''), request.form.get('recipe_links',''), request.form.get('season','')], original_meal=original_meal, enumerate=enumerate, message=message)


@app.route('/get-all-meals')
def get_all_meals():
    meals = get_all_meals_from_csv()
    return render_template('all_meals.html', meals=meals, enumerate=enumerate, message_3=request.args.get('message_3', ''))


def current_season():
    month = datetime.now().month
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
