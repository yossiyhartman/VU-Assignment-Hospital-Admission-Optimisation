import Patient
import datetime as dt

class STRC:

    def __init__(self, beds : int = 100, opening : int = 9, closing : int = 17, weekend : bool = False) -> None:
        
        self.beds         : int  = beds 

        self.patients     : list  = []
        self.waiting_list : list  = []
        self.shuttle      : list  = []

        self.opening_times : dict = {
            'weekend' : weekend, 
            'opening' : opening,
            'closing' : closing
        }


    # Waiting list

    def numberPatientsOnWaitingList(self) -> int:
        return len(self.waiting_list)

    def patientsOnWaitingList(self) -> None:
        return self.waiting_list

    def getWaitingPatient(self) -> Patient:
        return self.waiting_list.pop()['patient']

    def removeProlongedWaitingPatients(self) -> list:

        prolongedWaitingPatients = [ patient['patient'] for patient in self.waiting_list if patient['patience'] <= 0 ]
        self.waiting_list = [patient for patient in self.waiting_list if patient['patience'] > 0 ]

        return prolongedWaitingPatients

    def placePatientOnWaitingList(self, patient : Patient, duration : int) -> None:
        self.waiting_list.append({'patient' : patient, 'patience' : duration })

    def updateWaitingList(self) -> None:

        if self.waiting_list:
            for patient in self.waiting_list:
                if patient['patience'] > 0:
                    patient['patience'] -= 1        


    # Shuttle bus

    def numberPatientsOnShuttle(self) -> int:
        return len(self.shuttle)

    def patientsInShuttle(self) -> bool:
        return self.shuttle

    def removeArrivedPatients(self) -> list:

        arrived_patients = [ patient['patient'] for patient in self.shuttle if patient['ETA'] <= 0 ]
        self.shuttle = [patient for patient in self.shuttle if patient['ETA'] > 0 ]

        return arrived_patients

    def placePatientInShuttle(self, patient : Patient, duration : int) -> None:
        self.shuttle.append({ 'ETA' : duration, 'patient' : patient })


    def updateShuttle(self) -> None:

        if self.shuttle:
            for patient in self.shuttle:
                if patient['ETA'] > 0:
                    patient['ETA'] -= 1
            


        
    # At Location

    def numberPatientsInSTRC(self) -> int:
        return len(self.patients)    


    def isFull(self) -> bool:

        number_of_patients = len(self.patients)
        number_of_transits = len(self.shuttle)
        total = number_of_patients + number_of_transits

        return total == self.beds

    def isOpen(self, timestamp : dt):

        if (not self.opening_times['weekend']) & (timestamp.weekday() in [5,6]):
            return False
        elif (timestamp.hour < self.opening_times['opening']) | (self.opening_times['closing'] < timestamp.hour):
            return False
        else:
            return True

    def acceptPatient(self, patient: Patient) -> None:
        self.patients.append(patient)


    def patientsIn(self) -> bool:
        return self.patients

    # Patients

    def decreasePatientsRemainingStay(self) -> None:
        if self.patientsIn():
            [ patient.updateRemainingLengthOfStay() for patient in self.patients ]

    def removeRecoveredPatients(self) -> list:
        recovered_patients  = [ patient for patient in self.patients if patient.remaining_length_of_stay <= 0 ]
        self.patients       = [ patient for patient in self.patients if patient.remaining_length_of_stay > 0 ]

        return recovered_patients