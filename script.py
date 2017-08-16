import csv
import pandas as pd

fpath = "Volunteer Sign-Up ISW 2016 [Form] (Responses).csv"
w_a = open(fpath, "r")

SCHEDULED_YEAR = '2016'
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
            'september', 'october', 'november', 'december']
MAX_SLOTS = 5 #maximum slots to assign to volunteers who did not specify a clear max
volunteer_init_label = ["First name", "Last name", "Email address", "Gender", "Contact phone number",
 "How many 2-hour shifts would you be able to do in total?", "Is this your first time volunteering at the coach/train station?"]

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
    def __init__(self, first_name, last_name, email, gender, contact_no, total_shifts, first_time):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.gender = gender
        self.contact_no = contact_no
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


    def __str__(self):
        return "Name: {} {}. \nEmail: {}\nGender: {} \nPhone number: {}. Total shifts possible: {}. First Time?: {}.".format(self.first_name,
                self.last_name, self.email, self.gender, self.contact_no, self.total_shifts, "Yes" if self.first_time else "No")

def convert_to_date(string_date):
    parts = string_date.split()
    day = parts[1]
    month = parts[2].lower()
    assert month in MONTHS, "Month {} not valid.".format(month)
    month = MONTHS.index(month) + 1

    #print("converted {} to {}".format(string_date, "{}{}{}".format(SCHEDULED_YEAR,
    #        month if len(str(month)) == 2 else "0{}".format(month),
    #        day if len(str(day)) == 2 else "0{}".format(day))))
    return "{}{}{}".format(SCHEDULED_YEAR,
            month if len(str(month)) == 2 else "0{}".format(month),
            day if len(str(day)) == 2 else "0{}".format(day))

#From sign-up file, read volunteers and their signup times
volunteer_lst = []
with open(fpath, 'rb') as csvfile:
    volunteers = pd.read_table(csvfile, sep=',')
    signup_keys = [key for key in volunteers.keys() if 'day' in key]
    signups = {}
    for ind, email in enumerate(volunteers['Email address']):
        init_values = []
        for label in volunteer_init_label:
            init_values.append(volunteers[label][ind])
        vol = Volunteer(init_values[0], init_values[1], init_values[2], init_values[3], init_values[4], init_values[5],
                  init_values[6])
        volunteer_lst.append(vol)
        #vol.sanitize_data()

        signups[email] = {}
        for s_key in signup_keys:
            if str(volunteers[s_key][ind]) != 'nan':
                signups[email][s_key] = volunteers[s_key][ind]
                for time_period in volunteers[s_key][ind].split(','):
                    date = convert_to_date(s_key)
                    start_time = time_period.split('-')[0]
                    end_time = time_period.split('-')[1]
                    start_hr = start_time.split(':')[0].strip()
                    end_hr = end_time.split(':')[0].strip()
                    slot = Slot(date, start_hr, end_hr)
                    vol.available_slots.append(slot)


def sanitize_data(volunteers):
    emails = []
    duplicates = []
    for vol in volunteer_lst:
        if vol.email in emails:
            print("WARNING: Possible Duplicate: {} {} ({}). Deleting earlier.".format(vol.first_name,
                    vol.last_name, vol.email))
            duplicates.append(vol.email)
        vol.sanitize_data() #Makes 'first time' field binary and sanitizes offered slots based on available slots
        emails.append(vol.email)

    if len(duplicates) > 0:
        duplicate_vols = []
        for email in duplicates:
            for vol in volunteer_lst:
                if vol.email == email:
                    duplicate_vols.append(vol)
                    break
        for dup_vol in duplicate_vols:
            volunteer_lst.remove(dup_vol)
sanitize_data(volunteer_lst)

"""
for vol in volunteer_lst:
    #print(vol)
    vol.sanitize_data() #Makes 'first time' field binary and sanitizes offered slots based on available slots
    #for slot in vol.available_slots:
    #    print(slot)
    #print("\n")
"""

#Given start and end days (yyyymmdd) and start and end times (00, 24-hr format), returns a list of needed slots
def get_available_slots(start_date, end_date, start_time, end_time, type_=None, slot_length=2):
    slots = []

    start_year = int(start_date[:4])
    end_year = int(end_date[:4])
    start_month = int(start_date[4:6])
    end_month = int(end_date[4:6])
    start_day = int(start_date[6:])
    end_day = int(end_date[6:]) + 1 #hack to include last day in loop
    adj_end_date = "{}{}{}".format(end_year,
                end_month if len(str(end_month)) == 2 else "0{}".format(end_month),
                end_day if len(str(end_day)) == 2 else "0{}".format(end_day))

    cur_month_max = 30 #For this application we know this, would have to be set dynamically in while loop whenever
    #month is incremented for real implementation.
    cur_month = start_month
    cur_year = start_year
    cur_day = start_day
    cur_date = start_date

    while cur_date != adj_end_date:
        for hour in xrange(int(start_time), int(end_time), slot_length):
            slot = Slot(cur_date, hour, hour+slot_length, type_)
            slots.append(slot)
        if cur_day == cur_month_max:
            cur_day = 1
            if cur_month == 12:
                cur_month = 1
                cur_year += 1
            else:
                cur_month += 1
        else:
            cur_day += 1
        cur_date = "{}{}{}".format(cur_year,
                    cur_month if len(str(cur_month)) == 2 else "0{}".format(cur_month),
                    cur_day if len(str(cur_day)) == 2 else "0{}".format(cur_day))
    return slots

def get_ordered_slots(scheduled_slots, vols):
    """return list of slots in order of their sign-ups, from least to highest."""
    vol_cnts = {}
    for s_slot in scheduled_slots:
        s_key = "{}-{}-{}".format(s_slot.day, s_slot.time_period, s_slot.type)
        vol_cnts[s_key] = 0
        for vol in vols:
            for a_slot in vol.available_slots:
                a_key = "{}-{}".format(a_slot.day, a_slot.time_period)
                if a_key == s_key:
                    vol_cnts[s_key] += 1

    sorted_vol_cnts = sorted(vol_cnts.items(), key=lambda x: x[1])
    #print("ordered slots: {}".format(sorted_vol_cnts))
    return sorted_vol_cnts

def get_grouped_available_slots(vols):
    """return relevant volunteers grouped by the amount of slots possible."""
    vol_cnts = {}
    for vol in vols:
        slot_amt = len(vol.available_slots)
        if slot_amt < 1:
            continue
        if slot_amt in vol_cnts:
            vol_cnts[slot_amt].append(vol)
        else:
            vol_cnts[slot_amt] = [vol]

    #sorted_vol_cnts = sorted(vol_cnts.keys())
    #for amt in sorted_vol_cnts:
    #    print("{}: {}".format(amt, [vol.email for vol in vol_cnts[amt]]))
    return vol_cnts

def get_slot(day, start_hr, end_hr, slots, type_=None):
    start_hr = int(start_hr.split(':')[0])
    end_hr = int(end_hr.split(':')[0])
    start_hr = start_hr if len(str(start_hr).strip()) == 2 else "0{}".format(str(start_hr).strip())
    end_hr = end_hr if len(str(end_hr).strip()) == 2 else "0{}".format(str(end_hr).strip())
    query = "{}-{}-{}".format(day, start_hr, end_hr)
    for slot in slots:
        start_hr = slot.start_hr if len(str(slot.start_hr).strip()) == 2 else "0{}".format(str(slot.start_hr).strip())
        end_hr = slot.end_hr if len(str(slot.end_hr).strip()) == 2 else "0{}".format(str(slot.end_hr).strip())
        slot_id = "{}-{}-{}".format(slot.day, start_hr, end_hr)
        if slot_id == query:
            if not type_:
                return slot
            else:
                if slot.type == type_:
                    return slot

    return None

def match_slot(q_slot, slots_space, ignore_type=True):
    query_slot_id = "{}-{}-{}".format(q_slot.day, q_slot.start_hr, q_slot.end_hr)
    for slot in slots_space:
        slot_id = "{}-{}-{}".format(slot.day, slot.start_hr, slot.end_hr)
        if slot_id == query_slot_id:
            if ignore_type:
                return True
            else:
                if slot.type == q_slot.type:
                    return True
    return False

def day_assigned(volunteer, slot):
    for assigned_slot in volunteer.assigned_slots:
        if slot.day == assigned_slot.day:
            return True
    return False


#Match volunteers to available slots
coach_available_slots = get_available_slots('20160922', '20161002', '09', '19', 'coach')
train_avilable_slots = get_available_slots('20160924', '20161001', '09', '19', 'train')
coach_available_slots2 = get_available_slots('20160922', '20161002', '09', '19', 'coach2')

assigned_slots = []
for available_slots in [coach_available_slots, train_avilable_slots, coach_available_slots2]:
    for available_slot in available_slots:
        ordered_slots = get_ordered_slots(available_slots, volunteer_lst)
        grouped_available_slots = get_grouped_available_slots(volunteer_lst)

        sorted_grouped_available_slots = sorted(grouped_available_slots.keys())
        for amt in sorted_grouped_available_slots:
            volunteers = grouped_available_slots[amt]
            for volunteer in volunteers:
                for slot in ordered_slots:
                    if len(volunteer.assigned_slots) == int(volunteer.total_shifts):
                        continue
                    slot_id_lst = slot[0].split('-')
                    slot = get_slot(slot_id_lst[0], slot_id_lst[1], slot_id_lst[2], available_slots, slot_id_lst[3])
                    if not slot:
                        print("Slot '{}' '{}' '{}' '{}' could not be found.".format(slot_id_lst[0],
                            slot_id_lst[1], slot_id_lst[2], slot_id_lst[3]))
                    if slot and match_slot(slot, volunteer.available_slots):
                        #print("{} {} matches slot {} {}".format(volunteer.first_name, volunteer.last_name,
                        #        slot.day, slot.time_period))
                        if not match_slot(slot, assigned_slots, ignore_type=False):
                            #slot id available
                            if not day_assigned(volunteer, slot):
                                volunteer.assigned_slots.append(slot)
                                assigned_slots.append(slot)

available_slots = coach_available_slots + train_avilable_slots + coach_available_slots2
print("{} of {} slots filled. {} not filled.".format(len(assigned_slots), len(available_slots),
                                    len(available_slots) - len(assigned_slots)))
unassigned = []
for slot in available_slots:
    if not match_slot(slot, assigned_slots, ignore_type=False):
        unassigned.append("{} {} ({})".format(slot.day, slot.time_period, slot.type))
print("Unassigned slots: {}.".format(' ,'.join(unassigned)))

csv_output = "First Name, Surname, Email, Gender, experienced, offered, scheduled,"
second_line = ",,,,,,,"
for slot in coach_available_slots:
     csv_output += "{},".format(slot.day)
     second_line += "{},".format(slot.time_period)
csv_output =  csv_output + '\n' + second_line + '\n'

for volunteer in volunteer_lst:
    offered = str(volunteer.total_shifts).replace(',', ' ')
    offered = offered.replace('-', ' to ')
    offered = offered.replace('nan', 'No Response')
    #print("Volunteer first time: {}".format(volunteer.first_time))
    line = "{},{},{},{},{},{},{},".format(volunteer.first_name, volunteer.last_name,
        volunteer.email, volunteer.gender, 'Y' if not volunteer.first_time else 'N',
        offered, len(volunteer.assigned_slots))
    for slot in coach_available_slots:
        if match_slot(slot, volunteer.assigned_slots):
            for a_slot in volunteer.assigned_slots:
                if a_slot.day == slot.day and a_slot.time_period == slot.time_period:
                    #val = '1' if 'coach' in a_slot.type else '2'
                    line += "{},".format('1' if 'coach' in a_slot.type else '2')
        elif match_slot(slot, volunteer.available_slots):
            line += "{},".format('0')
        else:
            line += ","
    csv_output =  csv_output + '\n' + line

csv_file = open('rota.csv', 'w')
csv_file.write(csv_output)
csv_file.close()


simplified_output = "Day, Time, Coach, Coach, Train,\n"
for slot in coach_available_slots:
    simplified_output += "{},{},".format(slot.day, slot.time_period)
    filled = False
    for vol in volunteer_lst:
        if match_slot(slot, vol.assigned_slots):
            for a_slot in vol.assigned_slots:
                if a_slot.day == slot.day and a_slot.time_period == slot.time_period and  a_slot.type == 'coach':
                    simplified_output += "{} {},".format(vol.first_name, vol.last_name)
                    filled = True
                    break
    if not filled:
        simplified_output += "UNASSIGNED,"
    filled = False
    for vol in volunteer_lst:
        if match_slot(slot, vol.assigned_slots):
            for a_slot in vol.assigned_slots:
                if a_slot.day == slot.day and a_slot.time_period == slot.time_period and a_slot.type == 'coach2':
                    simplified_output += "{} {},".format(vol.first_name, vol.last_name)
                    filled = True
                    break
    if not filled:
        simplified_output += "UNASSIGNED,"
    filled = False
    for vol in volunteer_lst:
        if match_slot(slot, vol.assigned_slots):
            for a_slot in vol.assigned_slots:
                if a_slot.day == slot.day and a_slot.time_period == slot.time_period and a_slot.type == 'train':
                    simplified_output += "{} {},".format(vol.first_name, vol.last_name)
                    filled = True
                    break
    if not filled:
        simplified_output += "UNASSIGNED,"
    filled = False
    simplified_output += '\n'
simplified_csv_file = open('simplified_rota.csv', 'w')
simplified_csv_file.write(simplified_output)
simplified_csv_file.close()

"""
for volunteer in volunteer_lst:
    print("\n{} {} ({}):".format(volunteer.first_name, volunteer.last_name, volunteer.email))
    for slot in volunteer.assigned_slots:
        print("{}: {} ({})".format(slot.day, slot.time_period, slot.type))
"""
