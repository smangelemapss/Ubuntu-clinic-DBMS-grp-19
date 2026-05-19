import { useState, useEffect } from 'react'
import { Plus, Phone, User, Pencil, Trash2, ShieldAlert } from 'lucide-react'
import {
  getEmergencyContacts,
  createEmergencyContact,
  updateEmergencyContact,
  deleteEmergencyContact,
} from '../services/api'
import PageHeader from '../components/ui/PageHeader'
import PageLoading from '../components/ui/PageLoading'
import EmptyState from '../components/ui/EmptyState'
import Modal from '../components/ui/Modal'

const EMPTY_FORM = { name: '', relationship: '', phone: '', label: 'Emergency' }

const EmergencyContacts = () => {
  const [contacts, setContacts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingContact, setEditingContact] = useState(null)
  const [formData, setFormData] = useState(EMPTY_FORM)

  const loadContacts = () => {
    getEmergencyContacts()
      .then(setContacts)
      .catch((err) => console.error('Error loading contacts:', err))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadContacts()
  }, [])

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingContact) {
        await updateEmergencyContact(editingContact.id, formData)
      } else {
        await createEmergencyContact(formData)
      }
      handleCancel()
      loadContacts()
    } catch (err) {
      console.error('Error saving contact:', err)
    }
  }

  const handleEdit = (contact) => {
    setEditingContact(contact)
    setFormData({
      name: contact.name,
      relationship: contact.relationship,
      phone: contact.phone,
      label: contact.label || 'Emergency',
    })
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      try {
        await deleteEmergencyContact(id)
        loadContacts()
      } catch (err) {
        console.error('Error deleting contact:', err)
      }
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingContact(null)
    setFormData(EMPTY_FORM)
  }

  const openAdd = () => setShowForm(true)

  if (loading) {
    return <PageLoading message="Loading emergency contacts..." />
  }

  return (
    <>
      <PageHeader
        eyebrow="Safety & contacts"
        icon={ShieldAlert}
        title="Emergency contacts"
        subtitle="People the clinic can reach on your behalf during urgent situations."
        action={
          <button type="button" className="btn btn-success" onClick={openAdd}>
            <Plus size={18} aria-hidden="true" />
            Add Contact
          </button>
        }
      />

      {contacts.length === 0 ? (
        <EmptyState
          icon={ShieldAlert}
          title="No emergency contacts"
          description="Add someone we can reach if you need urgent help."
          action={
            <button type="button" className="btn btn-primary" onClick={openAdd}>
              <Plus size={18} aria-hidden="true" />
              Add Your First Contact
            </button>
          }
        />
      ) : (
        <div className="list-stack">
          {contacts.map((contact) => (
            <article key={contact.id} className="list-card">
              <div className="list-card__header">
                <div>
                  <h3 className="list-card__title">{contact.name}</h3>
                  <p className="list-card__meta">
                    <User size={14} aria-hidden="true" />
                    {contact.relationship}
                  </p>
                </div>
                <span className="contact-card__badge">{contact.label}</span>
              </div>
              <div className="list-card__body">
                <p className="list-card__meta">
                  <Phone size={14} aria-hidden="true" />
                  {contact.phone}
                </p>
              </div>
              <div className="list-card__actions">
                <button type="button" className="btn btn-warning btn-sm" onClick={() => handleEdit(contact)}>
                  <Pencil size={15} aria-hidden="true" />
                  Edit
                </button>
                <button type="button" className="btn btn-danger btn-sm" onClick={() => handleDelete(contact.id)}>
                  <Trash2 size={15} aria-hidden="true" />
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {showForm && (
        <Modal
          title={editingContact ? 'Edit Contact' : 'Add Emergency Contact'}
          onClose={handleCancel}
          footer={
            <>
              <button type="button" className="btn btn-ghost" onClick={handleCancel}>
                Cancel
              </button>
              <button type="submit" form="contact-form" className="btn btn-primary">
                {editingContact ? 'Update' : 'Save'} Contact
              </button>
            </>
          }
        >
          <form id="contact-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                id="name"
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="relationship">Relationship *</label>
              <input
                id="relationship"
                type="text"
                name="relationship"
                value={formData.relationship}
                onChange={handleInputChange}
                required
                placeholder="e.g., Father, Mother, Spouse"
              />
            </div>
            <div className="form-group">
              <label htmlFor="phone">Phone Number *</label>
              <input
                id="phone"
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                required
                placeholder="e.g., 071 234 5678"
              />
            </div>
            <div className="form-group">
              <label htmlFor="label">Label</label>
              <select id="label" name="label" value={formData.label} onChange={handleInputChange}>
                <option value="Emergency">Emergency</option>
                <option value="Home">Home</option>
                <option value="Work">Work</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </form>
        </Modal>
      )}
    </>
  )
}

export default EmergencyContacts
