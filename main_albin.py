import numpy as np


def write_file(path, schedule):
    with open(path, 'w') as out_file:
        out_file.write("{}\n".format(len(schedule)))
        for intersection_id, traffic_lights_with_schedule in enumerate(schedule):
            nbr_traffic_lights = len(traffic_lights_with_schedule)

            out_file.write("{}\n{}\n".format(
                intersection_id, nbr_traffic_lights))
            out_file.write("\n".join("{} {}".format(road, time)
                                     for road, time in traffic_lights_with_schedule))
            out_file.write("\n")

    with open(path) as submission:
        return submission.read()


def read_file(path):
    with open(path) as text_file:
        D, I, S, V, F = list(map(int, text_file.readline().split(" ")))
        streets_id = {}
        streets = []
        intersections = [[] for i in range(I)]
        for i in range(S):
            B, E, name, L = text_file.readline().split(" ")
            streets_id[name] = i
            streets.append((name, int(B), int(E), int(L)))
            intersections[int(E)].append(i)
        cars = []
        for i in range(V):
            names = text_file.readline().strip().split(" ")
            cars.append(names[1:])
    return D, I, S, V, F, streets, streets_id, cars, intersections


def simple(I, D, streets, street_ids, cars, intersections):
    street_count = np.zeros(len(streets))
    for car in cars:
        weight = 1 / np.sum([streets[street_ids[street]][3] for street in car])
        for roadname in car:
            street_count[street_ids[roadname]] += 1 + D * weight / 10

    schedules = []
    for i in range(I):
        incoming = street_count[intersections[i]]
        if np.sum(incoming) == 0.0:
            schedules.append([(streets[intersections[i][0]][0], D)])
            continue
        incoming = incoming / np.sum(incoming) * len(incoming) * 1.2
        schedules.append([])
        for i, street_id in enumerate(intersections[i]):
            street_name = streets[street_id][0]
            street_time = incoming[i]
            if street_time > 0:
                schedules[-1].append((street_name,
                                      int(np.round(np.clip(street_time, 1, D)))))
        #sorted(schedules[-1], key=lambda x: x[1])
    return schedules


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
        print(path)
        D, I, S, V, F, streets, streets_id, cars, intersections = read_file(
            path + ".txt")
        schedules = simple(I, D, streets, streets_id, cars, intersections)
        write_file(path + ".out", schedules)


if __name__ == "__main__":
    main()
