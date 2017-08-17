MAX_SLOTS = 5 #maximum slots to assign to volunteers who did not specify a clear max

class Slot(object):

    def __init__(self, day, start_hr, end_hr, type_=None):
        self.day = day
        self.start_hr = str(start_hr).strip() if len(str(start_hr).strip()) == 2 else "0{}".format(str(start_hr).strip())
        self.end_hr = str(end_hr).strip() if len(str(end_hr).strip()) == 2 else "0{}".format(str(end_hr).strip())
        self.time_period = "{}:00-{}:00".format(self.start_hr, self.end_hr)
        self.type = type_ if type_ else None

    def __str__(self):
         return "Day: {}. Slot: {}.".format(self.day, self.time_period)

class Volunteer(object):
    def __init__(self, first_name, last_name, email, gender, contact_no, undergrad, total_shifts, first_time):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.gender = gender
        self.contact_no = contact_no
        self.undergrad = undergrad
        self.total_shifts = total_shifts
        self.first_time = first_time
        self.available_slots = []
        self.assigned_slots = []

        #self.sanitize_data() # Be careful with this function and where it is called!!

    def sanitize_data(self):
        if '@' not in self.email:
            print("WARNING: User {} has incorrect email: {}".format(self.email, self.email))

        try:
            int(self.contact_no)
        except:
            print("WARNING: User {} has questionable phone number: {}".format(self.email, self.contact_no))

        try:
            int(self.total_shifts)
        except:
            print("WARNING: User {} has questionable total shifts: {}".format(self.email, self.total_shifts))
            if len(self.available_slots) > MAX_SLOTS:
                self.total_shifts = MAX_SLOTS
            else:
                self.total_shifts = len(self.available_slots)

        try:
            int(self.first_time)
        except:
            if str(self.first_time).lower() == 'yes':
                self.first_time = 1
            elif str(self.first_time).lower() == 'no':
                self.first_time = 0
            else:
                print("WARNING: User {} has questionable first time resonse: {}".format(self.email, self.first_time))

        try:
            int(self.undergrad)
        except:
            if 'undergraduate' in str(self.undergrad).lower():
                self.undergrad = 1
            else:
                self.undergrad = 0


    def __str__(self):
        return "Name: {} {}. \nEmail: {}\nGender: {} \nPhone number: {}. \nUndergrad: {}. Total shifts possible: {}. First Time?: {}.".format(self.first_name,
                self.last_name, self.email, self.gender, self.contact_no, "Yes" if self.undergrad else "No", self.total_shifts, "Yes" if self.first_time else "No")
