import datetime as dt

class Patient:

    def __init__(self, arrival_time : dt, department : str, care : str, LOS : int) -> None:

        self.arrival_time                = arrival_time  
        self.department                  = department
        self.care                        = care
        self.length_of_stay              = LOS
        self.time_placed_on_waiting_list = None
        self.time_of_blocking            = None
        self.time_of_acceptance          = None
        self.remaining_length_of_stay    = LOS
        self.time_of_recovery            = None


    def isRejected(self, timestamp : dt) -> None:
        self.time_of_blocking = timestamp

    def placedOnWaitingList(self, timestamp : dt) -> None:
        self.time_placed_on_waiting_list = timestamp

    def isRecovered(self, timestamp : dt) -> None:
        self.time_of_recovery = timestamp

    def updateRemainingLengthOfStay(self) -> None:
        if self.remaining_length_of_stay > 0:
            self.remaining_length_of_stay -= 1

    def isAccepted(self, timestamp : dt) -> None:
        self.time_of_acceptance = timestamp

