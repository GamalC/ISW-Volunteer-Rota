import sys
import csv
import pandas as pd

from utilities import *
from classes import *

volunteer_init_label = ["First name", "Last name", "Email address",
"Contact phone number", "Academic Category", "How many 2-hour shifts would you be able to do in total?",
"Is this your first time volunteering at the coach/train station?"]

def argparser():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--input-file', help='Input .csv file')
    ap.add_argument('-y', '--year', help='Year of ISW. Example: 2017')
    ap.add_argument('-csd', '--coach-start-day', help='Day to start at coach station (format: yyyymmdd)')
    ap.add_argument('-ced', '--coach-end-day', help='Day to end at coach station (format: yyyymmdd)')
    ap.add_argument('-csh', '--coach-start-hour', help='Hour to start at coach station (24 hr format). Example: 9')
    ap.add_argument('-ceh', '--coach-end-hour', help='Hour to end at coach station (24 hr format). Example: 19')
    ap.add_argument('-tsd', '--train-start-day', help='Day to start at train station (format: yyyymmdd)')
    ap.add_argument('-ted', '--train-end-day', help='Day to end at train station (format: yyyymmdd)')
    ap.add_argument('-tsh', '--train-start-hour', help='Hour to start at train station (24 hr format). Example: 9')
    ap.add_argument('-teh', '--train-end-hour', help='Hour to end at train station (24 hr format). Example: 19')
    ap.add_argument('-l', '--slot-length', default=2, help='Amount of hours of each slot (default 2)')
    ap.add_argument('-ms', '--max-slots', default=5, help='Maximum amount of slots to give to persons who do not specify (default 5)')
    ap.add_argument('-asf', '--assigned-slots-file', default=None, help='File to read pre-assigned slots from. (default None)')

    return ap

#fpath = "Volunteer Sign-Up ISW 2016 [Form] (Responses).csv"
def do_rota(input_file, year, coach_start_day, coach_end_day, coach_start_hour,
    coach_end_hour, train_start_day, train_end_day, train_start_hour, train_end_hour,
    slot_length, max_slots, assigned_slots_file):

    MAX_SLOTS = max_slots #maximum slots to assign to volunteers who did not specify a clear max

    #From sign-up file, read volunteers and their signup times
    volunteer_lst = []
    with open(input_file, 'rb') as csvfile:
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

            signups[email] = {}
            for s_key in signup_keys:
                if str(volunteers[s_key][ind]) != 'nan':
                    signups[email][s_key] = volunteers[s_key][ind]
                    for time_period in volunteers[s_key][ind].split(','):
                        date = convert_to_date(s_key, year)
                        start_time = time_period.split('-')[0]
                        end_time = time_period.split('-')[1]
                        start_hr = start_time.split(':')[0].strip()
                        end_hr = end_time.split(':')[0].strip()
                        slot = Slot(date, start_hr, end_hr)
                        vol.available_slots.append(slot)

    sanitize_data(volunteer_lst, max_slots)

    #Match volunteers to available slots
    #coach_available_slots = get_available_slots('20160922', '20161002', '09', '19', 'coach')
    #train_avilable_slots = get_available_slots('20160924', '20161001', '09', '19', 'train')
    #coach_available_slots2 = get_available_slots('20160922', '20161002', '09', '19', 'coach2')
    coach_available_slots = get_available_slots(coach_start_day, coach_end_day, coach_start_hour, coach_end_hour, 'coach', slot_length)
    train_avilable_slots = get_available_slots(train_start_day, train_end_day, train_start_hour, train_end_hour, 'train', slot_length)
    coach_available_slots2 = get_available_slots(coach_start_day, coach_end_day, coach_start_hour, coach_end_hour, 'coach2', slot_length)

    assigned_slots = []
    undergrads = [vol for vol in volunteer_lst if vol.undergrad]
    non_undergrads = [vol for vol in volunteer_lst if not vol.undergrad]
    print("There are {} undergrads and {} non-undergrads".format(len(undergrads), len(non_undergrads)))

    #Read already assigned slots from file if provided
    if assigned_slots_file:
        asf = open(assigned_slots_file, 'r')
        with open(assigned_slots_file, 'r') as asffile:
            asf = csv.reader(asffile, delimiter=',')
            for line in asf:
                if len(line) == 5:
                    vol_email = line[0]
                    slot_day = line[1]
                    slot_start_hr = line[2]
                    slot_end_hr = line[3]
                    slot_type = line[4]
                    focus_vol = None
                    #find volunteer
                    for vol in volunteer_lst:
                        if vol.email == vol_email:
                            focus_vol = vol
                            break
                    #find slot
                    avail_slots = coach_available_slots + train_avilable_slots + coach_available_slots2
                    focus_slot = get_slot(slot_day, slot_start_hr, slot_end_hr, avail_slots, slot_type)
                    if focus_slot and focus_vol:
                        print("Pre-assigning {} to {}-{}-{}".format(focus_vol.email, focus_slot.day,
                                focus_slot.time_period,focus_slot.type))
                        focus_vol.assigned_slots.append(focus_slot)
                        assigned_slots.append(focus_slot)
                else:
                    print("Assigned slots file had invalid amount of values: {}".format(len(line)))

    constrained_slots = {}
    for available_slots in [coach_available_slots, train_avilable_slots, coach_available_slots2]:
        for available_slot in available_slots:
            ordered_slots = get_ordered_slots(available_slots, volunteer_lst)

            #grouped_available_slots = get_grouped_available_slots(volunteer_lst)
            for v_lst in [undergrads, non_undergrads]:
                grouped_available_slots = get_grouped_available_slots(v_lst)
                sorted_grouped_available_slots = sorted(grouped_available_slots.keys())

                for amt in sorted_grouped_available_slots:
                    volunteers = grouped_available_slots[amt]
                    for volunteer in volunteers:
                        for slot in ordered_slots:
                            #if len(volunteer.assigned_slots) == int(volunteer.total_shifts):
                            #    continue
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
                                    if len(volunteer.assigned_slots) < int(volunteer.total_shifts):
                                        if not day_assigned(volunteer, slot):
                                            if experience_match(volunteer, volunteer_lst, slot):
                                                volunteer.assigned_slots.append(slot)
                                                assigned_slots.append(slot)
                                            else:
                                                if 'experience_match' in constrained_slots:
                                                    if (slot, volunteer) not in constrained_slots['experience_match']:
                                                        constrained_slots['experience_match'].append((slot, volunteer))
                                                else:
                                                    constrained_slots['experience_match'] = [(slot, volunteer)]
                                        else:
                                            if 'day_assigned' in constrained_slots:
                                                if (slot, volunteer) not in constrained_slots['day_assigned']:
                                                    constrained_slots['day_assigned'].append((slot, volunteer))
                                            else:
                                                constrained_slots['day_assigned'] = [(slot, volunteer)]
                                    else:
                                        if 'max_slots' in constrained_slots:
                                            if (slot, volunteer) not in constrained_slots['max_slots']:
                                                constrained_slots['max_slots'].append((slot, volunteer))
                                        else:
                                            constrained_slots['max_slots'] = [(slot, volunteer)]

    available_slots = coach_available_slots + train_avilable_slots + coach_available_slots2
    print("{} of {} slots filled. {} not filled.".format(len(assigned_slots), len(available_slots),
                                        len(available_slots) - len(assigned_slots)))
    unassigned = []
    unassigned_info = []
    for slot in available_slots:
        if not match_slot(slot, assigned_slots, ignore_type=False):
            unassigned.append("{} {} ({})".format(slot.day, slot.time_period, slot.type))
            unassigned_info.append("\n--------------------------------------------------------------")

            for key, value in constrained_slots.iteritems():
                for tup in value:
                    if tup[0] == slot:
                        unassigned_info.append("\n{} {} ({} slots remaining) could be assigned to {} {} {} if not for {} constraint.".format(
                            tup[1].first_name, tup[1].last_name, int(tup[1].total_shifts) - len(tup[1].assigned_slots),
                             slot.day, slot.time_period, slot.type, key))
    print("Unassigned slots: {}.".format(', '.join(unassigned)))

    #Output investigate unassigned slots file
    investigate_fil = open('investigate.txt', 'w')
    investigate_fil.write(' '.join(unassigned_info))

    #Output rota files
    output_rota(coach_available_slots, volunteer_lst)
    output_simplified_rota(coach_available_slots, volunteer_lst)
    output_preassigned_file(volunteer_lst) #File to become preassigned file for next use if neccessary

def main(argv):
    args = argparser().parse_args(argv[1:])
    do_rota(args.input_file, args.year, args.coach_start_day, args.coach_end_day, args.coach_start_hour,
        args.coach_end_hour, args.train_start_day, args.train_end_day, args.train_start_hour,
        args.train_end_hour, int(args.slot_length), int(args.max_slots), args.assigned_slots_file)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
