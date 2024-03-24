import datetime as dt
from Patient import Patient
import pandas as pd


class Tracker():
    def __init__(self) -> None:

        self.date       : dt = None
        self.datetime   : dt = None

        self.waiting_list   : list = []
        self.hopsital_queue : list = []
        self.shuttle        : list = []

        self.system_ouput : dict = {
            'datetime' : [],
            'weekday' : [],
            'arrivals' : [],
            'waiting_list' : [],
            'hospital_queue' : [],
            'shuttle_bus': [],
            'STRC': [],
        }

        self.patient_output : dict = {
            'arrival_time' : [],
            'department' : [],
            'care' : [],
            'length_of_stay' : [],
            'time_placed_on_waiting_list' : [],
            'time_of_blocking' : [],
            'time_of_acceptance' : [],
            'time_of_recovery' : [],
            'waiting_time': [],
            'time_in_queue': [],
            'blocked': [],
            'hospital_recovery': [],
        }

    # Time Tracking
    def now(self) -> dt:
        return self.datetime

    # Print output
    def getOutput(self):
        
        patient = pd.DataFrame(self.patient_output)
        system = pd.DataFrame(self.system_ouput)

        patient.to_csv('patients.csv')
        system.to_csv('system.csv')

        return patient, system

    
    # Patients Updates

    def addPatients(self, patients : list[Patient], timestamp : dt) -> None:

        while patients:
            patient = patients.pop()

            self.patient_output['arrival_time'].append(patient.arrival_time)
            self.patient_output['department'].append(patient.department)
            self.patient_output['care'].append(patient.care)
            self.patient_output['length_of_stay'].append(round(patient.length_of_stay / 24, 2))
            self.patient_output['time_placed_on_waiting_list'].append(patient.time_placed_on_waiting_list)
            self.patient_output['time_of_blocking'].append(patient.time_of_blocking)
            self.patient_output['time_of_acceptance'].append(patient.time_of_acceptance)

            time_of_recovery = timestamp
            self.patient_output['time_of_recovery'].append(time_of_recovery)


            blocked             = True if patient.time_of_blocking != None else False
            hospital_recovery   = True if patient.time_of_acceptance == None else False
            waiting_time        = ((patient.time_of_acceptance - patient.arrival_time).total_seconds() / 3600) if (not hospital_recovery) else ((time_of_recovery - patient.arrival_time).total_seconds() / 3600) 
            time_in_queue       = 0
            
            if (blocked) & (not hospital_recovery):
                time_in_queue = ((patient.time_of_acceptance - patient.time_of_blocking).total_seconds() / 3600)
            elif (blocked) & (hospital_recovery):
                time_in_queue = ((time_of_recovery - patient.time_of_blocking).total_seconds() / 3600)

            self.patient_output['blocked'].append(blocked)
            self.patient_output['hospital_recovery'].append(hospital_recovery)
            self.patient_output['waiting_time'].append(waiting_time)
            self.patient_output['time_in_queue'].append(time_in_queue)

    # System Updates

    def addTime(self, time : dt) -> None:
        self.system_ouput['datetime'].append(time)
        self.system_ouput['weekday'].append(time.strftime('%A'))

    def addArrivals(self, arrivals : int) -> None:
        self.system_ouput['arrivals'].append(arrivals)

    def getOccupancyHospitalQueue(self, patients : int) -> None:
        self.system_ouput['hospital_queue'].append(patients)

    def getOccupancySTRC(self, patients : int) -> None:
        self.system_ouput['STRC'].append(patients)

    def getPatientsOnWaitingList(self, patients : int) -> None:
        self.system_ouput['waiting_list'].append(patients)

    def getPatientsInShuttle(self, patients : int) -> None:
        self.system_ouput['shuttle_bus'].append(patients)        