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

**Usage**

$ **python** script.py --input-file "Volunteer_Sign-Up_.csv" --coach-start-day 20160922 --coach-end-day 20161002 --coach-start-hour 9 --coach-end-hour 19 --train-start-day 20160924 --train-end-day 20161001 --train-start-hour 9 --train-end-hour 19  --slot-length 2 --max-slots 5
