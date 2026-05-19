// F4 — Appointment Booking Page
// Rule: This component calls service functions only — never axios directly.

import { useState, useEffect } from "react";
import {
  getAvailableTimeslots,
  bookAppointment,
} from "../../services/appointmentService";

// ─── Booking type options ────────────────────────────────────────────────────
const BOOKING_TYPES = ["General Consultation", "Follow-Up", "Urgent", "Specialist"];

// ─── Helpers ─────────────────────────────────────────────────────────────────
const today = () => new Date().toISOString().split("T")[0];

const formatTime = (timeStr) => {
  if (!timeStr) return "";
  const [h, m] = timeStr.split(":");
  const hour = parseInt(h, 10);
  const ampm = hour >= 12 ? "PM" : "AM";
  const display = hour % 12 || 12;
  return `${display}:${m} ${ampm}`;
};

// ─── Step indicator ──────────────────────────────────────────────────────────
const StepIndicator = ({ current }) => {
  const steps = ["Pick a Date", "Choose a Slot", "Confirm Booking"];
  return (
    <div style={styles.stepRow}>
      {steps.map((label, i) => {
        const stepNum = i + 1;
        const done = current > stepNum;
        const active = current === stepNum;
        return (
          <div key={label} style={styles.stepItem}>
            <div
              style={{
                ...styles.stepCircle,
                background: done ? "#16a34a" : active ? "#2563eb" : "#e5e7eb",
                color: done || active ? "#fff" : "#6b7280",
              }}
            >
              {done ? "✓" : stepNum}
            </div>
            <span
              style={{
                ...styles.stepLabel,
                color: active ? "#2563eb" : done ? "#16a34a" : "#6b7280",
                fontWeight: active ? 700 : 400,
              }}
            >
              {label}
            </span>
            {i < steps.length - 1 && <div style={styles.stepLine} />}
          </div>
        );
      })}
    </div>
  );
};

// ─── Main component ──────────────────────────────────────────────────────────
export default function AppointmentBooking() {
  const [step, setStep] = useState(1);

  // Step 1 state
  const [selectedDate, setSelectedDate] = useState("");

  // Step 2 state
  const [timeslots, setTimeslots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [slotsError, setSlotsError] = useState("");
  const [selectedSlot, setSelectedSlot] = useState(null);

  // Step 3 state
  const [reasonForVisit, setReasonForVisit] = useState("");
  const [bookingType, setBookingType] = useState(BOOKING_TYPES[0]);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  // Success state
  const [confirmedAppointment, setConfirmedAppointment] = useState(null);

  // ── Step 1 → 2: fetch slots when date is chosen ───────────────────────────
  useEffect(() => {
    if (step !== 2 || !selectedDate) return;
    const fetchSlots = async () => {
      setLoadingSlots(true);
      setSlotsError("");
      setTimeslots([]);
      try {
        const data = await getAvailableTimeslots(selectedDate);
        // API returns { data: [...] } or just an array — handle both
        const slots = Array.isArray(data) ? data : data.data ?? [];
        setTimeslots(slots);
        if (slots.length === 0) setSlotsError("No available slots for this date. Please pick another day.");
      } catch (err) {
        setSlotsError("Could not load timeslots. Please try again.");
      } finally {
        setLoadingSlots(false);
      }
    };
    fetchSlots();
  }, [step, selectedDate]);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleDateNext = () => {
    if (!selectedDate) return;
    setStep(2);
  };

  const handleSlotNext = () => {
    if (!selectedSlot) return;
    setStep(3);
  };

  const handleBack = () => setStep((s) => s - 1);

  const handleSubmit = async () => {
    if (!reasonForVisit.trim()) {
      setSubmitError("Please describe your reason for visit.");
      return;
    }
    setSubmitting(true);
    setSubmitError("");
    try {
      const payload = {
        slot_id: selectedSlot.slot_id,
        staff_id: selectedSlot.staff_id,
        reason_for_visit: reasonForVisit.trim(),
        booking_type: bookingType.toUpperCase().replace(/ /g, "_"),
      };
      const result = await bookAppointment(payload);
      setConfirmedAppointment(result.data ?? result);
    } catch (err) {
      const msg =
        err?.response?.data?.error ||
        err?.response?.data?.code ||
        "Booking failed. The slot may no longer be available.";
      setSubmitError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleBookAnother = () => {
    setStep(1);
    setSelectedDate("");
    setSelectedSlot(null);
    setReasonForVisit("");
    setBookingType(BOOKING_TYPES[0]);
    setConfirmedAppointment(null);
    setSubmitError("");
    setSlotsError("");
  };

  // ─────────────────────────────────────────────────────────────────────────
  // SUCCESS SCREEN
  // ─────────────────────────────────────────────────────────────────────────
  if (confirmedAppointment) {
    return (
      <div style={styles.page}>
        <div style={{ ...styles.card, textAlign: "center", maxWidth: 480 }}>
          <div style={styles.successIcon}>✓</div>
          <h2 style={styles.successTitle}>Appointment Confirmed!</h2>
          <p style={styles.successSub}>
            Your booking is locked in. Show the QR code at the clinic reception.
          </p>

          <div style={styles.infoBox}>
            <InfoRow label="Date" value={selectedDate} />
            <InfoRow label="Time" value={formatTime(selectedSlot?.start_time)} />
            <InfoRow label="Appointment ID" value={`#${confirmedAppointment.appointment_id}`} />
            <InfoRow label="Booking Type" value={bookingType} />
          </div>

          {confirmedAppointment.qr_code_token && (
            <div style={styles.qrBox}>
              <p style={styles.qrLabel}>Your QR Token</p>
              <p style={styles.qrToken}>{confirmedAppointment.qr_code_token}</p>
              <p style={styles.qrHint}>Screenshot this or show it at reception</p>
            </div>
          )}

          <button style={styles.primaryBtn} onClick={handleBookAnother}>
            Book Another Appointment
          </button>
        </div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // BOOKING FORM
  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.pageTitle}>Book an Appointment</h1>
        <p style={styles.pageSubtitle}>Ubuntu Campus Clinic</p>

        <StepIndicator current={step} />

        {/* ── STEP 1: Pick a date ─────────────────────────────────────────── */}
        {step === 1 && (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>Select a Date</h2>
            <p style={styles.stepHint}>Choose the date you want to visit the clinic.</p>
            <input
              type="date"
              min={today()}
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              style={styles.dateInput}
            />
            <button
              style={{
                ...styles.primaryBtn,
                opacity: selectedDate ? 1 : 0.45,
                cursor: selectedDate ? "pointer" : "not-allowed",
              }}
              onClick={handleDateNext}
              disabled={!selectedDate}
            >
              See Available Slots →
            </button>
          </div>
        )}

        {/* ── STEP 2: Choose a slot ───────────────────────────────────────── */}
        {step === 2 && (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>Choose a Time Slot</h2>
            <p style={styles.stepHint}>Available slots for {selectedDate}</p>

            {loadingSlots && <p style={styles.loadingText}>Loading available slots…</p>}

            {slotsError && !loadingSlots && (
              <div style={styles.errorBox}>{slotsError}</div>
            )}

            {!loadingSlots && !slotsError && (
              <div style={styles.slotGrid}>
                {timeslots.map((slot) => (
                  <button
                    key={slot.slot_id}
                    onClick={() => setSelectedSlot(slot)}
                    style={{
                      ...styles.slotBtn,
                      ...(selectedSlot?.slot_id === slot.slot_id
                        ? styles.slotBtnActive
                        : {}),
                    }}
                  >
                    <span style={styles.slotTime}>
                      {formatTime(slot.start_time)} – {formatTime(slot.end_time)}
                    </span>
                    {slot.doctor_name && (
                      <span style={styles.slotDoctor}>Dr. {slot.doctor_name}</span>
                    )}
                  </button>
                ))}
              </div>
            )}

            <div style={styles.navRow}>
              <button style={styles.ghostBtn} onClick={handleBack}>
                ← Back
              </button>
              <button
                style={{
                  ...styles.primaryBtn,
                  opacity: selectedSlot ? 1 : 0.45,
                  cursor: selectedSlot ? "pointer" : "not-allowed",
                }}
                onClick={handleSlotNext}
                disabled={!selectedSlot}
              >
                Continue →
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 3: Confirm ─────────────────────────────────────────────── */}
        {step === 3 && (
          <div style={styles.stepContent}>
            <h2 style={styles.stepTitle}>Confirm Your Booking</h2>

            <div style={styles.infoBox}>
              <InfoRow label="Date" value={selectedDate} />
              <InfoRow label="Time" value={`${formatTime(selectedSlot?.start_time)} – ${formatTime(selectedSlot?.end_time)}`} />
              {selectedSlot?.doctor_name && (
                <InfoRow label="Doctor" value={`Dr. ${selectedSlot.doctor_name}`} />
              )}
            </div>

            <label style={styles.label}>Booking Type</label>
            <select
              value={bookingType}
              onChange={(e) => setBookingType(e.target.value)}
              style={styles.select}
            >
              {BOOKING_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>

            <label style={styles.label}>Reason for Visit *</label>
            <textarea
              rows={4}
              placeholder="Briefly describe your symptoms or reason for the appointment…"
              value={reasonForVisit}
              onChange={(e) => setReasonForVisit(e.target.value)}
              style={styles.textarea}
            />

            {submitError && <div style={styles.errorBox}>{submitError}</div>}

            <div style={styles.navRow}>
              <button style={styles.ghostBtn} onClick={handleBack} disabled={submitting}>
                ← Back
              </button>
              <button
                style={{
                  ...styles.primaryBtn,
                  opacity: submitting ? 0.6 : 1,
                  cursor: submitting ? "not-allowed" : "pointer",
                }}
                onClick={handleSubmit}
                disabled={submitting}
              >
                {submitting ? "Booking…" : "Confirm Booking"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Small helper component ───────────────────────────────────────────────────
const InfoRow = ({ label, value }) => (
  <div style={styles.infoRow}>
    <span style={styles.infoLabel}>{label}</span>
    <span style={styles.infoValue}>{value}</span>
  </div>
);

// ─── Styles ───────────────────────────────────────────────────────────────────
const styles = {
  page: {
    minHeight: "100vh",
    background: "#f1f5f9",
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "center",
    padding: "40px 16px",
    fontFamily: "'Segoe UI', sans-serif",
  },
  card: {
    background: "#ffffff",
    borderRadius: 16,
    boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
    padding: "40px 36px",
    width: "100%",
    maxWidth: 560,
  },
  pageTitle: {
    fontSize: 26,
    fontWeight: 800,
    color: "#0f172a",
    margin: 0,
  },
  pageSubtitle: {
    fontSize: 14,
    color: "#64748b",
    marginTop: 4,
    marginBottom: 28,
  },

  // Step indicator
  stepRow: {
    display: "flex",
    alignItems: "center",
    gap: 0,
    marginBottom: 32,
  },
  stepItem: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    flex: 1,
  },
  stepCircle: {
    width: 30,
    height: 30,
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 13,
    fontWeight: 700,
    flexShrink: 0,
    transition: "background 0.3s",
  },
  stepLabel: {
    fontSize: 12,
    whiteSpace: "nowrap",
    transition: "color 0.3s",
  },
  stepLine: {
    flex: 1,
    height: 2,
    background: "#e2e8f0",
    marginLeft: 8,
  },

  // Step content
  stepContent: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#1e293b",
    margin: 0,
  },
  stepHint: {
    fontSize: 14,
    color: "#64748b",
    margin: 0,
  },

  // Date input
  dateInput: {
    width: "100%",
    padding: "12px 14px",
    border: "1.5px solid #cbd5e1",
    borderRadius: 10,
    fontSize: 15,
    outline: "none",
    color: "#0f172a",
    boxSizing: "border-box",
  },

  // Slot grid
  slotGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 10,
  },
  slotBtn: {
    background: "#f8fafc",
    border: "1.5px solid #e2e8f0",
    borderRadius: 10,
    padding: "12px 10px",
    cursor: "pointer",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 4,
    transition: "all 0.2s",
  },
  slotBtnActive: {
    background: "#eff6ff",
    borderColor: "#2563eb",
  },
  slotTime: {
    fontSize: 14,
    fontWeight: 600,
    color: "#0f172a",
  },
  slotDoctor: {
    fontSize: 12,
    color: "#64748b",
  },

  // Info box (confirmation summary)
  infoBox: {
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: 10,
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  infoRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  infoLabel: {
    fontSize: 13,
    color: "#64748b",
    fontWeight: 500,
  },
  infoValue: {
    fontSize: 14,
    color: "#0f172a",
    fontWeight: 600,
  },

  // Form elements
  label: {
    fontSize: 13,
    fontWeight: 600,
    color: "#374151",
  },
  select: {
    width: "100%",
    padding: "11px 14px",
    border: "1.5px solid #cbd5e1",
    borderRadius: 10,
    fontSize: 14,
    color: "#0f172a",
    background: "#fff",
    outline: "none",
    boxSizing: "border-box",
  },
  textarea: {
    width: "100%",
    padding: "12px 14px",
    border: "1.5px solid #cbd5e1",
    borderRadius: 10,
    fontSize: 14,
    color: "#0f172a",
    resize: "vertical",
    outline: "none",
    fontFamily: "inherit",
    boxSizing: "border-box",
  },

  // Buttons
  navRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: 8,
  },
  primaryBtn: {
    background: "#2563eb",
    color: "#fff",
    border: "none",
    borderRadius: 10,
    padding: "13px 28px",
    fontSize: 15,
    fontWeight: 700,
    cursor: "pointer",
    transition: "opacity 0.2s",
    marginTop: 8,
  },
  ghostBtn: {
    background: "transparent",
    color: "#2563eb",
    border: "1.5px solid #2563eb",
    borderRadius: 10,
    padding: "11px 20px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
  },

  // Status messages
  loadingText: {
    color: "#64748b",
    fontSize: 14,
    textAlign: "center",
    padding: "20px 0",
  },
  errorBox: {
    background: "#fef2f2",
    border: "1px solid #fca5a5",
    borderRadius: 10,
    padding: "12px 16px",
    fontSize: 14,
    color: "#dc2626",
  },

  // Success screen
  successIcon: {
    width: 64,
    height: 64,
    borderRadius: "50%",
    background: "#dcfce7",
    color: "#16a34a",
    fontSize: 30,
    fontWeight: 900,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    margin: "0 auto 16px",
  },
  successTitle: {
    fontSize: 22,
    fontWeight: 800,
    color: "#0f172a",
    marginBottom: 8,
  },
  successSub: {
    fontSize: 14,
    color: "#64748b",
    marginBottom: 20,
  },
  qrBox: {
    background: "#0f172a",
    borderRadius: 12,
    padding: "20px",
    margin: "16px 0",
    textAlign: "center",
  },
  qrLabel: {
    color: "#94a3b8",
    fontSize: 12,
    fontWeight: 600,
    letterSpacing: 1,
    textTransform: "uppercase",
    margin: "0 0 8px",
  },
  qrToken: {
    color: "#38bdf8",
    fontSize: 13,
    fontFamily: "monospace",
    wordBreak: "break-all",
    margin: "0 0 8px",
  },
  qrHint: {
    color: "#64748b",
    fontSize: 11,
    margin: 0,
  },
};