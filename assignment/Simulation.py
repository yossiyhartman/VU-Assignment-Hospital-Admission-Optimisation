from Hospital import Hospital
from STRC import STRC
from Tracker import Tracker
from Patient import Patient
import datetime as dt
import numpy as np


class Simulation():

    def __init__(self, simulation_years : int = 1, patience : int = 5, transfer_time : int = 4, beds : int = 100, weekend : bool = False, opening: int = 9, closing : int = 17, incresae_arrivals : float = 1., decrease_length_of_stay : float = 0.) -> None:

        # Simulation parameters
        # self.parameters : dict = params
        self.parameters : dict = {
            'simulation_years'          : simulation_years,
            'patience'                  : patience,     
            'transfer_time'             : transfer_time, 
            'increase_arrivals'         : incresae_arrivals,
            'decrease_length_of_stay'   : decrease_length_of_stay,

        }

        # Track progress
        self.tracker  : Tracker = Tracker()

        # Instances
        self.hospital : Hospital = Hospital()
        self.STRC     : STRC = STRC(beds, opening, closing, weekend)

        
        

    # Simulation timespan

    def output(self):
        return self.tracker.getOutput()

    def start(self) -> None:
        days    = self.parameters['simulation_years'] * 365
        period  = dt.datetime(2023, 1, 1) + np.arange(days) * dt.timedelta(days = 1)

        for date in period:
            self.tracker.date = date
            self.__simulateDay()


    def __simulateDay(self) -> None:
        for hour in range(0,24):
            self.tracker.datetime = dt.datetime(self.tracker.date.year, self.tracker.date.month, self.tracker.date.day, hour )
            self.__simulateHour()


    def __simulateHour(self) -> None:
        self.__updateInstances()
        self.__processPatients()
        self.__updateTrackers()


    # Update functions

    def __updateTrackers(self) -> None:

        self.tracker.addTime(self.tracker.now())
        self.tracker.getOccupancyHospitalQueue(self.hospital.numberPatientsInQueue())
        self.tracker.getPatientsOnWaitingList(self.STRC.numberPatientsOnWaitingList())
        self.tracker.getPatientsInShuttle(self.STRC.numberPatientsOnShuttle())
        self.tracker.getOccupancySTRC(self.STRC.numberPatientsInSTRC())


    def __updateInstances(self) -> None:
        self.__updateWaitingList()
        self.__updateShutle()
        self.__updatePatientsResidualLengthOfStay()


    def __updateWaitingList(self) -> None:
        self.STRC.updateWaitingList()

        self.__rejectAccesToSTRC(self.STRC.removeProlongedWaitingPatients())


    def __updateShutle(self) -> None:
        self.STRC.updateShuttle()

        if self.STRC.isOpen(self.tracker.now()):
            [self.STRC.acceptPatient(patient) for patient in self.STRC.removeArrivedPatients()]


    def __updatePatientsResidualLengthOfStay(self) -> None:
        self.hospital.decreasePatientsRemainingStay()
        self.STRC.decreasePatientsRemainingStay()

        if self.STRC.isOpen(self.tracker.now()):
            recovered = self.STRC.removeRecoveredPatients() + self.hospital.releaseRecoveredPatients()
            self.tracker.addPatients(recovered, self.tracker.now())
        pass


    # Process functions

    def __processPatients(self) -> None:

        arrivals = self.__getArrivals()

        self.tracker.addArrivals(arrivals['total'])

        self.__checkAvailability(arrivals)


    def __checkAvailability(self, patients : dict) -> None:

        if self.STRC.isOpen(self.tracker.now()):
            self.__applyToSTRC(patients)

        else: 
            self.__placeOnWaitingList(patients['priority'])
            self.__rejectAccesToSTRC(patients['normal'])


    def __placeOnWaitingList(self, patients : list[Patient]) -> None:

        if self.parameters['patience'] <= 0:
            self.__rejectAccesToSTRC(patients)

        else:
            while(patients):
                patient = patients.pop()
                patient.placedOnWaitingList(self.tracker.now())
                self.STRC.placePatientOnWaitingList(patient, self.parameters['patience'])



    # Application functions

    def __applyPatientsOnWaitingList(self) -> None:
        while self.STRC.patientsOnWaitingList():
            if not self.STRC.isFull():
                self.__acceptAccesToSTRC(self.STRC.getWaitingPatient())
            else: break


    def __applyPriorityPatients(self, patients : list[Patient]) -> None:
        while patients:
            if self.STRC.isFull():
                self.__placeOnWaitingList(patients)
            else:
                self.__acceptAccesToSTRC(patients.pop())


    def __applyPatientsInHospitalQueue(self) -> None:
        while self.hospital.patientsInQueue():
            if not self.STRC.isFull():
                self.__acceptAccesToSTRC(self.hospital.getPatient())
            else: break


    def __applyNonPriorityPatients(self, patients : list[Patient]) -> None:
        while patients:
            if self.STRC.isFull():
                self.__rejectAccesToSTRC(patients)
            else:
                self.__acceptAccesToSTRC(patients.pop())


    def __applyToSTRC(self, patients : list[Patient]) -> None:
        self.__applyPatientsOnWaitingList()
        self.__applyPriorityPatients(patients['priority'])
        self.__applyPatientsInHospitalQueue()
        self.__applyNonPriorityPatients(patients['normal'])


    def __rejectAccesToSTRC(self, patients : list[Patient]) -> None:

        while(patients):
            patient = patients.pop()
            patient.isRejected(self.tracker.now())
            self.hospital.placeInQueue(patient)


    def __acceptAccesToSTRC(self, patient : Patient) -> None:

        patient.isAccepted(self.tracker.now())

        if self.parameters['transfer_time'] == 0:
            self.STRC.acceptPatient(patient)
        else:
            self.STRC.placePatientInShuttle(patient, self.parameters['transfer_time'])



    # Simulation functions

    def __getArrivals(self):

        GP = np.random.poisson(lam = 0.054166 * self.parameters['increase_arrivals']) # p hour
        ED = np.random.poisson(lam = 0.034583 * self.parameters['increase_arrivals']) # p hour
        HA = np.random.poisson(lam = 0.039166 * self.parameters['increase_arrivals']) # p hour
        
        GP_arr = self.__createPatients(amount = GP, department = 'GP')
        ED_arr = self.__createPatients(amount = ED, department = 'ED')
        HA_arr = self.__createPatients(amount = HA, department = 'HA')

        return {
            'priority'  : ED_arr + GP_arr,
            'normal'    : HA_arr,
            'total'     : ED + GP + HA
        }


    def __createPatients(self, amount : int, department : str) -> list:

        patients = []
        
        for _ in range(amount):
            care, los = self.__getCare()
            patients.append(Patient(self.tracker.now(), department, care, los))
        
        return patients
        


    def __getCare(self):

        RV = np.random.rand() # simulate a uniformly distributed random number

        distribution = {
            'label'         : ["Home", "Death", 'Home with Adjustments', 'Long Term Care', 'Geriatric Rehabilitation', 'Hospice Care'],
            'cumulative'    : [0.578, 0.638, 0.745, 0.943, 0.977, 1], 
            'value'         : [31.1, 22.9, 43.9, 47.8, 29.8, 22.9, 5],
        }

        for label, cumulative, value in zip(distribution['label'], distribution['cumulative'], distribution['value']):
            if RV <= cumulative:
                care = label
                los = np.random.gamma(value) if label in ['Home with Adjustments', 'Long Term Care'] else np.random.exponential(value)
                break

        los = np.ceil(24 * los * (1 - self.parameters['decrease_length_of_stay']))

        return care, los
        









# Run the Script
if __name__ == "__main__":

    simulation = Simulation(simulation_years=3, patience = 8, transfer_time = 4, beds = 100, weekend = True, opening = 0, closing = 23)
    simulation.start()
    P, S = simulation.output() 

    print(P.describe())
