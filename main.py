import numpy as np


class RoadNet:
    def __init__(self):
        pass


class Intersection:
    def __init__(self, instreets, outstreets):
        self.instreets = instreets
        self.traficlights = [False] * len(instreets)
        self.outstreets = outstreets

    def set_green(self, street_name):
        pass

    def set_schedule(self, schedules):
        self.green_index = 0
        instreet_names = [street.name for street in self.instreets]
        green_street_indexs = [instreet_names.index(
            name) for name, _ in schedules]
        self.schedules = list(
            zip(green_street_indexs, [s[1] for s in schedules]))
        self.green_instreet_index = schedules[0][0]
        self.time_until_light_change = schedules[0][1]
        self.schedule = schedules

    def step(self):
        # set green light
        if self.time_until_light_change > 0:
            self.time_until_light_change -= 1
        else:
            self.green_index += 1
            next_schedule = self.schedules[self.green_index % len(
                self.schedules)]
            self.green_instreet_index = next_schedule[0]
            self.time_until_light_change = next_schedule[1]

        for i, street in enumerate(self.instreets):
            street.step(i == self.green_instreet_index)


class Street:
    def __init__(self, start: int, end: int, name: str, length: int):
        self.start_ind = start
        self.end_ind = end
        self.name = name
        self.start = start
        self.end = end
        self.length = length
        self.cars = []

    def add_car(self):
        self.cars.append(car)
        # car.arrives_at = current_time + self.length
        car.time_until_traffic_light = self.length

    def step(self, green: bool):
        for car in self.cars:
            car.step(green)


class Car:
    def __init__(self, streets):
        self.streets = streets
        self.current_street = 0
        self.time_until_traffic_light = 0
        self.finished_at = None
        self.framme_snart = False

    def step(self, green: bool):
        if self.time_until_traffic_light > 0:
            self.time_until_traffic_light -= 1
        elif green:
            current_street = car.streets[car.current_street]
            self.current_street.cars.remove(self)
            self.current_street += 1
            next_street = car.streets[car.current_street]
            next_street.add_car(self)

    def get_score(self, D):
        if self.finished_at is None:
            return 0
        else:
            return self.value + (D - self.finished_at)


def calculate_score(text, D, cars, intersections):
    lines = text.split("\n")
    nbr_intersections_with_schedule = int(lines[0])
    line_id = 1
    for _ in range(nbr_intersections_with_schedule):
        intersection_id = int(lines[line_id])
        line_id += 1
        nbr_streets = int(lines[line_id])
        line_id += 1
        schedule = []
        for _ in range(nbr_streets):
            name, duration = lines[line_id].split(" ")
            schedule.append((name, int(duration)))
            line_id += 1

        intersections[intersection_id].set_schedule(schedule)

        # setup intersection schedules based on text
    for t in range(D):
        # update lights
        for intersection in intersections:
            intersection.step()

    score = 0
    for car in cars:
        score += car.get_score(D)

    return score


def read_file(path):
    with open(path) as text_file:
        D, I, S, V, F = list(map(int, text_file.readline().split(" ")))
        intersections = [([], []) for i in range(I)]
        streets = {}
        for i in range(S):
            B, E, name, L = text_file.readline().split(" ")
            street = Street(int(B), int(E), name.strip(), int(L))
            streets[street.name] = street
            intersections[int(B)][1].append(street)
            intersections[int(E)][0].append(street)

        intersections = [Intersection(instreets, outstreets)
                         for instreets, outstreets in intersections]

        cars = []
        for i in range(V):
            tmp = text_file.readline().split(" ")
            street_track = [streets[name.strip()] for name in tmp[1:]]
            cars.append(Car(street_track))

    return D, I, F, intersections, list(streets.values()), cars


def write_file(path, schedule):
    with open(path, 'w') as out_file:
        out_file.write("{}\n".format(len(schedule)))
        for intersection in schedule:
            intersection_id = intersection[0]
            traffic_lights_with_schedule = intersection[1]
            nbr_traffic_lights = len(traffic_lights_with_schedule)

            if nbr_traffic_lights > 0:
                out_file.write("{}\n{}\n".format(
                    intersection_id, nbr_traffic_lights))
                out_file.write("\n".join(["{} {}".format(road, time)
                                          for road, time in traffic_lights_with_schedule]))
                out_file.write("\n")

    with open(path) as submission:
        return submission.read()


def simple(intersections):
    schedule = []
    for i, intersection in enumerate(intersections):
        street_schedule = list(
            zip([street.name for street in intersection.instreets], [1] * len(intersection.instreets)))
        schedule.append((i, street_schedule))
    return schedule


def better(cars, streets, intersections):
    schedule = []
    streets_counts = [0] * len(streets)
    for car in cars:
        pass
    for i, intersection in enumerate(intersections):
        street_schedule = list(
            zip([street.name for street in intersection.instreets], [1] * len(intersection.instreets)))
        schedule.append((i, street_schedule))
    return schedule


def adrian_better(intersections, streets, cars, D):
    street_count = {street.name: 0 for street in streets}
    for car in cars:
        for street in car.streets:
            street_count[street.name] += 1

    scale = 5
    schedule = []
    for i, intersection in enumerate(intersections):
        instreet_names = [street.name for street in intersection.instreets]
        instreet_count = np.array([street_count[name]
                                   for name in instreet_names])
        the_sum = np.min(instreet_count)
        if the_sum > 0:
            normed_counts = instreet_count / the_sum
            normed_counts[normed_counts < 0.1] = np.inf
            min_reasonable_val = np.min(normed_counts)
            if min_reasonable_val > 0:
                scaled_counts = (
                    normed_counts / min_reasonable_val).astype(int)
                scaled_counts[scaled_counts >= D] = D
            else:
                scaled_counts = normed_counts.astype(int)
            new_sched = []
            for name, time in zip(instreet_names, scaled_counts):
                if time > 0:
                    new_sched.append([name, time])
            schedule.append([i, new_sched])
    return schedule


def fastest_cars(intersections, streets, cars, D):
    distances = np.zeros(len(cars))
    for i, car in enumerate(cars):
        distance = 0
        for street in car.streets:
            distance += street.length
        distances[i] = distance

    fastest = np.argsort(distances)[::-1]

    schedule = {idx: [] for idx, intersection in enumerate(intersections)}
    for car_idx in fastest:
        car = cars[car_idx]
        for street in car.streets:
            if len(schedule[street.end_ind]) > 0:
                pass
            else:
                schedule[street.end_ind].append([street.name, 1])
    return list(schedule.items())


def main():
    paths = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
    ]
    for path in paths:
        D, I, F, intersections, streets, cars = read_file(path + ".txt")
        # Create classes
        # result = adrian_better(intersections, streets, cars, D)
        result = fastest_cars(intersections, streets, cars, D)
        text_result = write_file(path + ".out", result)
        print(path)
        # score = calculate_score(text_result, D, cars, intersections)
        # print(score)


if __name__ == "__main__":
    main()
