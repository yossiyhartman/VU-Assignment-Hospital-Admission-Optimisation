from Patient import Patient

class Hospital:

    def __init__(self) -> None:

        self.patients = []


    def numberPatientsInQueue(self) -> int:
        return len(self.patients)
    
    # Hospital

    def patientsInQueue(self) -> bool:
        return self.patients

    def placeInQueue(self, patient : Patient) -> None:
        self.patients.append(patient)

    def getPatient(self) -> Patient:
        return self.patients.pop()


    # Patients

    def decreasePatientsRemainingStay(self) -> None:

        if self.patientsInQueue():
            [ patient.updateRemainingLengthOfStay() for patient in self.patients ]


    def releaseRecoveredPatients(self) -> list:

        recovered_patients  = [ patient for patient in self.patients if patient.remaining_length_of_stay <= 0 ]
        self.patients       = [ patient for patient in self.patients if patient.remaining_length_of_stay > 0 ]

        return recovered_patients