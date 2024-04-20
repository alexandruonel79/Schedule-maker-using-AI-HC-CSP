from typing import Dict, Tuple, List
import copy
import random
import sys
from utils import read_yaml_file, pretty_print_timetable
from check_constraints import *
MAXTEACHERINTERVALS = 7

class State:
    def __init__(
        self, 
        info_days: List[str] = [],
        info_intervals: List[Tuple[int, int]] = [],
        # timetable : {str : {(int, int) : {str : (str, str)}}} 
        # Primește un dicționar ce are chei zilele, cu valori dicționare de intervale reprezentate ca tupluri de int-uri, cu valori dicționare de săli, cu valori tupluri (profesor, materie)
        timetable: Dict[str, Dict[Tuple[int, int], Dict[str, Tuple[str, str]]]] = {},
        remained_profs_intervals: Dict[str, int] = {},
        # teacher_name, subject_list
        info_teacher_subjects: Dict[str, List[str]]= {},
        info_teacher_constraints: Dict[str, List[str]] = {},
        # name, capacity, allowed_subjects
        info_rooms: Dict[str, Tuple[int, List[str]]] = {},
        remained_subjects: Dict[str, int] = {},
        conflicts: int = 0,
        seed: int = 42
    ) -> None:
        
        self.info_days = info_days
        self.info_intervals = info_intervals
        self.timetable = timetable
        self.remained_profs_intervals = remained_profs_intervals
        self.info_teacher_subjects = info_teacher_subjects
        self.info_rooms = info_rooms
        self.conflicts = conflicts
        self.remained_subjects = remained_subjects
        self.info_teacher_constraints = info_teacher_constraints
        self.seed = seed
    
    # checks if (subject, sala, profesor) is a soft constraint
    def is_soft_constraint(self, prof_name: str, interval: Tuple[int, int], day: str) -> int:
        # print prof_name
        print('prof_name', prof_name)
        constraints_list = self.info_teacher_constraints[prof_name]
        constraints_count = 0
        not_day = '!' + day
        
        # if '!Luni' 
        if not_day in constraints_list:
            constraints_count += 1
        # if 'Luni' isn't a preference
        elif day not in constraints_list:
            constraints_count += 1

        not_interval = '!' + str(interval[0]) + '-' + str(interval[1])
        # if the interval isn't a preference
        if not_interval in constraints_list:
            constraints_count += 1
        elif interval not in constraints_list:
            constraints_count += 1
        
        return constraints_count
    
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
        #
        # for subject, unallocated_students in self.remained_subjects.items():
        #     print('subject', subject)
        #     print('unallocated_students', unallocated_students)
        #     # if i have any students left without the course
        #     if int(unallocated_students) > 0:
        #         # search for an available teacher
        #         for teacher_name, left_intervals in self.remained_profs_intervals.items():
        #             teacher_subjects_list = self.info_teacher_subjects[teacher_name]
        #             if left_intervals and subject in teacher_subjects_list:
        #                 # search for an available classroom
        #                 for classroom, (classroom_capacity, classroom_subjects_list) in self.info_rooms.items():
        #                     # classroom_subjects_list = self.info_rooms[classroom][1]
        #                     # classroom_capacity = self.info_rooms[classroom][0]
        #                     if subject in classroom_subjects_list and :
        #                             for day in self.info_days:
        #                                 for interval in self.info_intervals:
        #
        #                                     if day not in self.timetable:
        #                                         self.timetable[day] = {}
        #
        #                                     if interval not in self.timetable[day]:
        #                                         self.timetable[day][interval] = {}
        #
        #                                     if self.timetable[day][interval] == {}:
        #                                         # we have the students, the teacher and the classroom
        #                                         new_state = copy.deepcopy(self)
        #                                         new_state.timetable[day][interval][classroom] = (teacher_name, subject)
        #                                         new_state.remained_profs_intervals[teacher_name] -= 1
        #                                         new_state.remained_subjects[subject] -= classroom_capacity
        #                                         if new_state.remained_subjects[subject] < 0:
        #                                             new_state.remained_subjects[subject] = 0
        #                                         new_state.conflicts += self.is_soft_constraint(teacher_name, interval, day)
        #                                         next_states.append(new_state)

        for day in self.info_days:
            for interval in self.info_intervals:
                # copy the new state
                new_state = copy.deepcopy(self)
                # new_state.remained_subjects = copy.deepcopy(self.remained_subjects)
                # new_state.remained_profs_intervals = copy.deepcopy(self.remained_profs_intervals)

                occupied_classrooms = {}
                teacher_interval = []

                if day not in new_state.timetable:
                    new_state.timetable[day] = {}

                if interval not in new_state.timetable[day]:
                    new_state.timetable[day][interval] = {}
                else:
                    continue

                for subject, unallocated_students in new_state.remained_subjects.items():
                    print('subject', subject)
                    print('unallocated_students', unallocated_students)
                    # if i have any students left without the course
                    if int(unallocated_students) > 0:
                        # search for an available teacher
                        for teacher_name, left_intervals in new_state.remained_profs_intervals.items():
                            teacher_subjects_list = new_state.info_teacher_subjects[teacher_name]
                            # if left_intervals and subject in teacher_subjects_list and teacher_name not in teacher_interval:
                            #     teacher_interval.append(teacher_name)
                                # search for an available classroom
                            for classroom_name, (classroom_capacity, classroom_subjects_list) in new_state.info_rooms.items():
                                # classroom_subjects_list = self.info_rooms[classroom][1]
                                # classroom_capacity = self.info_rooms[classroom][0]
                                if left_intervals and subject in teacher_subjects_list and teacher_name not in teacher_interval:
                                    if subject in classroom_subjects_list and classroom_name not in occupied_classrooms:
                                        teacher_interval.append(teacher_name)
                                        occupied_classrooms[classroom_name] = (teacher_name, subject)
                                        # update the new state
                                        new_state.remained_profs_intervals[teacher_name] -= 1
                                        new_state.remained_subjects[subject] -= classroom_capacity
                                        if new_state.remained_subjects[subject] < 0:
                                            new_state.remained_subjects[subject] = 0
                                        new_state.conflicts += new_state.is_soft_constraint(teacher_name, interval, day)
                # posibil necesar inca un deep copy
                new_state.timetable[day][interval] = occupied_classrooms
                next_states.append(copy.deepcopy(new_state))
        return next_states


def eval_function(state: State) -> int:
    total_cost = 0
    remained_subjects = state.remained_subjects
    # for _, students_count in initial_subjects_stud_count.items():
    for _, left_students_count in remained_subjects.items():
        if left_students_count != 0:
            total_cost += left_students_count * 100
    # TODO DEOCAMDATA IGNOR ASTEA SOFT MUST FIX IS_SOFT AIA
    #total_cost += state.conflicts

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
        print(possible_states)
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

def create_input_structures(input_data):
    info_days = input_data['Zile']
    info_intervals = input_data['Intervale']
    info_teacher_subjects = {}
    info_teacher_constraints = {}
    info_rooms = {}
    remained_profs_intervals = {}
    
    teachers = input_data['Profesori']
    for teacher_name, teacher_details in teachers.items():
        info_teacher_subjects[teacher_name] = teacher_details['Materii']
        info_teacher_constraints[teacher_name] = teacher_details['Constrangeri']
        # each teacher is allowed to maximum 7 intervals
        remained_profs_intervals[teacher_name] = MAXTEACHERINTERVALS

    rooms = input_data['Sali']
    for room_name, room_details in rooms.items():
        info_rooms[room_name] = (room_details['Capacitate'], room_details['Materii'])

    remained_subjects = input_data['Materii']

    return info_days, info_intervals, info_teacher_subjects, info_teacher_constraints, info_rooms, remained_subjects, remained_profs_intervals

def convert_string_to_int_tuple(timetable: Dict[str, Dict[str, Dict[str, Tuple[str, str]]]]) -> Dict[str, Dict[Tuple[int, int], Dict[str, Tuple[str, str]]]]:
    new_timetable = {}
    for day, intervals in timetable.items():
        new_intervals = {}
        for interval_str, courses in intervals.items():
            start, end = map(int, interval_str.strip('()').split(','))
            new_intervals[(start, end)] = courses
        new_timetable[day] = new_intervals
    return new_timetable

def add_missing_intervals_and_rooms(state: State) -> State:
    for day in state.timetable:
        for interval in state.info_intervals:
            if interval not in state.timetable[day]:
                state.timetable[day][interval] = {}

            for room in state.info_rooms:
                if room not in state.timetable[day][interval]:
                    state.timetable[day][interval][room] = None

    return state


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
    info_days, info_intervals, info_teacher_subjects, info_teacher_constraints, info_rooms, remained_subjects, remained_profs_intervals = create_input_structures(input_data)
    # Create initial state
    initial_state = State(
    info_days=info_days,
    info_intervals=info_intervals,
    timetable={},
    remained_profs_intervals=remained_profs_intervals,
    info_teacher_subjects=info_teacher_subjects,
    info_teacher_constraints=info_teacher_constraints,
    info_rooms=info_rooms,
    remained_subjects=remained_subjects,
    conflicts=0,
    seed=42
    )

    if algorithm == 'hc':
        # TODO ADD DAYS TO THE TIMETABLE
        _, _, _, state = stochastic_hill_climbing(initial_state, 1000)
        state = add_missing_intervals_and_rooms(state)
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


if __name__ == '__main__':
    main()