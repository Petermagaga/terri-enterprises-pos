import { useState } from 'react'
import { isAxiosError } from 'axios'
import { X } from 'lucide-react'

import {
  useCreateSupplier,
  useUpdateSupplier,
} from '../hooks/useSuppliers'

import type {
  Supplier,
  CreateSupplierPayload,
} from '../supplier.types'

interface SupplierFormProps {
  onClose: () => void
  supplier?: Supplier
}

const initialForm: CreateSupplierPayload = {
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: '',
  notes: '',
  is_active: true,
}

export default function SupplierForm({
  onClose,
  supplier,
}: SupplierFormProps) {
  const [form, setForm] = useState<CreateSupplierPayload>(() =>
    supplier
      ? {
          name: supplier.name,
          contact_person: supplier.contact_person,
          phone: supplier.phone,
          email: supplier.email,
          address: supplier.address,
          notes: supplier.notes,
          is_active: supplier.is_active,
        }
      : initialForm,
  )

  const [errorMessage, setErrorMessage] = useState('')

  const createSupplier = useCreateSupplier()
  const updateSupplier = useUpdateSupplier()

  const isPending =
    createSupplier.isPending || updateSupplier.isPending

  function updateField(
    field: keyof CreateSupplierPayload,
    value: string,
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')

    const payload: CreateSupplierPayload = {
      ...form,
      name: form.name.trim(),
      contact_person: form.contact_person.trim(),
      phone: form.phone.trim(),
      email: form.email.trim(),
      address: form.address.trim(),
      notes: form.notes.trim(),
    }

    try {
      if (supplier) {
        await updateSupplier.mutateAsync({
          id: supplier.id,
          payload,
        })
      } else {
        await createSupplier.mutateAsync(payload)
      }

      onClose()
    } catch (error) {
      if (isAxiosError(error)) {
        const detail = error.response?.data

        if (typeof detail === 'string') {
          setErrorMessage(detail)
        } else if (detail && typeof detail === 'object') {
          setErrorMessage(
            Object.entries(detail)
              .map(([field, messages]) =>
                `${field}: ${Array.isArray(messages) ? messages.join(', ') : String(messages)}`,
              )
              .join(' | '),
          )
        } else {
          setErrorMessage(
            'Unable to save supplier. Please try again.',
          )
        }
      } else {
        setErrorMessage('An unexpected error occurred.')
      }
    }
  }

  return (
    <div className="product-modal-backdrop">
      <div
        className="product-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="supplier-form-title"
      >
        <div className="product-modal-header">
          <div>
            <span className="page-eyebrow">SUPPLIER MANAGEMENT</span>

            <h2 id="supplier-form-title">
              {supplier ? 'Edit Supplier' : 'Add New Supplier'}
            </h2>

            <p>
              {supplier
                ? 'Update the supplier contact and business details.'
                : "Enter the supplier's contact and business details."}
            </p>
          </div>

          <button
            type="button"
            className="product-modal-close"
            onClick={onClose}
            aria-label="Close form"
            disabled={isPending}
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="product-form-grid">
            <label>
              Supplier Name *
              <input
                required
                maxLength={150}
                value={form.name}
                onChange={(event) =>
                  updateField('name', event.target.value)
                }
                placeholder="e.g. Coca-Cola Distributors"
              />
            </label>

            <label>
              Contact Person
              <input
                maxLength={150}
                value={form.contact_person}
                onChange={(event) =>
                  updateField('contact_person', event.target.value)
                }
                placeholder="e.g. John Kamau"
              />
            </label>

            <label>
              Phone Number *
              <input
                required
                type="tel"
                maxLength={30}
                value={form.phone}
                onChange={(event) =>
                  updateField('phone', event.target.value)
                }
                placeholder="e.g. 0712345678"
              />
            </label>

            <label>
              Email Address
              <input
                type="email"
                value={form.email}
                onChange={(event) =>
                  updateField('email', event.target.value)
                }
                placeholder="e.g. supplier@example.com"
              />
            </label>

            <label className="product-form-full-width">
              Address
              <textarea
                rows={2}
                value={form.address}
                onChange={(event) =>
                  updateField('address', event.target.value)
                }
                placeholder="Supplier business address"
              />
            </label>

            <label className="product-form-full-width">
              Notes
              <textarea
                rows={3}
                value={form.notes}
                onChange={(event) =>
                  updateField('notes', event.target.value)
                }
                placeholder="Additional supplier information"
              />
            </label>
          </div>

          {errorMessage && (
            <div className="product-form-error">
              {errorMessage}
            </div>
          )}

          <div className="product-form-actions">
            <button
              type="button"
              className="product-cancel-button"
              onClick={onClose}
              disabled={isPending}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={isPending}
            >
              {isPending
                ? 'Saving...'
                : supplier
                  ? 'Update Supplier'
                  : 'Save Supplier'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}