# Aadhaar Inactivity Analysis Report

## 1. Top Insights (TL;DR)

1.  **The "Super-User" Phenomenon**: In identifying "inactivity," we found the opposite extreme. States like **Andaman & Nicobar Islands** and **Andhra Pradesh** have an Inactivity Index of **-50+**. This means the average enrolled user authenticates **over 50 times**, suggesting massive reliance on Aadhaar for daily services (likely PDS/Ration).
2.  **Assam's Unique Behavior**: **Assam** stands out with a **51% share of Demographic updates** (vs ~25-30% elsewhere). This indicates a population heavily focused on *correcting or updating* their data rather than just using it for authentication, potentially linked to administrative requirements like NRC.
3.  **Low Enrollment, High Usage**: Small states are punching above their weight. Despite lower total enrolment counts, their authentication infrastructure is under the heaviest load per capita.

---

## 2. Methodology

### 2.1 Data Sources
The analysis aggregates data from three primary streams:
*   **Enrolment Data:** Total registered users per state.
*   **Biometric Data:** Volume of fingerprint/iris authentications.
*   **Demographic Data:** Volume of demographic updates/authentications.

### 2.2 Metrics
We introduced the **Inactivity Index** to quantify user engagement:

$$ \text{Inactivity Index} = 1 - \frac{\text{Total Authentications}}{\text{Total Enrolment}} $$

*   **Index $\approx$ 1:** High Inactivity (Low usage relative to population).
*   **Index $\approx$ 0:** Balanced usage.
*   **Index < 0:** High Utilization (Authentication volume exceeds enrolment count, indicating frequent usage per person).

---

## 3. Key Findings

### 3.1 High Utilization States (Negative Inactivity Index)
Preliminary analysis reveals several states with a **negative Inactivity Index**, indicating that the volume of authentications far exceeds the number of enrolments. This suggests high dependency on Aadhaar-linked services (DBT, PDS, etc.).

*   **Andaman & Nicobar Islands:** Index **-53.68**. 
*   **Andhra Pradesh:** Index **-46.07**.
*   **Arunachal Pradesh:** Index **-24.05**.
*   **Assam:** Index **-7.67**.

**Observation:** In these regions, the average user authenticates multiple times, driving the index negative. This is a positive indicator of service adoption but stresses the authentication infrastructure.

### 3.2 Authentication Mix: Biometric vs. Demographic
The ratio of Demographic interactions to Total interactions varies significantly:
*   **Assam:** ~51% share of demographic activity, suggesting a high rate of updates or corrections, possibly linked to NRC-related documentation or specific state requirements.
*   **Andhra Pradesh:** ~38% demographic share.

### 3.3 Data Quality Issues
*   **Junk Records:** We identified records with state labels such as `"100000"`, which likely represent data entry errors or test anomalies.
*   **Standardization:** State names required unification (e.g., mapping "Telengana" to "Telangana", "Orissa" to "Odisha") to ensure accurate aggregation.

---

## 4. Anomaly Detection
Using Z-Score analysis, we flagged states that deviate significantly from the national average.
*   **Z > 2 (High Inactivity):** Potential ghost beneficiaries or migration **out** of the state.
*   **Z < -2 (High Activity):** Potential migration **in** or heavy reliance on daily authentication for subsidies.

*(Run the "Anomaly Detection" section in the notebook to see the updated list of specific states based on the full dataset.)*

---

## 5. Policy Recommendations

### 5.1 For High Inactivity Regions
*   **Targeted Activation Drives:** Launch awareness campaigns to encourage usage.
*   **Audit Enrolments:** Investigate potential "ghost" enrolments or dead beneficiaries if inactivity persists despite interventions.

### 5.2 For High Utilization Regions
*   **Infrastructure Upgrades:** Ensure servers and biometric devices can handle the high load (averaging >10 auths per enrolment in some cases).
*   **Failure Analysis:** If demographic authentication share is abnormally high (>50%), investigate if biometric failure rates are forcing users to fall back to demographic/OTP methods.

---

## 6. Conclusion
The analysis highlights a diverse usage landscape. While some states show immense engagement, potentially driven by welfare schemes, others require further investigation into dormancy. The **Inactivity Index** serves as a robust, scale-independent metric to track this engagement over time.
