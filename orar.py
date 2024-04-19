from typing import Dict, Tuple, List
import copy
import random
import sys
from utils import read_yaml_file

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
        constraints_list = self.info_teacher_subjects[prof_name][1]
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
        for _, unallocated_students in self.remained_subjects:
            if unallocated_students > 0:
                return False
        
        return True
        
    # trb sa pun LIST[State]
    def get_next_states(self):
        '''
        Întoarce un generator cu toate posibilele stări următoare.
        '''
        next_states = []

        for subject, unallocated_students in self.remained_subjects:
            # if i have any students left without the course
            if int(unallocated_students) > 0:
                # search for an available teacher
                for teacher_name, left_intervals in self.remained_profs_intervals:
                    teacher_subjects_list = self.info_teacher_subjects[teacher_name]
                    if left_intervals and subject in teacher_subjects_list:
                        # search for an available classroom
                        for classroom, (classroom_subjects_list, classroom_capacity) in self.info_rooms:
                            # classroom_subjects_list = self.info_rooms[classroom][1]
                            # classroom_capacity = self.info_rooms[classroom][0]
                            if subject in classroom_subjects_list:
                                    for day in self.info_days:
                                        for interval in self.info_intervals:

                                            if day not in self.timetable:
                                                self.timetable[day] = {}

                                            if interval not in self.timetable[day]:
                                                self.timetable[day][interval] = {}

                                            if self.timetable[day][interval] == {}:
                                                # we have the students, the teacher and the classroom
                                                new_state = copy.deepcopy(self)
                                                new_state.timetable[day][interval][classroom] = (teacher_name, subject)
                                                new_state.remained_profs_intervals[teacher_name] -= 1
                                                new_state.remained_subjects[subject] -= classroom_capacity
                                                new_state.conflicts += self.is_soft_constraint(teacher_name, interval, day)
                                                next_states.append(new_state)

        return next_states

    
def stochastic_hill_climbing(initial: State, max_iters: int = 1000):
    iters, states = 0, 0
    state = initial
    
    while iters < max_iters:
        iters += 1
        print('iters', iters)
        # TODO 3. Alegem aleator între vecinii mai buni decât starea curentă.
        # Folosiți radnom.choice(lista)
        # Nu uitați să adunați numărul de stări construite.
        current_state_score = state.conflicts
        possible_states = state.get_next_states()
        print(possible_states)
        found_local_min = True

        better_states = []

        for possible_state in possible_states:
            states += 1
            possible_state_score = possible_state.conflicts
            if possible_state_score < current_state_score:
                found_local_min = False
                better_states.append(possible_state)

        if not found_local_min:
            state = random.choice(better_states)
            current_state_score = state.conflicts

        if found_local_min:
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

def main():
    # ceva
    # Check if correct number of command-line arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python program.py <algorithm> <input_file>")
        return

    # Extract algorithm and input file from command-line arguments
    algorithm = sys.argv[1]
    input_file = './inputs/' + sys.argv[2]

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
        print(stochastic_hill_climbing(initial_state, 1000))
        print('Got timetable' + str(initial_state.timetable))


if __name__ == '__main__':
    main()