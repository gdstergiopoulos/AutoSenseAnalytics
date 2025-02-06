from car import Car
import requests
import time
from fiware_to_influx import sync_indluxdb

def init_cars(num_cars):
    cars = []
    for i in range(num_cars+1):
        cars.append(Car(i))
        print(f"Car {i} created")
    return cars


def main():
    #maybe check how many paths (=>cars) are there
    cars = init_cars(7)

    while True:
        for car in cars:
            car.post_data()
            sync_indluxdb(car.car_id)
        time.sleep(2)
    

main()