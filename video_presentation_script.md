# Hospital Appointment Scheduling Optimization Video Script

**Target duration:** 5 to 7 minutes  
**Speakers:** Member 1 and Member 2  
**Before recording:** Replace the name placeholders and open the Streamlit dashboard in a browser.

## 0:00 to 0:30 - Introduction

**Member 1:** Good morning. We are [Name 1] and [Name 2]. Our project is Hospital Appointment Scheduling Optimization using a Genetic Algorithm. The goal is to generate the best valid appointment schedule while minimizing patient waiting time and improving patient preferences.

## 0:30 to 1:20 - Problem and Motivation

**Member 2:** In hospitals, doctors have limited time slots and patients may request similar times. A manual schedule can cause long waiting time, double booking, and poor use of doctor time. This is an optimization problem because many schedules may be valid, but we need the one with the lowest cost.

**Member 1:** In our model, every patient receives one slot. A patient cannot be scheduled before the requested slot. A doctor cannot have two patients in the same slot. These are hard constraints.

## 1:20 to 2:10 - Dataset and Objective

**Member 2:** Our input is a CSV dataset. It contains patient ID, specialty, doctor, requested slot, and preferred slot. We use six 30 minute slots from 9 AM to 12 PM.

**Member 1:** Our objective cost is 100 multiplied by total delay plus preference deviation. The weight 100 means patient delay is the first priority. Preference is optimized after the schedule has low delay.

## 2:10 to 3:20 - Genetic Algorithm Design

**Member 1:** We use integer chromosome representation. Each gene represents one patient, and its value is the assigned appointment slot.

**Member 2:** We begin with feasible schedules. We calculate the objective cost for each schedule. The best schedules are selected as parents. Crossover combines parts of two parent schedules. Mutation changes one slot occasionally to explore new solutions.

**Member 1:** After crossover and mutation, a repair method checks for doctor clashes or appointments before the requested slot. This ensures that the final schedule remains valid.

## 3:20 to 4:40 - Dashboard Demonstration

**Member 2:** Now we demonstrate the dashboard. First, we can use the included example dataset or upload our own CSV file. We have also prepared multiple test datasets with different patient counts and doctor workloads.

**Member 1:** In the sidebar, we can choose population size, generations, mutation rate, and random seed. When we click Run Genetic Algorithm, the system creates and improves candidate schedules.

**Member 2:** The dashboard displays the best schedule as an appointment table. It also shows total delay, preference deviation, objective cost, and whether the schedule is valid.

**Member 1:** The three charts show fitness convergence, doctor workload distribution, and patient-wise scheduling delay. For the included example, total delay remains 8 slots, while preference deviation improves from 8 to 6. This is a 25 percent improvement in the preference metric with zero appointment conflicts.

## 4:40 to 5:40 - Results and Limitations

**Member 2:** The main result is that the Genetic Algorithm finds a feasible schedule and improves patient preferences without increasing delay. The dataset can be changed without modifying the code because the dashboard accepts CSV input.

**Member 1:** One limitation is that our demonstration uses fixed 30 minute slots and fixed doctor-patient specialty assignment. Real hospitals may need emergency priority, cancellations, no-shows, variable consultation duration, and multiple doctors per specialty.

## 5:40 to 6:10 - Conclusion

**Member 2:** In conclusion, our project applies evolutionary computing to a practical hospital scheduling problem. It provides an interactive tool that can compare schedules and support better appointment decisions.

**Member 1:** Thank you. We are ready to answer questions.

## Likely Viva Questions

1. **Why is this optimization instead of only constraint satisfaction?**  
   Because several valid schedules can exist, and the project selects the one with the lowest delay and preference cost.

2. **Why did you use a Genetic Algorithm?**  
   The number of possible schedules grows quickly, so a GA searches for good solutions without enumerating every possible schedule.

3. **What is the chromosome?**  
   It is a list of slot numbers; one position corresponds to one patient.

4. **How do you avoid invalid schedules?**  
   The validation and repair functions prevent early appointments, doctor clashes, invalid slots, and duplicate appointments.

5. **Why is delay multiplied by 100?**  
   It makes delay the primary objective, so the algorithm does not increase waiting time merely to match a preferred time.
