from classes import *

#SCHEDULED_YEAR = '2015'
MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
            'september', 'october', 'november', 'december']
#MAX_SLOTS = 5 #maximum slots to assign to volunteers who did not specify a clear max

def convert_to_date(string_date, scheduled_year):
    parts = string_date.split()
    day = parts[1]
    month = parts[2].lower()
    assert month in MONTHS, "Month {} not valid.".format(month)
    month = MONTHS.index(month) + 1

    #print("converted {} to {}".format(string_date, "{}{}{}".format(SCHEDULED_YEAR,
    #        month if len(str(month)) == 2 else "0{}".format(month),
    #        day if len(str(day)) == 2 else "0{}".format(day))))
    return "{}{}{}".format(scheduled_year,
            month if len(str(month)) == 2 else "0{}".format(month),
            day if len(str(day)) == 2 else "0{}".format(day))

def sanitize_data(volunteer_lst, max_slots):
    emails = []
    duplicates = []
    for vol in volunteer_lst:
        if vol.email in emails:
            print("WARNING: Possible Duplicate: {} {} ({}). Deleting earlier.".format(vol.first_name,
                    vol.last_name, vol.email))
            duplicates.append(vol.email)
        vol.sanitize_data(max_slots) #Makes 'first time' field binary and sanitizes offered slots based on available slots
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

def experience_match(volunteer, volunteers, slot):
    """
    Returns true if it OK add the olunteer to this slot as far as experience goes.
    That is if the other person assigned to the slot is experienced.
    Only returns false if someone else already assigned to slot and the current volunteer is inexperienced.
    so seeks to avoid all inexperienced persons at slot.
    """
    if not volunteer.first_time:
        return True
    elif slot.type != 'coach2':
        return True #Brittle alert. Uses knowledge of the task: that this only matters currently for persons at coach 2
    else:
        for volunteer2 in volunteers:
            for a_slot in volunteer2.assigned_slots:
                if a_slot.day == slot.day and a_slot.time_period == slot.time_period:
                    #This should only match for coach 2 slots with same day and time period
                    if volunteer2.first_time:
                        #print("Not matching {} {} and {} {} for slot {} {} {}".format(volunteer.first_name,
                        #    volunteer.last_name, volunteer2.first_name, volunteer2.last_name,
                        #    slot.day, slot.time_period, slot.type))
                        return False
                    #else:
                    #    print("OK to match {} {} and {} {} for slot {} {}".format(volunteer.first_name,
                    #        volunteer.last_name, volunteer2.first_name, volunteer2.last_name,
                    #        slot.day, slot.time_period))
        return True

def output_rota(coach_available_slots, volunteer_lst):
    csv_output = "First Name, Surname, Email, Gender, Undergrad, experienced, offered, scheduled,"
    second_line = ",,,,,,,,"
    for slot in coach_available_slots:
         csv_output += "{},".format(slot.day)
         second_line += "{},".format(slot.time_period)
    csv_output =  csv_output + '\n' + second_line + '\n'

    for volunteer in volunteer_lst:
        offered = str(volunteer.total_shifts).replace(',', ' ')
        offered = offered.replace('-', ' to ')
        offered = offered.replace('nan', 'No Response')
        #print("Volunteer first time: {}".format(volunteer.first_time))
        line = "{},{},{},{},{},{},{},{},".format(volunteer.first_name, volunteer.last_name,
            volunteer.email, volunteer.gender, 'Y' if volunteer.undergrad else 'N',
             'Y' if not volunteer.first_time else 'N', offered, len(volunteer.assigned_slots))
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

def output_simplified_rota(coach_available_slots, volunteer_lst):
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
