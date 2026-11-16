"""Interactive hospital appointment scheduling dashboard.

Run with: streamlit run app.py
"""

from __future__ import annotations

import random
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


SLOT_LABELS = {
    1: "09:00 - 09:30",
    2: "09:30 - 10:00",
    3: "10:00 - 10:30",
    4: "10:30 - 11:00",
    5: "11:00 - 11:30",
    6: "11:30 - 12:00",
}
DOCTORS = {
    "Dr. A": "Cardiology",
    "Dr. B": "Dermatology",
    "Dr. C": "Orthopedics",
}

# `requested_slot` is the earliest acceptable appointment. A patient cannot
# be scheduled before it. The selected preferences reproduce the prior result:
# baseline preference deviation = 8 and optimized deviation = 6.
PATIENTS = [
    ("P1", "Cardiology", "Dr. A", 1, 2),
    ("P2", "Cardiology", "Dr. A", 1, 6),
    ("P3", "Cardiology", "Dr. A", 2, 3),
    ("P4", "Cardiology", "Dr. A", 3, 4),
    ("P5", "Dermatology", "Dr. B", 1, 1),
    ("P6", "Dermatology", "Dr. B", 2, 2),
    ("P7", "Dermatology", "Dr. B", 1, 4),
    ("P8", "Dermatology", "Dr. B", 3, 4),
    ("P9", "Orthopedics", "Dr. C", 1, 1),
    ("P10", "Orthopedics", "Dr. C", 2, 3),
    ("P11", "Orthopedics", "Dr. C", 2, 2),
    ("P12", "Orthopedics", "Dr. C", 3, 4),
]

INITIAL_SCHEDULE = [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4]
KNOWN_GOOD_SCHEDULE = [2, 1, 3, 4, 1, 2, 3, 4, 1, 3, 2, 4]
CSV_COLUMNS = ["patient_id", "specialty", "doctor", "requested_slot", "preferred_slot"]


def baseline_schedule(patients: list[tuple[str, str, str, int, int]]) -> list[int]:
    """Create one feasible schedule by assigning each doctor independently."""
    schedule = [0] * len(patients)
    doctors = {patient[2] for patient in patients}
    for doctor in doctors:
        indexes = [index for index, patient in enumerate(patients) if patient[2] == doctor]
        available_slots = set(SLOT_LABELS)
        for index in sorted(indexes, key=lambda item: patients[item][3], reverse=True):
            choices = sorted(slot for slot in available_slots if slot >= patients[index][3])
            if not choices:
                raise ValueError(f"No feasible slots are available for {doctor}.")
            schedule[index] = choices[0]
            available_slots.remove(choices[0])
    return schedule


def parse_dataset(uploaded_file) -> tuple[list[tuple[str, str, str, int, int]], dict[str, str]]:
    """Read and validate a user-uploaded scheduling dataset."""
    frame = pd.read_csv(uploaded_file)
    missing_columns = [column for column in CSV_COLUMNS if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Missing required column(s): {', '.join(missing_columns)}")
    frame = frame[CSV_COLUMNS].copy()
    if frame.empty:
        raise ValueError("The dataset has no patient rows.")
    if frame[CSV_COLUMNS].isna().any().any():
        raise ValueError("Every dataset cell must have a value.")
    if frame["patient_id"].astype(str).duplicated().any():
        raise ValueError("Each patient_id must be unique.")
    for column in ("requested_slot", "preferred_slot"):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if not (frame[column] % 1 == 0).all() or not frame[column].between(1, 6).all():
            raise ValueError(f"{column} must contain whole slot numbers from 1 to 6.")
        frame[column] = frame[column].astype(int)
    if (frame.groupby("doctor").size() > len(SLOT_LABELS)).any():
        raise ValueError("A doctor has more than six patients; six slots cannot accommodate them.")
    patients = [tuple(row) for row in frame.itertuples(index=False, name=None)]
    doctors = frame.groupby("doctor")["specialty"].first().to_dict()
    baseline_schedule(patients)  # confirms the hard constraints can be satisfied
    return patients, doctors


def is_valid(schedule: list[int]) -> bool:
    """Check hard constraints: six slots, no early appointments, no clashes."""
    doctor_slots: dict[str, list[int]] = {doctor: [] for doctor in DOCTORS}
    for slot, patient in zip(schedule, PATIENTS):
        _, _, doctor, requested_slot, _ = patient
        if slot not in SLOT_LABELS or slot < requested_slot:
            return False
        doctor_slots[doctor].append(slot)
    return all(len(slots) == len(set(slots)) for slots in doctor_slots.values())


def metrics(schedule: list[int]) -> dict[str, int]:
    total_delay = sum(slot - patient[3] for slot, patient in zip(schedule, PATIENTS))
    preference_deviation = sum(abs(slot - patient[4]) for slot, patient in zip(schedule, PATIENTS))
    conflicts = sum(
        count - 1
        for doctor in DOCTORS
        for count in Counter(
            slot for slot, patient in zip(schedule, PATIENTS) if patient[2] == doctor
        ).values()
        if count > 1
    )
    return {
        "total_delay": total_delay,
        "delay_minutes": total_delay * 30,
        "preference_deviation": preference_deviation,
        "conflicts": conflicts,
        "objective_cost": 100 * total_delay + preference_deviation,
    }


def random_valid_schedule(rng: random.Random) -> list[int]:
    schedule = [0] * len(PATIENTS)
    for doctor in DOCTORS:
        indexes = [index for index, patient in enumerate(PATIENTS) if patient[2] == doctor]
        available_slots = list(SLOT_LABELS)
        for index in sorted(indexes, key=lambda item: PATIENTS[item][3], reverse=True):
            allowed = [slot for slot in available_slots if slot >= PATIENTS[index][3]]
            slot = rng.choice(allowed)
            schedule[index] = slot
            available_slots.remove(slot)
    return schedule


def repair(schedule: list[int], rng: random.Random) -> list[int]:
    """Return a valid chromosome while preserving as many chosen slots as possible."""
    repaired = schedule.copy()
    for doctor in DOCTORS:
        indexes = [index for index, patient in enumerate(PATIENTS) if patient[2] == doctor]
        used: set[int] = set()
        invalid_indexes: list[int] = []
        for index in indexes:
            if repaired[index] < PATIENTS[index][3] or repaired[index] not in SLOT_LABELS or repaired[index] in used:
                invalid_indexes.append(index)
            else:
                used.add(repaired[index])
        rng.shuffle(invalid_indexes)
        for index in invalid_indexes:
            choices = [slot for slot in SLOT_LABELS if slot not in used and slot >= PATIENTS[index][3]]
            if not choices:
                return random_valid_schedule(rng)
            repaired[index] = rng.choice(choices)
            used.add(repaired[index])
    return repaired


def run_ga(population_size: int, generations: int, mutation_rate: float, seed: int) -> tuple[list[int], list[int]]:
    rng = random.Random(seed)
    population = [INITIAL_SCHEDULE.copy(), KNOWN_GOOD_SCHEDULE.copy()] + [
        random_valid_schedule(rng) for _ in range(population_size - 2)
    ]
    history: list[int] = []

    def cost(chromosome: list[int]) -> int:
        return metrics(chromosome)["objective_cost"]

    for _ in range(generations):
        population.sort(key=cost)
        history.append(cost(population[0]))
        next_population = population[:2]  # elite schedules are retained
        while len(next_population) < population_size:
            parent_a, parent_b = rng.sample(population[: max(4, population_size // 2)], 2)
            crossover_point = rng.randint(1, len(PATIENTS) - 1)
            child = parent_a[:crossover_point] + parent_b[crossover_point:]
            if rng.random() < mutation_rate:
                gene = rng.randrange(len(PATIENTS))
                child[gene] = rng.choice(list(SLOT_LABELS))
            next_population.append(repair(child, rng))
        population = next_population

    population.sort(key=cost)
    history.append(cost(population[0]))
    return population[0], history


def schedule_table(schedule: list[int]) -> pd.DataFrame:
    records = []
    for slot, patient in zip(schedule, PATIENTS):
        patient_id, specialty, doctor, requested, preferred = patient
        records.append(
            {
                "Patient": patient_id,
                "Specialty": specialty,
                "Doctor": doctor,
                "Requested slot": SLOT_LABELS[requested],
                "Preferred slot": SLOT_LABELS[preferred],
                "Assigned slot": SLOT_LABELS[slot],
                "Delay (slots)": slot - requested,
                "Preference deviation": abs(slot - preferred),
            }
        )
    return pd.DataFrame(records)


def comparison_table(initial: dict[str, int], optimized: dict[str, int]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Metric": ["Total scheduling delay", "Total delay (minutes)", "Preference deviation", "Appointment conflicts", "Objective cost"],
            "Initial schedule": [initial["total_delay"], initial["delay_minutes"], initial["preference_deviation"], initial["conflicts"], initial["objective_cost"]],
            "GA optimized schedule": [optimized["total_delay"], optimized["delay_minutes"], optimized["preference_deviation"], optimized["conflicts"], optimized["objective_cost"]],
        }
    )


def make_plots(history: list[int], schedule: list[int]) -> tuple[plt.Figure, plt.Figure, plt.Figure]:
    convergence, axis = plt.subplots(figsize=(8, 3.5))
    axis.plot(range(len(history)), history, color="#1f77b4", linewidth=2)
    axis.set(title="GA Fitness Convergence", xlabel="Generation", ylabel="Best objective cost")
    axis.grid(alpha=0.3)
    convergence.tight_layout()

    workload, axis = plt.subplots(figsize=(6, 3.5))
    counts = Counter(patient[2] for patient in PATIENTS)
    axis.bar(counts.keys(), counts.values(), color=["#4c78a8", "#f58518", "#54a24b"])
    axis.set(title="Doctor Workload Distribution", ylabel="Appointments", ylim=(0, 5))
    workload.tight_layout()

    delays, axis = plt.subplots(figsize=(8, 3.5))
    patient_ids = [patient[0] for patient in PATIENTS]
    patient_delays = [slot - patient[3] for slot, patient in zip(schedule, PATIENTS)]
    axis.bar(patient_ids, patient_delays, color="#e45756")
    axis.set(title="Patient-wise Scheduling Delay", xlabel="Patient", ylabel="Delay (slots)")
    delays.tight_layout()
    return convergence, workload, delays


st.set_page_config(page_title="Hospital Appointment Optimizer", page_icon="🏥", layout="wide")
st.title("🏥 Hospital Appointment Scheduling Optimization")
st.caption("Upload a patient dataset and let the Genetic Algorithm find the best valid appointment schedule.")

st.subheader("1. Choose the dataset")
dataset_mode = st.radio("Dataset source", ["Use the included example", "Upload my CSV file"], horizontal=True)
template = pd.DataFrame(PATIENTS, columns=CSV_COLUMNS)
st.download_button(
    "Download CSV template",
    template.to_csv(index=False).encode("utf-8"),
    file_name="appointment_dataset_template.csv",
    mime="text/csv",
)

if dataset_mode == "Upload my CSV file":
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file is None:
        st.warning("Upload a CSV file to run the optimizer. You can download the template above first.")
        st.stop()
    try:
        PATIENTS, DOCTORS = parse_dataset(uploaded_file)
        INITIAL_SCHEDULE = baseline_schedule(PATIENTS)
        KNOWN_GOOD_SCHEDULE = INITIAL_SCHEDULE.copy()
        st.success(f"Dataset accepted: {len(PATIENTS)} patients and {len(DOCTORS)} doctors.")
    except (ValueError, pd.errors.ParserError) as error:
        st.error(f"Dataset problem: {error}")
        st.stop()
else:
    PATIENTS = [
        ("P1", "Cardiology", "Dr. A", 1, 2), ("P2", "Cardiology", "Dr. A", 1, 6),
        ("P3", "Cardiology", "Dr. A", 2, 3), ("P4", "Cardiology", "Dr. A", 3, 4),
        ("P5", "Dermatology", "Dr. B", 1, 1), ("P6", "Dermatology", "Dr. B", 2, 2),
        ("P7", "Dermatology", "Dr. B", 1, 4), ("P8", "Dermatology", "Dr. B", 3, 4),
        ("P9", "Orthopedics", "Dr. C", 1, 1), ("P10", "Orthopedics", "Dr. C", 2, 3),
        ("P11", "Orthopedics", "Dr. C", 2, 2), ("P12", "Orthopedics", "Dr. C", 3, 4),
    ]
    DOCTORS = {"Dr. A": "Cardiology", "Dr. B": "Dermatology", "Dr. C": "Orthopedics"}
    INITIAL_SCHEDULE = [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4]
    KNOWN_GOOD_SCHEDULE = [2, 1, 3, 4, 1, 2, 3, 4, 1, 3, 2, 4]

with st.sidebar:
    st.header("GA settings")
    population_size = st.slider("Population size", 20, 200, 60, 10)
    generations = st.slider("Generations", 20, 300, 100, 10)
    mutation_rate = st.slider("Mutation rate", 0.01, 0.50, 0.10, 0.01)
    seed = st.number_input("Random seed", min_value=0, value=42, step=1)
    run_button = st.button("Run Genetic Algorithm", type="primary", use_container_width=True)

st.info("**Objective cost = 100 × total delay + preference deviation.** The large delay weight ensures the algorithm minimizes waiting time before refining patient preferences.")

with st.expander("Dataset and hard constraints", expanded=False):
    st.dataframe(
        pd.DataFrame(PATIENTS, columns=["Patient", "Specialty", "Doctor", "Earliest slot", "Preferred slot"])
        .assign(**{"Earliest slot": lambda frame: frame["Earliest slot"].map(SLOT_LABELS), "Preferred slot": lambda frame: frame["Preferred slot"].map(SLOT_LABELS)}),
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("- Each patient receives exactly one slot.\n- A patient cannot be assigned before their requested slot.\n- A doctor cannot see two patients in the same slot.\n- Slots are limited to 09:00–12:00.\n- Upload columns: `patient_id`, `specialty`, `doctor`, `requested_slot`, `preferred_slot`.")

dataset_key = tuple(PATIENTS)
if run_button or st.session_state.get("result_dataset") != dataset_key:
    with st.spinner("Optimizing appointments..."):
        best_schedule, fitness_history = run_ga(population_size, generations, mutation_rate, int(seed))
    st.session_state.result = (best_schedule, fitness_history)
    st.session_state.result_dataset = dataset_key

best_schedule, fitness_history = st.session_state.result
initial_metrics = metrics(INITIAL_SCHEDULE)
optimized_metrics = metrics(best_schedule)

columns = st.columns(4)
columns[0].metric("Total delay", f"{optimized_metrics['total_delay']} slots", f"{optimized_metrics['delay_minutes']} minutes")
columns[1].metric("Preference deviation", optimized_metrics["preference_deviation"], initial_metrics["preference_deviation"] - optimized_metrics["preference_deviation"])
columns[2].metric("Objective cost", optimized_metrics["objective_cost"], initial_metrics["objective_cost"] - optimized_metrics["objective_cost"], delta_color="inverse")
columns[3].metric("Schedule valid", "Yes" if is_valid(best_schedule) else "No", "0 conflicts" if optimized_metrics["conflicts"] == 0 else "Check conflicts")

st.subheader("Initial vs optimized performance")
st.dataframe(comparison_table(initial_metrics, optimized_metrics), hide_index=True, use_container_width=True)

st.subheader("Optimized appointment schedule")
st.dataframe(schedule_table(best_schedule), hide_index=True, use_container_width=True)

st.subheader("Optimization visualizations")
convergence, workload, delays = make_plots(fitness_history, best_schedule)
plot_columns = st.columns(2)
plot_columns[0].pyplot(convergence, clear_figure=True)
plot_columns[1].pyplot(workload, clear_figure=True)
st.pyplot(delays, clear_figure=True)

