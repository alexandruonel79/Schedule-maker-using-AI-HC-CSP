from typing import Dict, Tuple, List
import copy
import random
import sys
from utils import read_yaml_file, pretty_print_timetable
from check_constraints import *

MAX_TEACHER_INTERVALS = 7

INTERVALS = None
DAYS = None
SUBJECTS = None
TEACHERS = None
ROOMS = None

class State:
    def __init__(
            self,
            timetable: Dict[str, Dict[Tuple[int, int], Dict[str, Tuple[str, str]]]] = {},
            remained_profs_intervals: Dict[str, int] = {},
            remained_subjects: Dict[str, int] = {},
            teacher_rooms_day_intervals: Dict[str, Dict[Tuple[int, int], List[str]]] = {},
            conflicts: int = 0,
            seed: int = 42
    ) -> None:
        self.timetable = timetable
        self.remained_profs_intervals = remained_profs_intervals
        self.remained_subjects = remained_subjects
        self.conflicts = conflicts
        self.teacher_rooms_day_intervals = teacher_rooms_day_intervals
        self.seed = seed

    def is_final(self) -> bool:
        '''
        Întoarce True dacă este stare finală.
        '''
        for _, unallocated_students in self.remained_subjects.items():
            if int(unallocated_students) > 0:
                return False

        return True

    # trb sa pun LIST[State]
    def get_next_states(self):
        '''
        Întoarce un generator cu toate posibilele stări următoare.
        '''
        next_states = []

        for day in DAYS:
            for interval in INTERVALS:
                for room_name, room_details in ROOMS.items():
                    if self.timetable[day][interval][room_name] == None and room_name not in self.teacher_rooms_day_intervals[day][interval]:
                        for subject in room_details["Materii"]:
                            if self.remained_subjects[subject] > 0:
                                for teacher_name, teacher_details in TEACHERS.items():
                                    if subject in teacher_details["Materii"] and self.remained_profs_intervals[teacher_name] > 0:
                                        if teacher_name not in self.teacher_rooms_day_intervals[day][interval]:
                                            new_state = copy.deepcopy(self)
                                            # print all combinations of subject, teacher, room
                                            # print(day, interval, subject, teacher_name, room_name)
                                            # generate the new state
                                            new_state.timetable[day][interval][room_name] = (teacher_name, subject)
                                            new_state.conflicts += is_soft_constraint(day, interval, teacher_name)
                                            new_state.remained_profs_intervals[teacher_name] -= 1
                                            new_state.remained_subjects[subject] -= room_details["Capacitate"]
                                            if new_state.remained_subjects[subject] < 0:
                                                new_state.remained_subjects[subject] = 0
                                            new_state.teacher_rooms_day_intervals[day][interval].append(teacher_name)
                                            new_state.teacher_rooms_day_intervals[day][interval].append(room_name)
                                            next_states.append(new_state)
        return next_states


def eval_function(state: State) -> int:
    total_cost = 0
    remained_subjects = state.remained_subjects
    # for _, students_count in initial_subjects_stud_count.items():
    for _, left_students_count in remained_subjects.items():
        if left_students_count != 0:
            total_cost += left_students_count

    total_cost += state.conflicts * 10

    return total_cost


def stochastic_hill_climbing(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial

    while iters < max_iters:
        iters += 1
        print('iters', iters)
        # TODO 3. Alegem aleator între vecinii mai buni decât starea curentă.
        # Folosiți radnom.choice(lista)
        # Nu uitați să adunați numărul de stări construite.
        current_state_score = eval_function(state)
        possible_states = state.get_next_states()
        #print(possible_states)
        found_local_min = True

        better_states = []

        for possible_state in possible_states:
            states += 1
            possible_state_score = eval_function(possible_state)
            if possible_state_score < current_state_score:
                found_local_min = False
                better_states.append(possible_state)

        if not found_local_min:
            state = random.choice(better_states)

        if found_local_min:
            print(str(state.is_final()) + " Found local min with score: " + str(eval_function(state)))
            return state.is_final(), iters, states, state

    return state.is_final(), iters, states, state

def steepest_ascent_HC(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial

    while iters < max_iters:
        iters += 1
        print('iters', iters)
        better_exists = False
        successors = state.get_next_states()
        current_state_score = eval_function(state)

        for possible_state in successors:
            possible_state_score = eval_function(possible_state)
            if possible_state_score < current_state_score:
                better_exists = True
                state = possible_state
                current_state_score = possible_state_score

        if not better_exists:
            return state.is_final(), iters, states, state

    return state.is_final(), iters, states, state

def random_restart_HC(initial: State, max_restarts: int = 100):
    total_iters, total_states = 0, 0
    succesors_list = initial.get_next_states()

    state = random.choice(succesors_list)

    for i in range(0, max_restarts):
        state_is_final, iters, states, final_state = stochastic_hill_climbing(state, 100)
        total_iters += iters + 1
        total_states += states

        if state_is_final:
            return state_is_final, total_iters, total_states, final_state
        else:
            print("Random choosing a succesor")
            state = random.choice(succesors_list)

    return False, total_iters, total_states, state

def my_HC(initial: State, max_iters: int = 100, max_tries: int = 20):
    total_iters, total_states = 0, 0

    state_is_final, iters, states, state = steepest_ascent_HC(initial, max_iters)

    total_states += states
    total_iters += iters

    if not state_is_final:
        print("Steepest failed! Trying stochastic...")
        for i in range(0, max_tries):
            total_iters += 1
            state_is_final, iters, states, state = stochastic_hill_climbing(initial, max_iters)
            total_iters += iters
            total_states += states

            if state_is_final:
                return state_is_final, total_iters, total_states, state
    # it failed, return all the details anyway
    return state_is_final, total_iters, total_states, state



# sa merg doar pe conflicte soft poate merge ala mediu
# def stochastic_hill_climbing(initial: State, max_iters: int = 10000):
#     iters, states = 0, 0
#     best_state = initial
#
#     while iters < max_iters:
#         iters += 1
#         print('iters', iters)
#         better_states = best_state.get_next_states()
#         if better_states:
#             best_state = random.choice(better_states)
#         else:
#             return best_state.is_final(), iters, states, best_state
#
#     return best_state.is_final(), iters, states, best_state

def process_input_data(input_data):
    global INTERVALS, SUBJECTS, TEACHERS, ROOMS, DAYS
    # POATE UN TRY CATCH FRUMOS
    INTERVALS = input_data['Intervale']
    SUBJECTS = input_data['Materii']
    TEACHERS = input_data['Profesori']
    ROOMS = input_data['Sali']
    DAYS = input_data['Zile']

def initialise_timetable_empty() -> Dict[str, Dict[Tuple[int, int], Dict[str, Tuple[str, str]]]]:
    timetable = {}
    for day in DAYS:
        timetable[day] = {}
        for interval in INTERVALS:
            timetable[day][interval] = {}
            for room in ROOMS:
                timetable[day][interval][room] = None

    return timetable

def convert_string_to_int_tuple(timetable: Dict[str, Dict[str, Dict[str, Tuple[str, str]]]]) -> Dict[
    str, Dict[Tuple[int, int], Dict[str, Tuple[str, str]]]]:
    new_timetable = {}
    for day, intervals in timetable.items():
        new_intervals = {}
        for interval_str, courses in intervals.items():
            start, end = map(int, interval_str.strip('()').split(','))
            new_intervals[(start, end)] = courses
        new_timetable[day] = new_intervals
    return new_timetable

def contains_number(string):
    return any(char.isdigit() for char in string)
def get_explicit_constraints(constraints: []):
    modified_constraints = []
    for constraint in constraints:
        if contains_number(constraint):
            contains_exclamation = False
            constraint = constraint.replace(", ", "-").replace("(", "").replace(")", "")
            # now its like !10-14
            if constraint[0] == '!':
                contains_exclamation = True
                constraint = constraint.replace("!", "")
                # now its like 10-14
            small = int(constraint.split("-")[0])
            big = int(constraint.split("-")[1])

            if big - small > 2:
                while small < big:
                    if contains_exclamation:
                        modified_constraints.append("!" + str(small) + "-" + str(small + 2))
                    else:
                        modified_constraints.append(str(small) + "-" + str(small + 2))
                    small += 2
            else:
                if contains_exclamation:
                    constraint = "!" + constraint
                modified_constraints.append(constraint)
        else:
            modified_constraints.append(constraint)

    return modified_constraints

def is_soft_constraint(day: str, interval: str, teacher_name: str):
    total_cost = 0

    teacher_constraints = get_explicit_constraints(TEACHERS[teacher_name]["Constrangeri"])
    not_day = '!' + day
    interval = interval.replace(", ", "-").replace("(", "").replace(")", "")
    # interval = str(interval[0]) + '-' + str(interval[1])
    not_interval = '!' + interval

    if not_day in teacher_constraints:
        total_cost += 1
    elif day not in teacher_constraints:
        total_cost += 1

    if not_interval in teacher_constraints:
        total_cost += 1
    elif interval not in teacher_constraints:
        total_cost += 1

    return total_cost


def main():
    # ceva
    # Check if correct number of command-line arguments are provided
    # TODO MODIFY THIS 4 TO 3 WHEN RUNNING ON OTHER THAN PYCHARM
    # TODO AND THE SYS.ARGV[3]...
    if len(sys.argv) != 4:
        print("Usage: python program.py <algorithm> <input_file>")
        return

    # Extract algorithm and input file from command-line arguments
    algorithm = sys.argv[2]
    input_file = "C:\\Users\\alexa\\PycharmProjects\\temaIA_V2\\tema1_v2.\\inputs\\" + sys.argv[3]

    # Read input file
    input_data = read_yaml_file(input_file)
    process_input_data(input_data)
    # Create initial state
    initial_state = State(
        # TODO MUST SET INITIAL TIMETABLE EMPTY
        timetable = initialise_timetable_empty(),
        remained_profs_intervals = {teacher: MAX_TEACHER_INTERVALS for teacher in TEACHERS},
        remained_subjects = {subject: SUBJECTS[subject] for subject in SUBJECTS},
        teacher_rooms_day_intervals = {day: {interval: [] for interval in INTERVALS} for day in DAYS},
        conflicts = 0,
        seed = 42
    )

    if algorithm == 'hc':
        # TODO ADD DAYS TO THE TIMETABLE
        # _, _, _, state = stochastic_hill_climbing(initial_state, 100)
        # _, _, _, state = steepest_ascent_HC(initial_state, 10000)
        # _, _, _, state = random_restart_HC(initial_state, 100)
        _, _, _, state = my_HC(initial_state, 100, 20)

        print('Conflicte soft: ', state.conflicts)
        print(state.timetable)
        print(pretty_print_timetable(convert_string_to_int_tuple(state.timetable), input_file))

        print('\n----------- Constrângeri obligatorii -----------')
        constrangeri_incalcate = check_mandatory_constraints(convert_string_to_int_tuple(state.timetable), input_data)

        print(f'\n=>\nS-au încălcat {constrangeri_incalcate} constrângeri obligatorii!')

        print('\n----------- Constrângeri optionale -----------')
        constrangeri_optionale = check_optional_constraints(convert_string_to_int_tuple(state.timetable), input_data)

        print(f'\n=>\nS-au încălcat {constrangeri_optionale} constrângeri optionale!\n')
        if not state.is_final():
            print(state.remained_subjects)
        print("conflicts: " + str(state.conflicts))
if __name__ == '__main__':
    main()
