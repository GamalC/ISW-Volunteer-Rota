# ISW Volunteer Rota READMe

This repository contains code to create a rota of volunteers signed up to tke part in CGS' annual International Student Welcome (http://www.societies.cam.ac.uk/cgs/isw/) programme. Part of it involves
meeting new students of Cambridge University at the Coach and Train stations. This usually involves matching approximately 50-80 volunteers into approximately 150 slots over an appromimately 2 week period. 
This code seeks to automate the process.

**Features:**
+ Reads availabilities from a file containing signups from an online form.
+ Creates slots for coach and train station based on given start and end dates.
+ Assigns persons to slots they signed up as being available for.
+ Does not schedule a single volunteer to multiple shifts on the same day. (Though it may give last shift one day and first shift next day)
+ Starts with least available persons and least subscribed slots.
+ Limits amount of assigned slots to the amount persons indicated as their maximum.
+ Matches experienced persons with inexperienced.
+ Schedules undergraduates before postgraduates who may be needed for other duties besides waiting at teh station.
+ Deals with duplicate signups (detects it and delete earlier one)
+ Allows command line usage to specify things which may change from year to year
+ Outputs rota and simplified rota files
+ Outputs suggestions of persons who may be available to fill a currently unassigned slot but were not due to certain (possibly soft) constraints. 

*Possible TODOs:*
+ More documentation?
+ Station affinity (keep persons at same station as much as possible)
+ Time affinity (giving persons same times each day as much as possible)
+ Ensure no schedule clashes with ISW events.

**Dependencies**
+ Python 2.7
+ Pandas

**Usage**

$ **python** script.py --input-file "Volunteer_Sign-Up_.csv" --coach-start-day 20160922 --coach-end-day 20161002 --coach-start-hour 9 --coach-end-hour 19 --train-start-day 20160924 --train-end-day 20161001 --train-start-hour 9 --train-end-hour 19  --slot-length 2 --max-slots 5


It is also possible to pre-assign slots to particular users so that the script skips them on execution. Lines of files specifying this information need to be of form: <volunteer email>,<slot day>,<slot start hour>,<slot end hour>,<slot type>.
  
*Use Case:* After assigning volunteers to rota, persons may sign up after or persons may become unavailable, so the script needs to be re-run but with no disruption to the slots of other assigned volunteers. The information of unaffected assignments can be passed in this way. The script also now outputs the rota in a file of this format for use in future runs if needed as 'last_assigned_slots.csv'.
  
**Usage**

$ **python** script.py --input-file "volunteers_2017_master.csv" --coach-start-day 20170920 --coach-end-day 20171001 --coach-start-hour 9 --coach-end-hour 21 --train-start-day 20170923 --train-end-day 20171001 --train-start-hour 11 --train-end-hour 21 --slot-length 2 --max-slots 5 --year 2017 **--assigned-slots-file "assigned_slots.csv"**
