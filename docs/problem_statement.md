# Problem Statement

Hospital staff must allocate a limited number of doctor appointment slots to patients. A valid schedule must assign every patient exactly one appointment, avoid doctor double-booking, and never schedule a patient before their requested slot.

The project applies a Genetic Algorithm to select the best valid schedule from the possible alternatives. The objective is:

```text
Objective cost = 100 x total delay + preference deviation
```

The high delay weight makes patient waiting time the primary objective. Preference deviation is a secondary objective that measures the difference between a patient's preferred and assigned slot.

## Inputs

Each CSV row requires these columns:

```text
patient_id,specialty,doctor,requested_slot,preferred_slot
```

Slots are numbered from 1 to 6 and represent 30-minute appointments from 09:00 to 12:00.

## Hard Constraints

1. Each patient receives exactly one appointment.
2. An assigned slot cannot be earlier than the requested slot.
3. A doctor cannot have more than one patient in the same slot.
4. Only slots 1 through 6 may be used.

## Genetic Algorithm Design

- **Chromosome:** integer list; each position is a patient and each value is an assigned slot.
- **Population:** valid baseline, known-good, and randomly generated valid schedules.
- **Selection:** the lower-cost schedules are chosen as parents.
- **Crossover:** one-point crossover creates a child from two parents.
- **Mutation:** one patient slot changes randomly.
- **Repair:** invalid children are corrected to remove conflicts and early appointments.
- **Termination:** fixed number of generations, with 100 as the default.
