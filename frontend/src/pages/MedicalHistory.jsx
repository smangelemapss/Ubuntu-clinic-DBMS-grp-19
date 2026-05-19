import { useState, useEffect } from 'react'
import { FileText, Stethoscope, Building2, Eye } from 'lucide-react'
import { getMedicalRecords, getMedicalRecordById } from '../services/api'
import PageHeader from '../components/ui/PageHeader'
import PageLoading from '../components/ui/PageLoading'
import EmptyState from '../components/ui/EmptyState'
import Modal from '../components/ui/Modal'

const MedicalHistory = () => {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedRecord, setSelectedRecord] = useState(null)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    getMedicalRecords()
      .then(setRecords)
      .catch((err) => console.error('Error loading medical records:', err))
      .finally(() => setLoading(false))
  }, [])

  const handleViewDetails = async (id) => {
    try {
      const record = await getMedicalRecordById(id)
      setSelectedRecord(record)
      setShowModal(true)
    } catch (err) {
      console.error('Error loading record details:', err)
    }
  }

  if (loading) {
    return <PageLoading message="Loading medical records..." />
  }

  return (
    <>
      <PageHeader
        eyebrow="Health records"
        icon={FileText}
        title="Medical history"
        subtitle="Diagnoses, prescriptions, and visit notes from your campus clinic consultations."
      />

      {records.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No medical records yet"
          description="Your visit history and diagnoses will appear here after consultations."
        />
      ) : (
        <div className="list-stack">
          {records.map((record) => (
            <article key={record.id} className="list-card">
              <div className="list-card__header">
                <div>
                  <h3 className="list-card__title">{record.date}</h3>
                  <p className="list-card__meta">
                    <Stethoscope size={14} aria-hidden="true" />
                    Dr. {record.doctor}
                  </p>
                </div>
                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={() => handleViewDetails(record.id)}
                >
                  <Eye size={16} aria-hidden="true" />
                  View Details
                </button>
              </div>
              <div className="list-card__body">
                <p>
                  <strong>Diagnosis:</strong> {record.diagnosis}
                </p>
                <p className="list-card__meta" style={{ marginTop: '0.35rem' }}>
                  <Building2 size={14} aria-hidden="true" />
                  {record.department}
                </p>
              </div>
            </article>
          ))}
        </div>
      )}

      {showModal && selectedRecord && (
        <Modal title="Medical Record Details" onClose={() => setShowModal(false)}>
          <div className="detail-list">
            <div className="detail-row">
              <span className="detail-row__label">Date</span>
              <span className="detail-row__value">{selectedRecord.date}</span>
            </div>
            <div className="detail-row">
              <span className="detail-row__label">Doctor</span>
              <span className="detail-row__value">Dr. {selectedRecord.doctor}</span>
            </div>
            <div className="detail-row">
              <span className="detail-row__label">Department</span>
              <span className="detail-row__value">{selectedRecord.department}</span>
            </div>
            <div className="detail-row">
              <span className="detail-row__label">Diagnosis</span>
              <span className="detail-row__value">{selectedRecord.diagnosis}</span>
            </div>
            {selectedRecord.symptoms && (
              <div className="detail-row">
                <span className="detail-row__label">Symptoms</span>
                <span className="detail-row__value">{selectedRecord.symptoms}</span>
              </div>
            )}
            {selectedRecord.prescription && (
              <div className="detail-row">
                <span className="detail-row__label">Prescription</span>
                <span className="detail-row__value">{selectedRecord.prescription}</span>
              </div>
            )}
          </div>
        </Modal>
      )}
    </>
  )
}

export default MedicalHistory
