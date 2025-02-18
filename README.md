

# MealSelector

To launch, go into the root directory and run

    pip install -r requirements.txt

## Run as an application

Once the requirements are installed, use the following commands to launch the server

    python main.py

## Run as a service

    sudo cp meal-selector.service /lib/systemd/system/meal-selector.service
    sudo systemctl enable meal-selector
    sudo systemctl start meal-selector
    sudo systemctl status meal-selector
