# Performance Analysis

## Included 12 Patient Dataset

| Metric | Initial Schedule | GA Optimized Schedule |
|---|---:|---:|
| Total scheduling delay | 8 slots | 8 slots |
| Total delay | 240 minutes | 240 minutes |
| Preference deviation | 8 | 6 |
| Appointment conflicts | 0 | 0 |
| Objective cost | 808 | 806 |

## Interpretation

The optimized schedule reduces preference deviation by 2 points, which is a 25% improvement over the initial value. Total delay remains at 8 slots, indicating that the example's timing and doctor constraints limit further waiting-time reduction. The optimized schedule keeps zero conflicts, so it satisfies the hard constraints.

## Visualizations

The dashboard produces three graphs:

1. **Fitness convergence:** shows the best objective cost across generations.
2. **Doctor workload:** shows appointments allocated to each doctor.
3. **Patient-wise delay:** shows the delay for each patient.

## Suggested Demonstration

Run the dashboard once for each supplied dataset. Compare total delay, preference deviation, and workload as the number of patients and doctors changes. Use a fixed random seed for repeatable results during the presentation.
